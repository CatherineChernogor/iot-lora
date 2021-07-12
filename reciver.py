import base64
import socket
import time
import requests
import json

gateway_adress = "192.168.1.1"
gateway_port = 8002

flask_adress = "127.0.0.1"
flask_port = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((gateway_adress, gateway_port))


def send_post(device_code, value, rssi):
    data = {"device": {
        "value": value,
        "rssi": rssi
    }}
    r = requests.post(f"http://{flask_adress}:{flask_port}/data/{device_code}", data=data)
    print(r.status_code, r.reason)


def get_device_code_by_freq(freq):
    r = requests.get(f"http://{flask_adress}:{flask_port}/devices")
    data = r.content.decode()
    data = json.loads(data)

    for line in data["devices"]:
        f = line[4]
        if float(f) == float(freq):
            return line[3]

    print(r.status_code, r.reason)
    return "nothing found"


if __name__ == '__main__':
    while True:
        rec, addr = sock.recvfrom(1024)

        rec = rec[12:].decode()
        if "rxpk" in rec:
            data = json.loads(rec)
            data = data['rxpk'][0]

            msg = data["data"]
            freq = data["freq"]
            rssi = data["rssi"]

            value = base64.b64decode(msg)
            device_code = get_device_code_by_freq(freq)

            send_post(device_code, value, rssi)
            print(f"send post {device_code} {value} {rssi}")
        time.sleep(0.5)
