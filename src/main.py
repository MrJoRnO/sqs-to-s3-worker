import os
import sys
import logging
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

SQS_QUEUE_URL = os.environ["SQS_QUEUE_URL"]
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]


def receive_message(sqs):
    response = sqs.receive_message(
        QueueUrl=SQS_QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=5,
    )
    messages = response.get("Messages", [])
    if not messages:
        log.info("No messages in queue, exiting.")
        sys.exit(0)
    return messages[0]


def save_to_s3(s3, body: str) -> str:
    key = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S") + ".txt"
    s3.put_object(Bucket=S3_BUCKET_NAME, Key=key, Body=body.encode("utf-8"))
    log.info("Saved s3://%s/%s", S3_BUCKET_NAME, key)
    return key


def delete_message(sqs, receipt_handle: str):
    sqs.delete_message(QueueUrl=SQS_QUEUE_URL, ReceiptHandle=receipt_handle)
    log.info("Deleted message from queue.")


def main():
    sqs = boto3.client("sqs")
    s3 = boto3.client("s3")

    message = receive_message(sqs)
    body = message["Body"]
    log.info("Received message: %s", body)

    try:
        save_to_s3(s3, body)
        delete_message(sqs, message["ReceiptHandle"])
    except ClientError as e:
        log.error("AWS error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
