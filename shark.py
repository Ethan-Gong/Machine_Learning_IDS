import os
import subprocess
script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)


class WiresharkController:
    def __init__(self, capture_directory, interface='WLAN', host='127.0.0.1', output_format='pcap'):
        self.capture_directory = capture_directory
        self.interface = interface
        self.host = host
        self.output_format = output_format
        self.filesize = 500
        self.tshark_process = None

    def set_host(self, new_host):
        """
        Update the target host for packet capturing.

        :param new_host: The new host IP address or hostname.
        """
        self.host = new_host

    def set_filesize(self, new_filesize):
        """
        Update the maximum file size for capture files.

        :param new_filesize: The new file size in kilobytes.
        """
        self.filesize = new_filesize

    def start_capture(self):
        if self.tshark_process is None or self.tshark_process.poll() is not None:
            os.makedirs(self.capture_directory, exist_ok=True)
            tshark_command = os.getenv('TSHARK_PATH', 'tshark')
            command = [
                tshark_command, '-i', self.interface,
                '-n', '-f', f'host {self.host}',
                '-B', '4', '-b', f'filesize:{self.filesize}',
                '-w', os.path.join(self.capture_directory, 'temp.pcap'),
                '-F', self.output_format
            ]
            self.tshark_process = subprocess.Popen(command)
            return {"status": "Capture started"}
        else:
            return {"status": "Capture is already running"}

    def stop_capture(self):
        if self.tshark_process is not None:
            self.tshark_process.terminate()
            self.tshark_process = None
            return {"status": "Capture stopped"}
        else:
            return {"status": "No capture is running"}
