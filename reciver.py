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


def send_post(device_code, value):
    r = requests.post(f"http://{flask_adress}:{flask_port}/data/{device_code}", data={'value': value})
    print(r.status_code, r.reason)


if __name__ == '__main__':
    while True:
        rec, addr = sock.recvfrom(1024)

        rec = rec[12:].decode()
        if "rxpk" in rec:
            data = json.loads(rec)
            data = data['rxpk'][0]

            # if data["freq"] == 868.1:
            msg = data["data"]
            datr = data["datr"]
            # where should i get value and device code? cuz device code is generated at android app but datr
            # generated at device
            msg = base64.b64decode(msg)
            send_post(datr, msg)
            print(f"send {datr} {msg}")
        time.sleep(0.5)
