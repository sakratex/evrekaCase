import requests
import random
import json
import datetime
import time


#1000 Adet rastgele konum oluşturulur ve bu konumlar locations api ye gönderilir.

for i in range(1000):
    location = {
        "device_id": random.randint(1, 10),
        "latitude": random.uniform(36, 42),
        "longitude": random.uniform(27, 45),
        "timestamp": datetime.datetime.now().isoformat()
    }
    response = requests.post("http://localhost:8000/rabbitmq/location", json=location)
    print(response.json())
    time.sleep(0.1)

