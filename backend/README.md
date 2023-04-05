# Backend Software

Backend source code for the embedded computing project 'IoT FullStack'. It
serves as an interface between the frontend, the database and the AS-Pairs.

## Install dependencies
Installing Python libraries with
```
pip install -r requirements.txt
```

Settings can be influenced by the .env file. Starting the application with
``
python application.py
``

Additional MQTT broker is required. The broker is installed on the external system via the command
``
sudo apt install mosquitto
``
