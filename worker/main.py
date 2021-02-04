import json
import time
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

from pykafka import KafkaClient
import requests

from flask import Flask, request, abort, Response

OZON_API_LINK = "https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fcategory%2F{}%2F%3Flayout_container%3Ddefault%26layout_page_index%3D{}%26page%3D{}"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)-20s : %(filename)-10s[LINE:%(lineno)-3d] : %(levelname)-3s : %(message)s",
    handlers=[
        TimedRotatingFileHandler("logs/worker.log", when="midnight")])

logging.info("Trying to connect to kafka")

while True:
    try:
        client = KafkaClient(hosts="173.18.0.8:9092")
        producer_topic = client.topics['ozon-category']
        break

    except Exception as e:
        logging.error(f"Couldn't connect to kafka, sleeping! ({e})")
        time.sleep(5)

logging.info("Connection successful, starting webserver")

app = Flask(__name__)


@app.route("/", methods=["POST"])
def main():
    try:
        with producer_topic.get_sync_producer() as producer:
            if not request.json or "link" not in request.json:
                abort(400)

            link = request.json["link"]
            logging.info(f"Got a request to check {link}")
            spltd_link = link.split("/")
            # Наличие или отсутствие / в конце ссылки
            category = spltd_link[-1] if spltd_link[-1] else spltd_link[-2]
            logging.info(f"Found a category {category} in link")

            # 5 страниц
            for i in range(1, 6):
                try:
                    ozon_resp = requests.get(OZON_API_LINK.format(category, i, i)).text
                    data = {"ozon_resp": ozon_resp, "time": str(datetime.datetime.now().time())}
                    # category_producer.send("ozon-category", data)
                    producer.produce(json.dumps(data).encode("utf-8"))
                    logging.info(f"Sent unparsed page {i} to kafka")

                    # (иногда случаются \\"error\\":\\"internal Server Error\\",\\"traceID\\":\\"130758d9573a4b97\\"),
                    # но не думаю, что это из-за маленького "сна"
                    time.sleep(0.5)

                except Exception as e:
                    logging.exception(f"Exception while getting ozon page or sending data to kafka {e}")

            logging.info("Have sent all info to kafka")
            return Response(status=200)

    except Exception as e:
        logging.exception(f"Exception while parsing link {e}")
        abort(500)


app.run(host="0.0.0.0", port=80)
