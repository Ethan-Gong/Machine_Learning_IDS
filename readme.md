# Real-Time Network Intrusion Detection with CNN-LSTM

This repository contains an end-to-end prototype for detecting anomalous network traffic. TShark captures packets in real time, CICFlowMeter converts PCAP files into bidirectional flow features, and a trained parallel CNN-LSTM model classifies each flow as normal or anomalous. Detection results and traffic statistics are stored in MySQL and displayed through a real-time web dashboard.

> The screenshots use a Chinese user interface. English explanations for every screen are provided below.

## Highlights

- Trained a parallel CNN-LSTM model on CICIDS2017 to learn local traffic patterns and temporal dependencies simultaneously.
- Implemented an automated `TShark -> PCAP -> CICFlowMeter -> CSV -> preprocessing -> prediction -> MySQL` pipeline.
- Built the detection service and real-time data stream with Flask, Socket.IO, and SQLAlchemy.
- Developed a Vue, Element UI, and ECharts dashboard for traffic capture, statistical analysis, and inspection of individual predictions.

## Model Results

The following results were obtained from the CICIDS2017 binary-classification experiment:

| Model | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| CNN | 94.6% | 90.4% | 83.3% | 86.5% |
| LSTM | 93.8% | 89.8% | 78.9% | 84.0% |
| Serial CNN-LSTM | 95.1% | 92.2% | 83.5% | 87.6% |
| **Parallel CNN-LSTM** | **98.3%** | **99.0%** | **92.6%** | **95.7%** |

## System Workflow

```text
Select a target IP address and capture-file size
        |
        v
TShark captures packets and writes PCAP files
        |
        v
CICFlowMeter extracts bidirectional flow statistics
        |
        v
Pandas cleans, normalizes, and filters invalid values
        |
        v
The CNN-LSTM model classifies each flow
        |
        v
MySQL persistence + Socket.IO real-time updates
        |
        v
Vue / ECharts dashboard
```

## User Interface Guide

The left navigation menu in all screenshots contains three pages:

- `首页` - Home and packet-capture controls
- `流量分析` - Traffic analytics dashboard
- `流量检测` - Flow-level detection results

### 1. Start and Stop Packet Capture

![Packet capture controls and file download](image/image-20240519121841631.png)

On the Home page:

1. Enter the host to monitor in `IP地址` (**IP Address**).
2. Enter the maximum size of each rotated capture file in `抓包大小(KB)` (**Capture Size in KB**).
3. Select `开始` (**Start**) to launch TShark packet capture.
4. Select `停止` (**Stop**) to end the capture process.
5. Generated PCAP files appear in the table below. Select the required files and use **Download Selected** to download them as a ZIP archive.

### 2. Review Real-Time Traffic Analytics

![Real-time traffic analytics dashboard](image/image-20240519122111100.png)

The Traffic Analytics page contains three live visualizations:

- `热门IP TOP5` (**Top Five Source IPs**) ranks source addresses by the number of recorded flows.
- `预测结果比例` (**Prediction Distribution**) compares the proportions of normal (`0`) and anomalous (`1`) predictions.
- `实时数据请求` (**Real-Time Traffic Activity**) plots the number of detected flow events over time and supports zooming and image export.

### 3. Inspect and Manage Detection Results

![Flow-level intrusion detection results](image/image-20240519122155195.png)

The Flow Detection page displays one row per analyzed network flow:

| Chinese label | English meaning |
| --- | --- |
| `时间` | Timestamp |
| `源地址` / `源端口` | Source IP / Source port |
| `目标地址` / `目标端口` | Destination IP / Destination port |
| `协议` | IP protocol (`6` = TCP, `17` = UDP) |
| `预测` | Model prediction (`0` = normal, `1` = anomalous) |
| `编辑` / `删除` | Edit / delete the selected database record |

Use the pagination controls at the bottom of the table to browse additional results.

## Repository Structure

```text
Machine_Learning_IDS/
├── app.py                 # Flask API, Socket.IO events, and task coordination
├── shark.py               # TShark capture controller
├── proccess_file.py       # File monitoring, feature extraction, and inference
├── models.py              # SQLAlchemy data models
├── config.py              # Environment-variable and database configuration
├── new-cnn-lstm.h5        # Trained parallel CNN-LSTM model
├── migrations/            # Flask-Migrate database migrations
├── WWW/                   # Compiled Vue frontend
└── image/                 # README screenshots
```

Wireshark, CICFlowMeter, generated PCAP/CSV files, and local database credentials are intentionally excluded from the repository.

## Requirements

- Windows 10 or 11
- Python 3.9
- MySQL 8.x
- Wireshark / TShark
- [CICFlowMeter 4.0](https://github.com/ahlashkari/CICFlowMeter)

## Local Setup

1. Clone the repository and enter the project directory:

   ```powershell
   git clone https://github.com/Ethan-Gong/Machine_Learning_IDS.git
   cd Machine_Learning_IDS
   ```

2. Create a Python 3.9 environment and install the dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Install Wireshark and install or build CICFlowMeter 4.0.

4. Use `.env.example` as a reference and set the MySQL connection, capture interface, TShark executable, and CICFlowMeter command for your machine. Local passwords and machine-specific paths should never be committed.

5. Create the configured MySQL database and apply its migrations:

   ```powershell
   flask --app app db upgrade
   ```

6. Start the Socket.IO-enabled backend:

   ```powershell
   python app.py
   ```

7. Serve the compiled frontend from `WWW/` with a static HTTP server, then open it in a browser. The current frontend build connects to `http://localhost:5000`.

> Real-time packet capture commonly requires administrator privileges. Use TShark's interface list to determine the correct value for `CAPTURE_INTERFACE`.

## Data and External Tools

- [CICIDS2017](https://www.unb.ca/cic/datasets/ids-2017.html) was used for model training and offline evaluation.
- [CICFlowMeter](https://github.com/ahlashkari/CICFlowMeter) converts PCAP traffic into bidirectional flows and extracts statistical features.

## Scope

This is an educational network-intrusion-detection prototype. The reported metrics come from offline evaluation on CICIDS2017 and should not be interpreted as a production security guarantee.
