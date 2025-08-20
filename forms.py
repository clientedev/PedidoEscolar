from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import StringField, TextAreaField, SelectField, PasswordField, BooleanField, SubmitField, DecimalField, DateField
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
    observations = TextAreaField('Observações', validators=[Optional(), Length(max=500)])
    estimated_value = DecimalField('Valor Estimado (R$)', validators=[Optional(), NumberRange(min=0)], places=2)
    final_value = DecimalField('Valor Final (R$)', validators=[Optional(), NumberRange(min=0)], places=2)
    responsible_id = SelectField('Responsável pela Cotação', coerce=int, validators=[Optional()])
    attachments = MultipleFileField('Anexar Orçamentos', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg'], 
                   'Apenas arquivos PDF, Word, Excel e imagens são permitidos.')
    ])
    submit = SubmitField('Salvar Pedido')
    
    def __init__(self, *args, **kwargs):
        super(AcquisitionRequestForm, self).__init__(*args, **kwargs)
        # Populate status choices
        self.status.choices = AcquisitionRequest.STATUS_CHOICES
        # Populate responsible choices with active users
        self.responsible_id.choices = [(0, 'Selecionar responsável...')] + [
            (user.id, user.full_name) for user in User.query.filter_by(active=True).all()
        ]

class EditRequestForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Descrição', validators=[DataRequired(), Length(min=10, max=1000)])
    status = SelectField('Status', validators=[DataRequired()])
    observations = TextAreaField('Observações', validators=[Optional(), Length(max=500)])
    estimated_value = DecimalField('Valor Estimado (R$)', validators=[Optional(), NumberRange(min=0)], places=2)
    final_value = DecimalField('Valor Final (R$)', validators=[Optional(), NumberRange(min=0)], places=2)
    responsible_id = SelectField('Responsável pela Cotação', coerce=int, validators=[Optional()])
    attachments = MultipleFileField('Anexar Novos Orçamentos', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg'], 
                   'Apenas arquivos PDF, Word, Excel e imagens são permitidos.')
    ])
    change_comments = TextAreaField('Comentários sobre a alteração', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Atualizar Pedido')
    
    def __init__(self, *args, **kwargs):
        super(EditRequestForm, self).__init__(*args, **kwargs)
        self.status.choices = AcquisitionRequest.STATUS_CHOICES
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
    responsible_filter = SelectField('Filtrar por Responsável', coerce=int, validators=[Optional()])
    date_from = DateField('Data Inicial', validators=[Optional()])
    date_to = DateField('Data Final', validators=[Optional()])
    submit = SubmitField('Filtrar')
    
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.status_filter.choices = [('', 'Todos os status')] + AcquisitionRequest.STATUS_CHOICES
        self.responsible_filter.choices = [(0, 'Todos os responsáveis')] + [
            (user.id, user.full_name) for user in User.query.filter_by(active=True).all()
        ]
