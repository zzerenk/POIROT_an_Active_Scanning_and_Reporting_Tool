from app import db  
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class ScanRecord(db.Model):
    __tablename__ = 'scan_records'

    id = db.Column(db.Integer, primary_key=True)
    target_ip = db.Column(db.String(50), nullable=False)
    scan_type = db.Column(db.String(20), default='quick')
    
    raw_data = db.Column(JSONB, nullable=True)
    
    status = db.Column(db.String(20), default='pending') # pending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ScanRecord {self.target_ip} - {self.status}>"