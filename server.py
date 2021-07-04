from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import sqlite3
from datetime import datetime

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('value')
parser.add_argument('amount')


class Data(Resource):
    def get(self, device_code):
        args = parser.parse_args()
        amount = args['amount']

        if amount == None:
            return select("*", "measures", f"device_code=\"{device_code}\"", 10), 200
        else:
            return select("*", "measures", f"device_code=\"{device_code}\"", amount), 200

    def post(self, device_code):
        timestamp = datetime.now()
        args = parser.parse_args()
        value = args['value']

        insert([device_code, value, timestamp], "measures")

        return "ok", 200


api.add_resource(Data, '/data/<string:device_code>')


@app.route('/register/<string:device_code>', methods=['POST'])
def register_coords(device_code):
    try:
        device = request.json['device']
        lat = device["lat"]
        long = device["long"]

        qr_id = select("id", "qr", f'device_code=\"{device_code}\"', "1")[0]
        insert([qr_id[0], lat, long], 'coord')

        return "ok", 200

    except Exception:
        return "invalid", 500


@app.route('/register/', methods=['POST'])
def register_new_device():
    try:
        device = request.json["device"]
        code = device["code"]
        qr = device["qr"]
        type = device["type"]
        period = device["period"]

        insert([type, period, code], "device")
        insert([qr, code], "qr")

        return "ok", 200

    except Exception:
        return "invalid", 500


def create_tables(conn, cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS device(
       id INTEGER PRIMARY KEY AUTOINCREMENT not null,
       type TEXT,
       period INTEGER,
       code TEXT);
    """)
    conn.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS qr(
       id INTEGER PRIMARY KEY AUTOINCREMENT  not null,
       image BLOB,
       device_code TEXT);
    """)
    conn.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS coord(
          id INTEGER PRIMARY KEY AUTOINCREMENT  not null,
          qr_id INTEGER,
          lat INTEGER,
          long INTEGER);
       """)
    conn.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS measures(
           id INTEGER PRIMARY KEY AUTOINCREMENT  not null,
           device_code TEXT,
           value INTEGER,
           datetime TIMESTAMP);
        """)
    conn.commit()


def make_connection():
    connection = sqlite3.connect('iot.db')
    cursor = connection.cursor()

    create_tables(connection, cursor)

    return connection, cursor


def select(fields, table, condition, limit):
    _, cursor = make_connection()

    string = f"select {fields} from {table}"
    if condition != "":
        string += f" where {condition}"

    if limit != "":
        string += f" limit {limit};"
    else:
        limit += ";"
    print(string)
    cursor.execute(string)
    return cursor.fetchall()


def insert(fields, table):
    connection, cursor = make_connection()

    questions = "?"
    for i in range(len(fields) - 1):
        questions += ", ?"

    string = f'insert into {table} values (NULL, {questions})'

    print(string, fields)
    cursor.execute(string, fields)
    connection.commit()


if __name__ == '__main__':
    app.run(debug=True)
