import requests
from redislite import Redis
from helper import PeekFromSQS, DeleteFromSQS
import json

redis_db = Redis('response_db.rld')

while True:
    message = PeekFromSQS('1229960136-resp-queue', 1)
    if message is not None:
        messageBody = json.loads(message['Body'])
        msgId = messageBody['messageId']
        result = messageBody['result']
        redis_db.set(msgId, result)
        DeleteFromSQS('1229960136-resp-queue', message)