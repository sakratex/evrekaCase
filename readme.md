Bu proje Eren Köse tarafından, Evreka test case i olarak geliştirilmiştir.
```
Uygulamayı çalıştırmak için:
1. Python 3.8 (Geliştirici sürümü) ve üzeri bir sürüm gerekmektedir.

2. Gerekli kütüphaneleri yüklemek için:
    ```
    pip install -r requirements.txt
    ```
3. Uygulamayı çalıştırmak için aşağıda ki komutu terminal üzerinde run ediniz:
    ```
    uvicorn main:app --reload 
    ```
```
Proje hakkında detaylı bilgi için:

- Postgreqslq veritabanı kullanılmıştır.
- FastAPI framework kullanılmıştır.
- Uygulama içerisinde 8 endpoint bulunmaktadır.
    - /devices
      - Tüm cihazları listeler.
    - /devices/{device_id}
      - Gönderilen ID yi siler.
    - /locations
      - Lokasyon ekler
    - /locations/{location_id}
      - Lokasyonun detaylarını ID özelinde listeler.
    - /devices/last-locations/
      - Son lokasyonları listeler.
    - /rabbitmq/location
        - Gönderilen dataları alır ve kuyruğa ardından db ye ekler.
    - /rabbitmq/device
      - Gönderilen dataları alır ve kuyruğa ardından db ye ekler.


- Uygulama içerisinde 2 tablo bulunmaktadır.
- Uygulama içerisinde 2 model bulunmaktadır.


```
Tablo Yapısı:

- CREATE TABLE Device (
    id SERIAL PRIMARY KEY,  
    name VARCHAR(255) NOT NULL 
);


- CREATE TABLE Location (
    id SERIAL PRIMARY KEY,  
    device_id INT REFERENCES Device(id),  
    latitude FLOAT NOT NULL,  
    longitude FLOAT NOT NULL,  
    timestamp TIMESTAMP NOT NULL  
);

```


