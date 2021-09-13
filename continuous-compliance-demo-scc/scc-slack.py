import base64
import json
import requests

TOKEN = "xoxb-1402606383398-2460246669030-nXhBd7RqJJEGlJcn5Be6HfAz"

def send_slack_chat_notification(event, context):
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    message_json = json.loads(pubsub_message)
    finding = message_json['finding']

    requests.post("https://slack.com/api/chat.postMessage", data={
        "token": TOKEN,
        "channel": "#test-notification",
        "text": f"A high severity finding {finding['category']} was detected and auto-remedied, please investigate!"
    })

"""
Copy and paste these modules for the requirements.txt

requests

"""
