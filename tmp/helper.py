
import json
import boto3

session = boto3.Session(
    aws_access_key_id="",
    aws_secret_access_key="",
)

sqs_client = session.client('sqs', region_name='us-east-1')
s3_client = session.client('s3', region_name='us-east-1')


def AddToSQS(queue_name, data):
    queue_url = f'https://sqs.us-east-1.amazonaws.com/637423581378/{queue_name}'

    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(data)
    )


def AddToS3Bucket(bucket_name, key, value):
    value_bytes = value.encode('utf-8')
    s3_client.put_object(Bucket=bucket_name, Key=key, Body=value_bytes)


def PeekFromSQS(queue_name, numOfMessages):
    queue_url = f'https://sqs.us-east-1.amazonaws.com/637423581378/{queue_name}'
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        AttributeNames=['All'],
        MaxNumberOfMessages=numOfMessages,
        WaitTimeSeconds=0
    )
    messages = response.get('Messages', [])
    for new_message in messages:
        return new_message


def DeleteFromSQS(queue_name, message):
    queue_url = f'https://sqs.us-east-1.amazonaws.com/637423581378/{queue_name}'
    response = sqs_client.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=message['ReceiptHandle']
    )
