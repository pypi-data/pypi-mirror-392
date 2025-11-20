# src/veriskgo/config.py
import os
from dotenv import load_dotenv

load_dotenv()

def get_cfg():
    return {
        "aws_profile": os.getenv("AWS_PROFILE"),
        "aws_region": os.getenv("AWS_REGION", "us-east-1"),
        "sqs_url": os.getenv("AWS_SQS_OTEL"),
        "env": os.getenv("ENV", "dev"),
        "project": os.getenv("PROJECT", "genai-app"),
    }
