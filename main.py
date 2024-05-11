import pika
from fastapi import FastAPI, HTTPException,Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import psycopg2
import json
from typing import List
import datetime


app = FastAPI()

# PostgreSQL veritabanı bağlantısı ve Model
def get_db_connection():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5430"
    )
    return conn

# Veritabanı modeli
class Device(BaseModel):
    id: int
    name: str

class Location(BaseModel):
    device_id: int
    latitude: float
    longitude: float
    timestamp: str


# PostgreSQL veritabanı bağlantısı ve Model Sonu


# RabbitMQ bağlantısı
def connect_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    return connection

# Kuyruğa veri gönderme fonksiyonu
def publish_to_queue(queue, message):
    connection = connect_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=message
    )
    connection.close()

# Kuyruğu tüketen fonksiyon
def consume_queue(queue):
    connection = connect_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue=queue)

    def callback(ch, method, properties, body):
        data = json.loads(body)
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            if queue == "location_queue":
                cursor.execute(
                    "INSERT INTO Location (device_id, latitude, longitude, timestamp) VALUES (%s, %s, %s, %s)",
                    (data['device_id'], data['latitude'], data['longitude'], data['timestamp'])
                )
            elif queue == "device_queue":
                cursor.execute(
                    "INSERT INTO Device (id, name) VALUES (%s, %s)",
                    (data['id'], data['name'])
                )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(e)
        finally:
            cursor.close()
            conn.close()

    channel.basic_consume(queue, callback, auto_ack=True)
    channel.start_consuming()


@app.get("/")
async def redirect_to_docs(request: Request):
    return RedirectResponse(url="/docs")

# Cihaz oluşturma endpoint
@app.post("/devices/")
def create_device(device: Device):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Device (id, name) VALUES (%s, %s)", (device.id, device.name))
        conn.commit()
        return {"message": "Device created successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Error creating device")
    finally:
        cursor.close()
        conn.close()

# Cihaz silme endpoint
@app.delete("/devices/{device_id}/")
def delete_device(device_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Device WHERE id = %s", (device_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Device not found")
        return {"message": "Device deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Error deleting device")
    finally:
        cursor.close()
        conn.close()

# Cihaz listeleme endpoint
@app.get("/devices/")
def list_devices():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name FROM Device")
        devices = cursor.fetchall()
        return devices
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error fetching devices")
    finally:
        cursor.close()
        conn.close()

# Konum ekleme endpoint
@app.post("/locations/")
def create_location(location: Location):
    # Konumu kuyruğa gönder
    location_data = {
        "device_id": location.device_id,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "timestamp": location.timestamp
    }

    #Kuyruğa ekleme
    publish_to_queue("location_queue", json.dumps(location_data))
    return {"message": "Location sent to queue"}


# Cihaza göre konum geçmişini listeleme endpoint
@app.get("/locations/{device_id}/")
def list_locations_by_device(device_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Location WHERE device_id = %s", (device_id,))
        locations = cursor.fetchall()
        if not locations:
            raise HTTPException(status_code=404, detail="No locations found for this device")
        return locations
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error fetching locations")
    finally:
        cursor.close()
        conn.close()

# Tüm cihazlar için son konum endpoint

# Tüm cihazların son konumlarını getiren fonksiyon
def get_last_locations():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT DISTINCT ON (device_id) device_id, latitude, longitude, timestamp
            FROM Location
            ORDER BY device_id, timestamp DESC
        """)
        locations = cursor.fetchall()
        return locations
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error fetching last locations")
    finally:
        cursor.close()
        conn.close()

@app.get("/devices/last-locations/")
def list_last_locations():
    locations = get_last_locations()
    return locations




@app.post("/rabbitmq/location")
def send_to_queue(location: Location):
    queue_name = "location_queue"
    message = {
        "device_id": location.device_id,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "timestamp": location.timestamp
    }
    publish_to_queue(queue_name, json.dumps(message))
    return {"message": "Location sent to queue"}

@app.post("/rabbitmq/device")
def send_to_queue(device: Device):
    queue_name = "device_queue"
    message = {
        "id": device.id,
        "name": device.name
    }
    publish_to_queue(queue_name, json.dumps(message))
    return {"message": "Device sent to queue"}




# Kuyruk Threadleri
import threading
queue_thread = threading.Thread(target=consume_queue, args=("location_queue",))
queue_thread.start()

queue_thread = threading.Thread(target=consume_queue, args=("device_queue",))
queue_thread.start()

