import json
import time
import logging
import random
from logging.handlers import TimedRotatingFileHandler

from pykafka import KafkaClient

# ID для того, чтобы убедиться, что разные парсеры пишут разные продукты в кафку
parser_id = random.randint(100000, 999999)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)-20s : %(filename)-10s[LINE:%(lineno)-3d] : %(levelname)-3s : %(message)s",
    handlers=[
        TimedRotatingFileHandler(f"logs/parser-{parser_id}.log", when="midnight")])

logging.info("Trying to connect to kafka")
while True:
    try:
        # Консумер категорий и продюсер продуктов
        client = KafkaClient(hosts="173.18.0.8:9092")
        consumer_topic = client.topics['ozon-category']
        producer_topic = client.topics['ozon-products']
        break

    except Exception as e:
        logging.error(f"Couldn't connect to kafka, sleeping! ({e})")
        time.sleep(5)

logging.info("Connection successful, start listening to new messages")

with producer_topic.get_sync_producer() as producer:

    for msg in consumer_topic.get_balanced_consumer(
            "ozon_parsers",
            managed=True):

        try:
            data = json.loads(msg.value)
            # Забираем сырой json из сообщения
            ozon_raw = data["ozon_resp"]
            # .values())[0] нужно т.к. key после searchResultsV2 постоянно разный
            items = list(json.loads(ozon_raw)["catalog"]["searchResultsV2"].values())[0]['items']

            for item in items:
                product = {
                    "id": item["cellTrackingInfo"]["id"],
                    "price": item["cellTrackingInfo"]["price"],
                    "title": item["cellTrackingInfo"]["title"],
                    "discount": item["cellTrackingInfo"]["discount"],
                    "time": data["time"]
                }

                logging.info(f"Product: {product}")
                producer.produce(json.dumps(product).encode("utf-8"))

        except Exception as e:
            logging.exception(f"Exception while parsing data {e}")
            logging.info(f"Data with error: {msg}")
