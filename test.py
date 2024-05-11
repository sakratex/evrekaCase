from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Cihaz oluşturma testi
def test_create_device():
    # Test için geçerli cihaz verisi oluştur
    device_data = {"id": 11, "name": "Auto Test Device"}

    # Endpoint'e istek gönder
    response = client.post("/devices/", json=device_data)

    # Başarılı bir yanıt almalıyız
    assert response.status_code == 200
    assert response.json() == {"message": "Device created successfully"}
    print("Cihaz oluşturma testi başarılı!")

# Cihaz listeleme testi
def test_list_devices():
    # Endpoint'e istek gönder
    response = client.get("/devices/")

    # Başarılı bir yanıt almalıyız
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    print("Cihaz listeleme testi başarılı!")

# Son konumları listeleme testi
def test_list_last_locations():
    # Endpoint'e istek gönder
    response = client.get("/locations/last/")

    # Başarılı bir yanıt almalıyız
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    print("Son konumları listeleme testi başarılı!")

# Testleri çalıştır
test_create_device()
test_list_devices()
test_list_last_locations()


"""Curl Test device

curl -X POST "http://localhost:8000/rabbitmq/device" \
     -H "Content-Type: application/json" \
     -d '{
          "id": 10,
          "name": "Device 10"
         }'


"""


""" Curl Test location
curl -X POST "http://localhost:8000/rabbitmq/location" \
     -H "Content-Type: application/json" \
     -d '{
          "device_id": 1,
          "latitude": 39.9334,
          "longitude": 32.8597,
          "timestamp": "2024-05-10T12:00:00Z"
         }'


"""