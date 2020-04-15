import json
import os
import sys
import pika
from flask import Flask, jsonify, render_template
import flask_cors
from brew_session import BrewSession, Recipe

brew_session = BrewSession()
on_off = False
app = Flask(__name__, static_url_path='')
flask_cors.CORS(app)
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbit', 5672, '/'))
channel = connection.channel()
channel.exchange_declare(exchange='temps', exchange_type='fanout')
channel.queue_delete(queue='current_temps')
channel.queue_declare(queue='current_temps', arguments={'x-message-ttl': 1000})
channel.queue_bind(queue='current_temps', exchange='temps')
connection.close()


# MySQL:
# app.config['SQLALCHEMY_DATABASE_URI'] = mysql://username:password@server/db
# [DB_TYPE]+[DB_CONNECTOR]://[USERNAME]:[PASSWORD]@[HOST]:[PORT]/[DB_NAME]
# db = SQLAlchemy(app)
# existing db
# class Buildings(db.Model):
#     __table__ = db.Model.metadata.tables['BUILDING']
#
#     def __repr__(self):
#         return self.DISTRICT

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recipes')
def recipes():
    return render_template('recipes.html')


@app.route('/recipe')
def recipe():
    return jsonify([{'id': 1, 'name': 'Coors', 'completed': False}, Recipe().serialize()])


@app.route('/recipelist')
def recipelist():
    return jsonify(["Coors", "Rainier"])


@app.route('/session')
def session():
    return jsonify(brew_session.prompt())


@app.route('/timer')
def timer():
    brew_session.timer()
    return 'Ok'


@app.route('/session', methods=['POST'])
def toggle():
    brew_session.toggle_step()
    return session()


def send_toggle():
    tconnection = pika.BlockingConnection(pika.ConnectionParameters('rabbit', 5672, '/'))
    tchannel = tconnection.channel()
    tchannel.exchange_declare(exchange='temps', exchange_type='fanout')
    tchannel.basic_publish(exchange='temps', routing_key='', body=json.dumps(on_off),
                           properties=pika.BasicProperties(headers={'type': 'command'}))
    tconnection.close()


@app.route('/temp')
def thermo():
    print("Calling thermo")
    ctconnection = pika.BlockingConnection(pika.ConnectionParameters('rabbit', 5672, '/'))
    ctchannel = ctconnection.channel()
    for method_frame, properties, body in ctchannel.consume('current_temps'):
        print(body)
        message_type = properties.headers.get('type')
        if message_type != 'command':
            ctconnection.close()
            # all_temps = read_sensor()
            temp_list = json.loads(body)
            hlt = float(temp_list[0])
            mlt = float(temp_list[1])
            bk = float(temp_list[2])
            temps = {'hlt': hlt, 'mlt': mlt, 'bk': bk}
            print(temps)
            brew_session.set_temp(temps)
            return jsonify(temps)
# {'hlt': hlt, 'mlt': "{0:4.1f}".format(mlt), 'bk': "{0:4.1f}".format(bk)}

if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
