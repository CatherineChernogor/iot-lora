from flask import Flask
from flask_restful import Resource, Api
import sqlite3
from datetime import datetime

app = Flask(__name__)
api = Api(app)
cursor = None
connection = None


class Data(Resource):
    def get(self, device_code):
        return select("*", "measures", f"device_code={device_code}", 10)

    def post(self, device_code, value):
        timestamp = datetime.now()
        return insert([(device_code, value, timestamp)], "measures")


class Register(Resource):
    def get(self, device_code):
        pass

    def post(self, device_code):
        pass


def create_tables(conn, cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS device(
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       type TEXT,
       period INTEGER,
       code TEXT);
    """)
    conn.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS qr(
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       image BLOB,
       device_code TEXT);
    """)
    conn.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS coord(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          qr_id INTEGER,
          lat INTEGER,
          long INTEGER);
       """)
    conn.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS measures(
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           device_code TEXT,
           value INTEGER,
           datetime TIMESTAMP);
        """)
    conn.commit()


def init_db():
    global connection
    global cursor
    connection = sqlite3.connect('iot.db')
    cursor = connection.cursor()

    create_tables(connection, cursor)


def select(fields, table, condition, limit):
    global connection
    global cursor
    
    string = f"select {fields} from {table}"
    if condition != "":
        string += f" where {condition}"

    if limit != "":
        string += f" limit {limit};"
    else:
        limit += ";"
    cursor.execute(string)
    return cursor.fetchall()


def insert(fields, table):
    global connection
    global cursor

    questions = "?"
    for i in range(len(fields[0]) - 1):
        questions += ", ?"

    string = f'insert into {table} values ({questions})', fields

    if len(fields) > 1:
        cursor.executemany(string, fields)
    else:
        cursor.executeone(string, fields)
    connection.commit()


api.add_resource(Data, '/data/<string:device_code>')
api.add_resource(Register, '/register/<string:device_code>')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
