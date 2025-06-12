from datetime import datetime
from app import db

class MonitoringSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    check_interval = db.Column(db.Integer, default=30)  # seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Website(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to monitoring results
    results = db.relationship('MonitoringResult', backref='website', lazy=True, cascade='all, delete-orphan')
    
    @property
    def latest_result(self):
        return MonitoringResult.query.filter_by(website_id=self.id).order_by(MonitoringResult.checked_at.desc()).first()
    
    @property
    def uptime_percentage(self):
        total_checks = MonitoringResult.query.filter_by(website_id=self.id).count()
        if total_checks == 0:
            return 0
        successful_checks = MonitoringResult.query.filter_by(website_id=self.id, is_up=True).count()
        return round((successful_checks / total_checks) * 100, 2)
    
    def __repr__(self):
        return f'<Website {self.name}: {self.url}>'

class MonitoringResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey('website.id'), nullable=False)
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_up = db.Column(db.Boolean, nullable=False)
    status_code = db.Column(db.Integer)
    response_time = db.Column(db.Float)  # in seconds
    error_message = db.Column(db.Text)
    
    def __repr__(self):
        return f'<MonitoringResult {self.website_id}: {self.is_up} at {self.checked_at}>'
