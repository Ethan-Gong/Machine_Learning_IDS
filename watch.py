import threading
import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class MyHandler(FileSystemEventHandler):
    def __init__(self, butter, file_queue):
        self.butter = butter
        self.file_queue = file_queue

    def on_created(self, event):
        if not event.is_directory:
            self.butter.append(event.src_path)
            self.file_queue.put(self.butter)


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


def start_monitoring_thread(path, butter, file_queue):
    # 创建一个线程来运行监控任务
    monitoring_thread = threading.Thread(target=start_monitoring, args=(path, butter, file_queue))
    monitoring_thread.start()
    return monitoring_thread
