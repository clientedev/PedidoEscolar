from datetime import datetime
from app import db
from flask_login import UserMixin
from sqlalchemy import func

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def is_active(self):
        return self.active
    
    # Relationships
    acquisition_requests = db.relationship('AcquisitionRequest', foreign_keys='AcquisitionRequest.created_by_id', backref='creator', lazy='dynamic')
    assigned_requests = db.relationship('AcquisitionRequest', foreign_keys='AcquisitionRequest.responsible_id', backref='responsible', lazy='dynamic')
    status_changes = db.relationship('StatusChange', backref='changed_by_user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

class AcquisitionRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='orcamento')
    observations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    responsible_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    attachments = db.relationship('Attachment', backref='request', lazy='dynamic', cascade='all, delete-orphan')
    status_changes = db.relationship('StatusChange', backref='request', lazy='dynamic', cascade='all, delete-orphan')
    
    # Status choices
    STATUS_CHOICES = [
        ('orcamento', 'Orçamento'),
        ('fase_compra', 'Fase de Compra'),
        ('a_caminho', 'A Caminho'),
        ('finalizado', 'Finalizado')
    ]
    
    def get_status_display(self):
        status_dict = dict(self.STATUS_CHOICES)
        return status_dict.get(self.status, self.status)
    
    def __repr__(self):
        return f'<AcquisitionRequest {self.title}>'

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key
    request_id = db.Column(db.Integer, db.ForeignKey('acquisition_request.id'), nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    uploaded_by = db.relationship('User', backref='uploaded_files')
    
    def __repr__(self):
        return f'<Attachment {self.original_filename}>'

class StatusChange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    old_status = db.Column(db.String(50))
    new_status = db.Column(db.String(50), nullable=False)
    change_date = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.Column(db.Text)
    
    # Foreign keys
    request_id = db.Column(db.Integer, db.ForeignKey('acquisition_request.id'), nullable=False)
    changed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def get_old_status_display(self):
        status_dict = dict(AcquisitionRequest.STATUS_CHOICES)
        return status_dict.get(self.old_status, self.old_status) if self.old_status else 'Criado'
    
    def get_new_status_display(self):
        status_dict = dict(AcquisitionRequest.STATUS_CHOICES)
        return status_dict.get(self.new_status, self.new_status)
    
    def __repr__(self):
        return f'<StatusChange {self.old_status} -> {self.new_status}>'
