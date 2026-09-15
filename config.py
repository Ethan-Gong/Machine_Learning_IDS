import os


HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
PORT = os.getenv('MYSQL_PORT', '3306')
DATABASE = os.getenv('MYSQL_DATABASE', 'project')
USER = os.getenv('MYSQL_USER', 'root')
PASSWORD = os.getenv('MYSQL_PASSWORD', '')
DB_URI = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://{}:{}@{}:{}/{}'.format(USER, PASSWORD, HOST, PORT, DATABASE)
)
SQLALCHEMY_DATABASE_URI = DB_URI


SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-change-me')
DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'


PREDICTED_COLUMNS = ['Src IP', 'Src Port', 'Dst IP', 'Dst Port', 'Protocol', 'Timestamp']
NEW_PREDICTED_COLUMNS = ['Src_IP', 'Src_Port', 'Dst_IP', 'Dst_Port', 'Protocol', 'Timestamp', 'prediction']
