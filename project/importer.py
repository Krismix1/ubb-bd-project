import json
import time

import httpx
from pykafka import KafkaClient

ENDPOINT = "https://data-cloud.flightradar24.com/zones/fcgi/feed.js"
DELAY = 5


def loop(producer):
    response = httpx.get(ENDPOINT, timeout=1, headers={"User-Agent": "curl/7.86.0"})
    response.raise_for_status()

    data = response.text.encode()
    producer.produce(data)
    print("Imported data")


def main():
    client = KafkaClient(hosts="localhost:9092")
    topic = client.topics["flights_raw"]

    last_check = 0
    try:
        with topic.get_producer(delivery_reports=False) as producer:
            while True:
                now = time.time()
                if now - last_check >= DELAY:
                    last_check = now
                    loop(producer)
                else:
                    time.sleep(DELAY * 0.1)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
