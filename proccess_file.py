import os
import subprocess
import threading
import time
from queue import Queue
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import config
columns = ['Flow ID', 'Src IP', 'Src Port', 'Dst IP', 'Protocol', 'Timestamp', 'Label']
other_columns = ['Src IP', 'Src Port', 'Dst IP', 'Dst Port', 'Protocol', 'Timestamp',]
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
CICFLOWMETER_COMMAND = os.getenv(
    'CICFLOWMETER_COMMAND',
    fr'{script_dir}\CICFlowMeter-4.0\bin\cfm.bat'
)


class MyHandler(FileSystemEventHandler):
    def __init__(self, butter, file_queue):
        self.butter = butter
        self.file_queue = file_queue

    def on_created(self, event):
        if not event.is_directory:
            self.butter.append(event.src_path)
            self.file_queue.put(self.butter)


def process_file(file_queue, model):

    while True:
        file_path = file_queue.get()
        if file_path is None:
            break  # None 作为停止信号
        print(f"Processing {file_path}")
        if len(file_path) >= 2:
            file = file_path[0]
            os.makedirs(fr"{script_dir}\CSV", exist_ok=True)
            command = [CICFLOWMETER_COMMAND, file, fr"{script_dir}\CSV"]
            result = subprocess.run(command, capture_output=True)
            if result.returncode == 0:
                csv_file = file.replace(".pcap", ".pcap_Flow.csv")
                csv_file = csv_file.replace("\\DATA\\", "\\CSV\\")
                df = pd.read_csv(f'{csv_file}', encoding='GBK')
                row_count = df.shape[0]
                if row_count >= 10:
                    feature = df[other_columns]
                    df.drop(columns, axis=1, inplace=True)
                    all_col = df.columns
                    df = encode_numeric_zscore(df, all_col)
                    df = encode_numeric_range(df, all_col)
                    invalid_mask = np.isnan(df) | np.isinf(df)
                    valid_rows = ~np.any(invalid_mask, axis=1)
                    feature = feature[valid_rows]
                    df = df[valid_rows]
                    prediction = model.predict(df)
                    predicted_classes = (prediction > 0.5).astype(int)
                    feature['prediction'] = predicted_classes
                    feature.columns = config.NEW_PREDICTED_COLUMNS
                    feature.to_sql('predicted_data', con=engine, index=False, if_exists='append', chunksize=500)
                    df = pd.DataFrame()
                    feature = None
                else:
                    df = pd.DataFrame()
            del (file_path[0])
            print(f"Finished processing {file_path}")
            file_queue.task_done()


def start_monitoring(path, butter, file_queue):
    event_handler = MyHandler(butter, file_queue)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    print("Monitoring started.")
    try:
        while True:
            # 这里可以添加sleep以减少CPU使用
            time.sleep(1)  # 使用 sleep 来减少 CPU 占用
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
        file_queue.put(None)  # 发送一个信号来表示监控结束
        print("Monitoring stopped.")


def encode_numeric_zscore(df, names, mean=None, sd=None):
    for name in names:
        if mean is None:
            mean = df[name].mean()

        if sd is None:
            sd = df[name].std()

        df[name] = (df[name] - mean) / sd
    return df


def encode_numeric_range(df, names, normalized_low=0, normalized_high=1, data_low=None, data_high=None):
    for name in names:
        if data_low is None:
            data_low = min(df[name])
            data_high = max(df[name])

        df[name] = ((df[name] - data_low) / (data_high - data_low)) \
                   * (normalized_high - normalized_low) + normalized_low
    return df


def start_threads(path, model):
    file_queue = Queue()
    butter = []
    monitoring_thread = threading.Thread(target=start_monitoring, args=(path, butter, file_queue))
    processing_thread = threading.Thread(target=process_file, args=(file_queue, model))
    monitoring_thread.start()
    processing_thread.start()
    return monitoring_thread,processing_thread

