import boto3
import time
import os

sqs = boto3.client('sqs', region_name='us-east-2')  # Replace region
queue_url = os.environ.get("AWS_SQS_URL", "https://sqs.us-east-2.amazonaws.com/542024879144/cartage-image-upload-queue")

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

                

                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
                print("Deleted message.")
        else:
            print("No messages.")

        time.sleep(5)

if __name__ == "__main__":
    poll_sqs()