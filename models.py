from datetime import datetime
from exts import db


class User(db.Model):
    __tablename__ = 'user'
    email = db.Column(db.String(120), unique=True, nullable=False)
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    joined = db.Column(db.DateTime, default=datetime.utcnow)
    pass


class Prediction(db.Model):
    __tablename__ = 'predicted_data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Src_IP = db.Column(db.Text, nullable=True)
    Src_Port = db.Column(db.BigInteger, nullable=True)
    Dst_IP = db.Column(db.Text, nullable=True)
    Dst_Port = db.Column(db.BigInteger, nullable=True)
    Protocol = db.Column(db.BigInteger, nullable=True)
    Timestamp = db.Column(db.Text, nullable=True)
    prediction = db.Column(db.BigInteger, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'dstIp': self.Dst_IP,
            'dstPort': self.Dst_Port,
            'srcIp': self.Src_IP,
            'srcPort': self.Src_Port,
            'protocol': self.Protocol,
            'timestamp': self.Timestamp,
            'prediction': self.prediction
        }
    pass




