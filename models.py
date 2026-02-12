from datetime import datetime, date
from app import db
from flask_login import UserMixin
from sqlalchemy import func

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(256))
    needs_password_reset = db.Column(db.Boolean, default=False, nullable=False)
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
    status = db.Column(db.String(50), nullable=False, default='aberto')
    observations = db.Column(db.Text)
    priority = db.Column(db.String(20)) # urgente, necessario, planejado
    impact = db.Column(db.String(50)) # critico, alto, medio, baixo
    estimated_value = db.Column(db.Numeric(10, 2))  # Valor estimado para fase de orçamento
    final_value = db.Column(db.Numeric(10, 2))      # Valor final para fase de compra/entrega
    request_date = db.Column(db.Date, nullable=False, default=date.today)
    delivery_deadline = db.Column(db.Date)  # Prazo de entrega (opcional)
    deadline_alert_sent = db.Column(db.Boolean, default=False, nullable=False)  # Flag para controlar envio de alerta
    classe = db.Column(db.String(50), nullable=False, default='ensino')  # Ensino ou Manutenção
    categoria = db.Column(db.String(100), nullable=False, default='material')  # Serviço ou Material (podem ser múltiplas separadas por vírgula)
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
        ('aberto', 'Aberto'),
        ('em_cotacao', 'Em Cotação'),
        ('aprovado', 'Aprovado'),
        ('pedido_emitido', 'Pedido Emitido'),
        ('recebido', 'Recebido'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado')
    ]
    
    # Priority choices
    PRIORITY_CHOICES = [
        ('urgente', 'Urgente'),
        ('necessario', 'Necessário'),
        ('planejado', 'Planejado')
    ]
    
    # Impact choices
    IMPACT_CHOICES = [
        ('critico', 'Crítico (Paralisa)'),
        ('alto', 'Alto (Atraso)'),
        ('medio', 'Médio'),
        ('baixo', 'Baixo')
    ]
    
    # Classe choices
    CLASSE_CHOICES = [
        ('ensino', 'Ensino'),
        ('manutencao', 'Manutenção'),
        ('administrativo', 'Administrativo')
    ]
    
    # Categoria choices
    CATEGORIA_CHOICES = [
        ('material', 'Material'),
        ('servico', 'Serviço'),
        ('material,servico', 'Material e Serviço')
    ]
    
    def get_status_display(self):
        status_dict = dict(self.STATUS_CHOICES)
        return status_dict.get(self.status, self.status)
    
    def get_priority_display(self):
        priority_dict = dict(self.PRIORITY_CHOICES)
        return priority_dict.get(self.priority, self.priority)

    def get_impact_display(self):
        impact_dict = dict(self.IMPACT_CHOICES)
        return impact_dict.get(self.impact, self.impact)
    
    def get_classe_display(self):
        classe_dict = dict(self.CLASSE_CHOICES)
        return classe_dict.get(self.classe, self.classe)
    
    def get_categoria_display(self):
        if not self.categoria:
            return 'Não definida'
        
        categorias = self.categoria.split(',')
        categoria_dict = {'material': 'Material', 'servico': 'Serviço'}
        display_names = [categoria_dict.get(cat.strip(), cat.strip()) for cat in categorias]
        
        if len(display_names) > 1:
            return ' e '.join(display_names)
        return display_names[0] if display_names else 'Não definida'
    
    @property
    def is_overdue(self):
        """Verifica se o prazo de entrega foi ultrapassado"""
        if not self.delivery_deadline:
            return False
        return date.today() > self.delivery_deadline
    
    @property
    def days_until_deadline(self):
        """Retorna número de dias até o prazo (negativo se atrasado)"""
        if not self.delivery_deadline:
            return None
        delta = self.delivery_deadline - date.today()
        return delta.days
    
    def is_in_progress(self):
        """Verifica se o pedido está em andamento"""
        return self.status not in ['recebido', 'finalizado', 'cancelado']
    
    def is_completed(self):
        """Verifica se o pedido foi finalizado"""
        return self.status in ['recebido', 'finalizado', 'cancelado']
    
    def __repr__(self):
        return f'<AcquisitionRequest {self.title}>'

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    file_content = db.Column(db.LargeBinary)  # Nova coluna para salvar no banco
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
