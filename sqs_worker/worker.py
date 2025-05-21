import sys
sys.path.append('/app')

import boto3
import time
import os
import json
import tempfile
from PIL import Image

from model.imageUpload import UploadStatus, ImageUpload
from __init__ import app

# AWS clients
sqs = boto3.client('sqs', region_name='us-east-2')
s3 = boto3.client('s3', region_name='us-east-2')

# configuration
bucket_name = os.environ.get("AWS_S3_BUCKET_NAME", "cartage-image-upload")
queue_url = os.environ.get(
    "AWS_SQS_URL",
    "https://sqs.us-east-2.amazonaws.com/542024879144/cartage-image-upload-queue"
)

# medium‐size ceiling + JPEG quality
MAX_WIDTH = 1024
MAX_HEIGHT = 768
JPEG_QUALITY = 85

def resize_image(in_path, out_path, max_w=MAX_WIDTH, max_h=MAX_HEIGHT):
    """
    Resize the image at in_path so it fits within (max_w, max_h),
    preserving aspect ratio, and save to out_path. Supports JPEG & PNG.
    """
    with Image.open(in_path) as img:
        img.thumbnail((max_w, max_h), Image.ANTIALIAS)
        ext = os.path.splitext(out_path)[1].lower()
        if ext in (".jpg", ".jpeg"):
            img.convert("RGB").save(out_path, format="JPEG", quality=JPEG_QUALITY)
        elif ext == ".png":
            img.save(out_path, format="PNG", optimize=True)
        else:
            fmt = img.format or "JPEG"
            img.save(out_path, format=fmt)
    return out_path

def poll_sqs():
    while True:
        resp = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
            VisibilityTimeout=30
        )
        messages = resp.get('Messages', [])
        if not messages:
            print("No messages.")
            time.sleep(5)
            continue

        for msg in messages:
            print("Received:", msg['Body'])
            upload_id = str(json.loads(msg['Body'])["upload_id"])

            with app.app_context():
                entry = ImageUpload.query.get(upload_id)
                if entry is None:
                    print("Database entry not found for upload_id", upload_id)
                    sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=msg['ReceiptHandle']
                    )
                    continue

                try:
                    # 1) mark as processing
                    entry._upload_status = UploadStatus.PROCESSING
                    entry.update()

                    # 2) download original from S3
                    orig_ext = os.path.splitext(entry.s3_key)[1].lower()
                    local_orig = tempfile.NamedTemporaryFile(suffix=orig_ext, delete=False).name
                    s3.download_file(bucket_name, entry.s3_key, local_orig)

                    # 3) prepare resized temp file
                    out_ext = ".jpg" if orig_ext in (".jpg", ".jpeg") else ".png" if orig_ext == ".png" else orig_ext
                    local_resized = tempfile.NamedTemporaryFile(suffix=out_ext, delete=False).name

                    # 4) resize
                    resize_image(local_orig, local_resized)

                    # 5) upload resized back to S3
                    resized_key = f"medium/{os.path.basename(local_resized)}"
                    content_type = "image/jpeg" if out_ext in (".jpg", ".jpeg") else "image/png"
                    s3.upload_file(
                        Filename=local_resized,
                        Bucket=bucket_name,
                        Key=resized_key,
                        ExtraArgs={"ContentType": content_type}
                    )

                    # 6) cleanup
                    os.remove(local_orig)
                    os.remove(local_resized)

                    # 7) delete SQS message
                    sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=msg['ReceiptHandle']
                    )

                    # 8) mark as completed
                    entry._upload_status = UploadStatus.COMPLETED
                    entry.resized_s3_key = resized_key  # if your model tracks this
                    entry.update()
                    print(f"Processed upload_id {upload_id}, resized saved at {resized_key}")

                except Exception as e:
                    print("Error processing message:", e)
                    entry._upload_status = UploadStatus.FAILED
                    entry.update()

        time.sleep(5)

if __name__ == "__main__":
    poll_sqs()
