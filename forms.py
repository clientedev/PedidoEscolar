from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import StringField, TextAreaField, SelectField, PasswordField, BooleanField, SubmitField, DecimalField, DateField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, ValidationError, Optional, NumberRange
from models import User, AcquisitionRequest

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class AcquisitionRequestForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Descrição', validators=[DataRequired(), Length(min=10, max=1000)])
    status = SelectField('Status', validators=[DataRequired()])
    priority = SelectField('Prioridade', validators=[DataRequired()])
    impact = SelectField('Impacto', validators=[DataRequired()])
    classe = SelectField('Classe', validators=[DataRequired()])
    categoria_material = BooleanField('Material')
    categoria_servico = BooleanField('Serviço')
    observations = TextAreaField('Observações', validators=[Optional(), Length(max=500)])
    estimated_value = DecimalField('Valor Estimado (R$)', validators=[Optional(), NumberRange(min=0)], places=2)
    final_value = DecimalField('Valor Final (R$)', validators=[Optional(), NumberRange(min=0)], places=2)
    responsible_id = SelectField('Responsável pela Cotação', coerce=int, validators=[Optional()])
    request_date = DateField('Data da Solicitação', validators=[DataRequired()])
    attachments = MultipleFileField('Anexar Orçamentos', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg'], 
                   'Apenas arquivos PDF, Word, Excel e imagens são permitidos.')
    ])
    submit = SubmitField('Salvar Pedido')
    
    def validate_categoria_material(self, field):
        if not self.categoria_material.data and not self.categoria_servico.data:
            raise ValidationError('Selecione pelo menos uma categoria.')
    
    def __init__(self, *args, **kwargs):
        super(AcquisitionRequestForm, self).__init__(*args, **kwargs)
        # Populate status choices
        self.status.choices = AcquisitionRequest.STATUS_CHOICES
        # Populate priority choices
        self.priority.choices = AcquisitionRequest.PRIORITY_CHOICES
        # Populate impact choices
        self.impact.choices = AcquisitionRequest.IMPACT_CHOICES
        # Populate classe choices
        self.classe.choices = AcquisitionRequest.CLASSE_CHOICES
        # Categoria fields are now checkboxes, no choices needed
        # Populate responsible choices with active users
        self.responsible_id.choices = [(0, 'Selecionar responsável...')] + [
            (user.id, user.full_name) for user in User.query.filter_by(active=True).all()
        ]
        # Set default date to today if not already set
        if not self.request_date.data:
            from datetime import date
            self.request_date.data = date.today()

class EditRequestForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Descrição', validators=[DataRequired(), Length(min=10, max=1000)])
    status = SelectField('Status', validators=[DataRequired()])
    priority = SelectField('Prioridade', validators=[DataRequired()])
    impact = SelectField('Impacto', validators=[DataRequired()])
    classe = SelectField('Classe', validators=[DataRequired()])
    categoria_material = BooleanField('Material')
    categoria_servico = BooleanField('Serviço')
    observations = TextAreaField('Observações', validators=[Optional(), Length(max=500)])
    estimated_value = DecimalField('Valor Estimado (R$)', validators=[Optional(), NumberRange(min=0)], places=2)
    final_value = DecimalField('Valor Final (R$)', validators=[Optional(), NumberRange(min=0)], places=2)
    responsible_id = SelectField('Responsável pela Cotação', coerce=int, validators=[Optional()])
    request_date = DateField('Data da Solicitação', validators=[DataRequired()])
    attachments = MultipleFileField('Anexar Novos Orçamentos', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg'], 
                   'Apenas arquivos PDF, Word, Excel e imagens são permitidos.')
    ])
    change_comments = TextAreaField('Comentários sobre a alteração', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Atualizar Pedido')
    
    def validate_categoria_material(self, field):
        if not self.categoria_material.data and not self.categoria_servico.data:
            raise ValidationError('Selecione pelo menos uma categoria.')
    
    def __init__(self, *args, **kwargs):
        super(EditRequestForm, self).__init__(*args, **kwargs)
        self.status.choices = AcquisitionRequest.STATUS_CHOICES
        self.priority.choices = AcquisitionRequest.PRIORITY_CHOICES
        self.impact.choices = AcquisitionRequest.IMPACT_CHOICES
        self.classe.choices = AcquisitionRequest.CLASSE_CHOICES
        # Categoria fields are now checkboxes, no choices needed
        self.responsible_id.choices = [(0, 'Selecionar responsável...')] + [
            (user.id, user.full_name) for user in User.query.filter_by(active=True).all()
        ]

class UserForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    full_name = StringField('Nome Completo', validators=[DataRequired(), Length(min=2, max=120)])
    password = PasswordField('Senha', validators=[Length(min=6, max=128)])
    is_admin = BooleanField('Administrador')
    is_active = BooleanField('Ativo', default=True)
    submit = SubmitField('Salvar Usuário')
    
    def __init__(self, original_user=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.original_user = original_user
    
    def validate_username(self, username):
        if self.original_user is None or username.data != self.original_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Este nome de usuário já está em uso.')
    
    def validate_email(self, email):
        if self.original_user is None or email.data != self.original_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Este email já está em uso.')

class FirstPasswordForm(FlaskForm):
    new_password = PasswordField('Nova Senha', validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField('Definir Senha')
    
    def validate_confirm_password(self, confirm_password):
        if self.new_password.data != confirm_password.data:
            raise ValidationError('As senhas não coincidem.')

class SearchForm(FlaskForm):
    search = StringField('Buscar', validators=[Optional(), Length(max=100)])
    status_filter = SelectField('Filtrar por Status', validators=[Optional()])
    priority_filter = SelectField('Filtrar por Prioridade', validators=[Optional()])
    impact_filter = SelectField('Filtrar por Impacto', validators=[Optional()])
    classe_filter = SelectField('Filtrar por Classe', validators=[Optional()])
    categoria_filter = SelectField('Filtrar por Categoria', validators=[Optional()])
    responsible_filter = SelectField('Filtrar por Responsável', coerce=int, validators=[Optional()])
    date_from = DateField('Data Inicial', validators=[Optional()])
    date_to = DateField('Data Final', validators=[Optional()])
    submit = SubmitField('Filtrar')
    
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.status_filter.choices = [('', 'Todos os status')] + AcquisitionRequest.STATUS_CHOICES
        self.priority_filter.choices = [('', 'Todas as prioridades')] + AcquisitionRequest.PRIORITY_CHOICES
        self.impact_filter.choices = [('', 'Todos os impactos')] + AcquisitionRequest.IMPACT_CHOICES
        self.classe_filter.choices = [('', 'Todas as classes')] + AcquisitionRequest.CLASSE_CHOICES
        self.categoria_filter.choices = [('', 'Todas as categorias')] + AcquisitionRequest.CATEGORIA_CHOICES
        self.responsible_filter.choices = [(0, 'Todos os responsáveis')] + [
            (user.id, user.full_name) for user in User.query.filter_by(active=True).all()
        ]

class BulkImportForm(FlaskForm):
    excel_file = FileField('Arquivo Excel', validators=[
        DataRequired('Por favor, selecione um arquivo Excel.'),
        FileAllowed(['xlsx', 'xls'], 'Apenas arquivos Excel (.xlsx, .xls) são permitidos.')
    ])
    submit = SubmitField('Importar Pedidos')
