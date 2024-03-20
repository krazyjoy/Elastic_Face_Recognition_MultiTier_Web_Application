import asyncio
import base64
import os
import json

import boto3
import threading

from sqs_util import *
from model.face_recognition import face_match
import time

tmp_folder = "./tmp/"
s3_client = boto3.client('s3', aws_access_key_id = get_access_key(), aws_secret_access_key= get_secret_key(), region_name='us-east-1')

input_bucket_name = '1229960136-in-bucket'
output_bucket_name = '1229960136-out-bucket'

"""
    This function deletes file from disk of app instance.
"""
def remove_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

"""
    This function saves file to the disk of app instance.
"""
def save_file(file_path, file_content):
    with open(file_path, 'wb') as image_file:
        image_file.write(file_content)

def process_messages():
    image_folder = './dataset/face_images_1000/'
    ckpt = './model/data.pt'

    while True:
        time.sleep(1)
        response = receive_message(get_request_queue_url())

        for message in response.get("Messages", []):


            message_body = message["Body"]

            filename = message_body.split(':')[0]
            file_contents = message_body.split(':')[1]



            image_file_path = image_folder + filename
            result = face_match(image_file_path, ckpt)

            # output = {filename:result[0]}

            # send_message(get_response_queue_url(), json.dumps(output))
            output = f'{filename}:{result[0]}'.strip('"')
            send_message(get_response_queue_url(), output)
            print(f"sent response: {output} to response queue")

        # tmp_file_path = tmp_folder + filename
        # save_file(tmp_file_path, base64.b64decode(bytes(file_contents, encoding='utf-8')))

            try:
                print(f'upload file: {filename} to in-bucket')
                # Upload file to S3 bucket
                with open(image_file_path, 'rb') as f:
                    s3_client.put_object(
                        Bucket=input_bucket_name,
                        Key=filename,
                        Body=f
                    )


                # Clean up temporary file
                # remove_file(tmp_file_path)
                file_name_no_ext = filename.split('.')[0]

                print(f"put image: {filename} to input bucket")
                s3_client.put_object(
                    Bucket=output_bucket_name,
                    Key=file_name_no_ext,
                    Body=result[0].encode('utf-8')
                )
                print(f"put result: {result[0]} to output bucket")
            except Exception as e:
                # Print the exception message
                print(f"An error occurred: {str(e)}")



            delete_message(get_request_queue_url(), message['ReceiptHandle'])


if __name__ == "__main__":
    process_messages()
