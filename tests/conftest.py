import os

# Must be set before src.main is imported because the module reads
# these at import time via os.environ["KEY"].
os.environ.setdefault("SQS_QUEUE_URL", "https://sqs.eu-central-1.amazonaws.com/123456789/test-queue")
os.environ.setdefault("S3_BUCKET_NAME", "test-bucket")
