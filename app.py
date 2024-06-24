from flask import Flask, request
import json
import requests as requests_lib

from decouple import config
from openai import OpenAI


OPEN_API_KEY = config("OPEN_API_KEY")  # Replace with your OpenAI API key
LINE_ISSUE = config("LINE_ISSUE")
client = OpenAI(api_key=OPEN_API_KEY)

app = Flask(__name__)

@app.route('/')
def Hello():
    return "Hello World!!", 200

def get_openai_response(user_message):

    payload = client.chat.completions.create(
        model="gpt-3.5-turbo",  # เลือก model ได้จาก https://platform.openai.com/docs/models
        messages=[
            {"role": "system", "content": "You must respond to the user in Thai."},
            {"role": "user", "content": user_message}
        ],
        max_tokens=300,
        temperature=0.7,
        presence_penalty=0,
        frequency_penalty=0
    )

    response = payload.choices[0].message.content.strip()
    return response


@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == "POST":  # user send chat msg to line, line will POST
        req = request.json

        if 'events' in req:
            for event in req['events']:
                if event['type'] == 'message' and event['message']['type'] == 'text':
                    user_message = event['message']['text']
                    reply_token = event['replyToken']

                    response_message = get_openai_response(user_message)
                    ReplyMessage(reply_token, response_message, LINE_ISSUE)
        return 'OK', 200

    elif request.method == "GET":
        return 'GET method', 200


def ReplyMessage(Reply_token, TextMessage, LINE_ISSUE):
    LINE_API = 'https://api.line.me/v2/bot/message/reply'

    Authorization = 'Bearer {}'.format(LINE_ISSUE)
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': Authorization
    }

    data = {
        "replyToken": Reply_token,
        "messages":[{
            "type":"text",
            "text":TextMessage
        }]
    }

    data = json.dumps(data)  # dump dict >> json object
    r = requests_lib.post(LINE_API, headers=headers, data=data)
    return r.status_code


if __name__ == '__main__':
    # app.run(debug=False, port=200)

    txt = get_openai_response("สวัสดี")
    print(txt)