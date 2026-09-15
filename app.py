import os
from zipfile import ZipFile
from flask import Flask, jsonify, request, send_file
from keras.optimizers import Adam
from keras.saving.save import load_model
from models import Prediction
from exts import db
from flask_migrate import Migrate
from flask_socketio import SocketIO
from sqlalchemy import func
import config
import threading
from flask_cors import CORS
from proccess_file import start_threads
from shark import WiresharkController

model = load_model("new-cnn-lstm.h5", compile=False)
model.compile(optimizer=Adam(), loss='binary_crossentropy', metrics=['accuracy'])
app = Flask(__name__)
app.config.from_object(config)
CORS(app)
db.init_app(app)
migrate = Migrate(app, db)
socket = SocketIO(app, cors_allowed_origins='*')
thread_lock = threading.Lock()
thread_started = False
tshark_process = None
script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
DIRECTORY = fr'{script_dir}\DATA'
DIRECTORY = os.getenv('CAPTURE_DIRECTORY', DIRECTORY)
wireshark_controller = WiresharkController(
    capture_directory=DIRECTORY,
    interface=os.getenv('CAPTURE_INTERFACE', 'WLAN')
)


@app.route('/start_capture', methods=['POST'])
def start_capture():
    data = request.json
    print(data)
    host = data.get('ip')
    size = data.get('size')
    wireshark_controller.set_host(host)
    wireshark_controller.set_filesize(size)
    result = wireshark_controller.start_capture()
    return jsonify(result)


@app.route('/stop_capture', methods=['POST'])
def stop_capture():
    result = wireshark_controller.stop_capture()
    return jsonify(result)


@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(DIRECTORY)
    return jsonify(files)


@app.route('/download', methods=['POST'])
def download_files():
    data = request.json
    files = data.get('files', [])
    filename = data.get('filename', 'default_name.zip')  # 接收前端传来的文件名，默认为 'default_name.zip'
    zip_path = '/Temp'  # 临时文件的路径

    with ZipFile(zip_path, 'w') as zipf:
        for file_name in files:
            file_path = os.path.join(DIRECTORY, file_name)
            if os.path.exists(file_path):
                zipf.write(file_path, os.path.basename(file_path))

    return send_file(zip_path, as_attachment=True, download_name=filename)  # 使用接收的文件名


@app.route('/delete/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    entry = Prediction.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Entry deleted'}), 200


@app.route('/update/<int:entry_id>', methods=['PUT'])
def update_entry(entry_id):
    entry = Prediction.query.get_or_404(entry_id)
    data = request.json
    entry.Timestamp = data['timestamp']
    entry.Src_IP = data['srcIp']
    entry.Src_Port = data['srcPort']
    entry.Dst_IP = data['dstIp']
    entry.Dst_Port = data['dstPort']
    entry.Protocol = data['protocol']
    entry.prediction = data['prediction']
    db.session.commit()
    return jsonify(entry.to_dict()), 200


def fetch_predictions():
    with app.app_context():
        while True:
            socket.sleep(1)
            try:
                with db.session() as session:
                    predictions = session.query(Prediction).all()
                all_results = [
                    {
                        'id': prediction.id,
                        'dstIp': prediction.Dst_IP,
                        'dstPort': prediction.Dst_Port,
                        'srcIp': prediction.Src_IP,
                        'srcPort': prediction.Src_Port,
                        'protocol': prediction.Protocol,
                        'timestamp': prediction.Timestamp,
                        'prediction': prediction.prediction
                    } for prediction in predictions
                ]
                emit_data('data_update', all_results)
            except Exception as e:
                app.logger.error(f"Exception in fetch_predictions: {e}")


def fetch_ip_counts():
    with app.app_context():
        while True:
            socket.sleep(1)
            try:
                with db.session() as session:
                    ip_counts = session.query(Prediction.Src_IP, func.count().label('visit_count')).group_by(Prediction.Src_IP).all()
                ip_count_data = [{'srcIp': ip[0], 'visitCount': ip[1]} for ip in ip_counts]
                emit_data('ip_count', ip_count_data)
            except Exception as e:
                app.logger.error(f"Exception in fetch_ip_counts: {e}")


def fetch_time_counts():
    with app.app_context():
        while True:
            socket.sleep(1)
            try:
                with db.session() as session:
                    time_counts = session.query(Prediction.Timestamp, func.count().label('event_count')).group_by(Prediction.Timestamp).all()
                time_count_data = [{'timestamp': time[0], 'timeCount': time[1]} for time in time_counts]
                emit_data('time_count', time_count_data)
            except Exception as e:
                app.logger.error(f"Exception in fetch_time_counts: {e}")


def fetch_prediction_counts():
    with app.app_context():
        while True:
            socket.sleep(1)
            try:
                with db.session() as session:
                    pr_counts = session.query(Prediction.prediction, func.count().label('p_count')).group_by(Prediction.prediction).all()
                pr_count_data = [{'prediction': pr[0], 'pcount': pr[1]} for pr in pr_counts]
                emit_data('pr_count', pr_count_data)
            except Exception as e:
                app.logger.error(f"Exception in fetch_prediction_counts: {e}")


def emit_data(event_name, data):
    socket.emit(event_name, data, namespace='/test')


@socket.on('connect', namespace='/test')
def test_connect():
    global thread_started
    with thread_lock:
        if not thread_started:
            monitoring_thread, processing_thread = start_threads(DIRECTORY, model)
            thread_started = True
            print("Threads started.")
            socket.start_background_task(target=fetch_predictions)
            socket.start_background_task(target=fetch_ip_counts)
            socket.start_background_task(target=fetch_time_counts)
            socket.start_background_task(target=fetch_prediction_counts)
        else:
            print("Threads already started.")


if __name__ == '__main__':
    socket.run(app, host='0.0.0.0', port=5000, debug=app.config['DEBUG'])





