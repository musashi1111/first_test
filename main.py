from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os
import requests
import json
import csv
import math

app = Flask(__name__)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

appid = 'dj00aiZpPWd2MzRMS1F4ZWZPWSZzPWNvbnN1bWVyc2VjcmV0Jng9YTQ-'


def get_coordinates(addr):
    url = f'https://map.yahooapis.jp/geocode/V1/geoCoder?appid={appid}&query={addr}&output=json'
    r = requests.get(url)
    data = json.loads(r.text)
    coordinates = data['Feature'][0]['Geometry']['Coordinates'].split(',')
    lo = coordinates[1]  # 緯度
    la = coordinates[0]  # 経度
    return lo, la


def locate(x, y):
    with open(r'mergeFromCity1.csv', 'r', encoding="utf-8_sig") as f:
        reader = csv.reader(f)
        l = [row for row in reader]
        i = 0
        min = 100000000
        while (i < 103516):
            lo = float(l[i][2])
            la = float(l[i][3])
            dist = math.sqrt((x-lo)**2+(y-la)**2)
            if min > dist:
                min = dist
                ans1 = l[i][0]
                ans2 = l[i][1]
            i = i+1
    return ans1, ans2


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    lo, la = get_coordinates(event.message.text)
    a, b = locate(float(lo), float(la))

    massage = "{}\n「{}」\n{}\n「{}」\n".format(
        "現在地から最短の避難所は",
        a,
        "住所は",
        b
    )

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=massage))


if __name__ == "__main__":
    #    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
