import base64
from flask import Flask, request
from pathlib import Path
from helper import AddToSQS
import uuid
import time
from redislite import Redis

app = Flask(__name__)
redis_db = Redis('response_db.rld')


@app.route('/', methods=['POST'])
def predict():
    request_data = request.files['inputFile']
    image_data = request_data.stream.read()
    image_path = request_data.filename
    image_name = Path(image_path).name
    message_id = str(uuid.uuid4())
    data = {
        "messageId": message_id,
        "filename": image_name,
        "file": base64.b64encode(image_data).decode('utf-8')
    }
    AddToSQS(queue_name='1229960136-req-queue', data=data)
    while redis_db.get(message_id) is None:
        time.sleep(0.5)
        continue
    return redis_db.get(message_id).decode('utf-8')


if __name__ == '__main__':
    app.run()