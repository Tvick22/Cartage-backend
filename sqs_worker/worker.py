import sys
sys.path.append('/app')
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import time
import os
import json
from model.imageUpload import UploadStatus, ImageUpload
from __init__ import app
from PIL import Image

sqs = boto3.client('sqs', region_name='us-east-2')  # Replace region
s3 = boto3.client('s3', region_name='us-east-2')

MAX_WIDTH = 1024
MAX_HEIGHT = 768
JPEG_QUALITY = 85

bucket_name = os.environ.get("AWS_S3_BUCKET_NAME", "cartage-image-upload ")
queue_url = os.environ.get("AWS_SQS_URL", "https://sqs.us-east-2.amazonaws.com/542024879144/cartage-image-upload-queue")

def resize_image(in_path, out_path, max_w=MAX_WIDTH, max_h=MAX_HEIGHT):
    img = Image.open(in_path)
    img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    ext = os.path.splitext(out_path)[1].lower()
    if ext in (".jpg", ".jpeg"):
        img.convert("RGB").save(out_path, format="JPEG", quality=JPEG_QUALITY)
    else:
        img.save(out_path, format="PNG", optimize=True)
    return out_path

def get_extension(filename):
    return os.path.splitext(filename)[1]

def upload_file_to_s3(file_path, file_name, uid, bucket):
    s3_key = f"/uploads/{uid}/{file_name}"

    try:
        s3.upload_file(file_path, bucket, s3_key)
        print(f"Upload successful: {s3_key}")
        return s3_key
    except FileNotFoundError:
        print("Error: The file was not found.")
        return FileNotFoundError
    except NoCredentialsError:
        print("Error: AWS credentials not available.")
        return NoCredentialsError
    except ClientError as e:
        print(f"Unexpected error: {e}")
        return e

def poll_sqs():
    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
            VisibilityTimeout=30
        )

        messages = response.get('Messages', [])
        if messages:
            for message in messages:
                print("Received:", message['Body'])
                upload_id = str(json.loads(message['Body'])["upload_id"])
                with app.app_context():
                    image_db_entry = ImageUpload.query.get(upload_id)
                    if image_db_entry == None:
                        print("Database Entry not found")

                    try:
                        image_db_entry._upload_status = UploadStatus.PROCESSING
                        image_db_entry.update()
                        print("Updated status.")
                        image_filename = upload_id + get_extension(image_db_entry._filename)
                        image_path = "/app/instance/uploads/"+image_filename

                        #CHANGE IMAGE SIZE/RESOLUTION IF APPLICABLE
                        resized_image = resize_image(image_path, image_path)
                        print("Resized Image")
                        #UPLOAD IMAGE TO S3
                        s3_key = upload_file_to_s3(image_path, image_filename, image_db_entry._uid, bucket_name)
                        print("Uploaded to S3")
                        #DELETE LOCAL IMAGE FILE
                        os.remove(image_path)
                        print("Deleted local image")
                        #DELETE SQS MESSAGE
                        sqs.delete_message(
                            QueueUrl=queue_url,
                            ReceiptHandle=message['ReceiptHandle']
                        )
                        print("Deleted message.")
                        #UPDATE ENTRY STATUS
                        image_db_entry._upload_status = UploadStatus.COMPLETED
                        image_db_entry._s3_key = s3_key
                        image_db_entry.update()
                    except Exception as e:
                        print(f"Error processing message: {e}")
                        image_db_entry._upload_status = UploadStatus.FAILED
                        image_db_entry.update()
        else:
            print("No messages.")

        time.sleep(5)

if __name__ == "__main__":
    poll_sqs()