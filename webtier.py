from fastapi import FastAPI, UploadFile,HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
import json, base64;
import threading
import asyncio
from sqs_util import *;
import uvicorn
from scaling_controller_start_stop import auto_scaling_controller

import logging

app = FastAPI()
lock = threading.Lock()
filename_output_map = {};
# queue_listener.delay()

def convert_image_to_string(file):
    file_content = file.file.read();
    converted_string = base64.b64encode(file_content)
    return str(converted_string, 'utf-8').replace('"', "'")


"""
    This function continuously listens to the queue and updates the global data structure upon receiving the messages 
"""
logging.basicConfig(level=logging.INFO)

def queue_listener():
    try:
        while True:
            # logging.info("inside queue listener")
            response = receive_message(get_response_queue_url())
            for message in response.get("Messages", []):
                message_body = message["Body"]

                file_name, output = message_body.split(':', 1)
                file_name = file_name.strip().replace('"', "'")  # Remove leading/trailing whitespace
                output = output.strip().replace('"', "'")  # Remove leading/trailing whitespace

                lock.acquire()
                try:
                    filename_output_map[file_name] = output;
                    print("queue output", output)

                finally:
                    lock.release();

                delete_message(get_response_queue_url(), message['ReceiptHandle']);

    except Exception as e:
        logging.error(f"Error in queue listener: {e}")

"""
    This function continuously checks the global data structure and returns the output if its populated in the data structure 
"""


async def fetch_output(file_name):
    while True:
        # print("fetch output")
        await asyncio.sleep(1);
        with lock:
            if file_name in filename_output_map:
                output = filename_output_map[file_name]
                print(output)
                del filename_output_map[file_name];
                return output;
            else:
                pass;


@app.post("/")
async def recognize_image(inputFile: UploadFile):
    if not inputFile:
        raise HTTPException(status_code=400, detail="No File part")

    if not inputFile.filename:
        raise HTTPException(status_code=400, detail="Empty filename")
    file_name = str(inputFile.filename).replace('"', "'")
    file_content = convert_image_to_string(inputFile);

    message = f'{file_name}:{file_content}'

    # Send message to SQS queue
    send_message(get_request_queue_url(), message);

    print('Sent ' + file_name + ' into the request queue');
    out = await fetch_output(file_name)
    print('Response received:- for ' + file_name + '  :- ' + out)

    out = out.replace('"', "'")
    return PlainTextResponse(f"{file_name}:{out}")


if __name__ == "__main__":
    thread1 = threading.Thread(target=queue_listener)
    thread1.start()
    thread2 = threading.Thread(target=auto_scaling_controller)
    thread2.start()
    uvicorn.run(app=app, host="0.0.0.0", port=8000, lifespan="on")


    # command:  uvicorn webtier:app --host 0.0.0.0 --port 8000


