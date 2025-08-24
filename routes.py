import os
import secrets
from datetime import datetime, date
from flask import render_template, redirect, url_for, flash, request, send_from_directory, abort, Response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_, desc, func
from app import app, db
from models import User, AcquisitionRequest, Attachment, StatusChange
from forms import LoginForm, AcquisitionRequestForm, EditRequestForm, UserForm, SearchForm, FirstPasswordForm, BulkImportForm
from pdf_generator import generate_request_pdf, generate_general_report
from excel_generator import generate_requests_excel, generate_request_excel
from excel_template_generator import generate_import_template, process_import_file
from flask import Response

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    """Save uploaded file and return filename"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Generate unique filename to prevent conflicts
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{secrets.token_hex(8)}{ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return unique_filename, filename, os.path.getsize(file_path)
    return None, None, None

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    # Get filter parameters
    search_form = SearchForm()
    search = request.args.get('search', '')
    status_filter = request.args.get('status_filter', '')
    classe_filter = request.args.get('classe_filter', '')
    categoria_filter = request.args.get('categoria_filter', '')
    responsible_filter = request.args.get('responsible_filter', 0, type=int)
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Build query
    query = AcquisitionRequest.query
    
    if search:
        query = query.filter(or_(
            AcquisitionRequest.title.contains(search),
            AcquisitionRequest.description.contains(search)
        ))
    
    if status_filter:
        query = query.filter(AcquisitionRequest.status == status_filter)
        
    if classe_filter:
        query = query.filter(AcquisitionRequest.classe == classe_filter)
        
    if categoria_filter:
        query = query.filter(AcquisitionRequest.categoria == categoria_filter)
    
    if responsible_filter > 0:
        query = query.filter(AcquisitionRequest.responsible_id == responsible_filter)
    
    # Date range filtering
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(AcquisitionRequest.request_date >= from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(AcquisitionRequest.request_date <= to_date)
        except ValueError:
            pass
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10  # 10 items per page as requested
    
    # Order by most recent and paginate
    requests_pagination = query.order_by(desc(AcquisitionRequest.updated_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    requests = requests_pagination.items
    
    # Get statistics for dashboard
    total_requests = AcquisitionRequest.query.count()
    status_counts = {}
    for status_code, status_name in AcquisitionRequest.STATUS_CHOICES:
        count = AcquisitionRequest.query.filter_by(status=status_code).count()
        status_counts[status_name] = count
    
    # Set form defaults from URL parameters
    search_form.search.data = search
    search_form.status_filter.data = status_filter
    search_form.classe_filter.data = classe_filter
    search_form.categoria_filter.data = categoria_filter
    search_form.responsible_filter.data = responsible_filter
    if date_from:
        try:
            search_form.date_from.data = datetime.strptime(date_from, '%Y-%m-%d').date()
        except ValueError:
            pass
    if date_to:
        try:
            search_form.date_to.data = datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Calculate totals
    total_estimated = sum([req.estimated_value or 0 for req in requests])
    total_final = sum([req.final_value or 0 for req in requests])
    
    return render_template('dashboard.html', 
                         requests=requests, 
                         pagination=requests_pagination,
                         search_form=search_form,
                         total_requests=total_requests,
                         status_counts=status_counts,
                         total_estimated=total_estimated,
                         total_final=total_final,
                         current_search=search,
                         current_status_filter=status_filter,
                         current_classe_filter=classe_filter,
                         current_categoria_filter=categoria_filter,
                         current_responsible_filter=responsible_filter,
                         current_date_from=date_from,
                         current_date_to=date_to)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            # If user has no password set, they need username only for first login
            if not user.password_hash and user.needs_password_reset:
                if not user.is_active:
                    flash('Sua conta está desativada. Entre em contato com o administrador.', 'danger')
                    return redirect(url_for('login'))
                login_user(user)
                return redirect(url_for('first_password'))
            # Normal password authentication
            elif user.password_hash and check_password_hash(user.password_hash, form.password.data):
                if not user.is_active:
                    flash('Sua conta está desativada. Entre em contato com o administrador.', 'danger')
                    return redirect(url_for('login'))
                # Check if user needs to set password for first time  
                if user.needs_password_reset:
                    login_user(user)
                    return redirect(url_for('first_password'))
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                flash(f'Bem-vindo, {user.full_name}!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Usuário ou senha incorretos.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('login'))

@app.route('/first-password', methods=['GET', 'POST'])
@login_required
def first_password():
    # Only allow users who need password reset
    if not current_user.needs_password_reset:
        return redirect(url_for('dashboard'))
    
    form = FirstPasswordForm()
    if form.validate_on_submit():
        current_user.password_hash = generate_password_hash(form.new_password.data)
        current_user.needs_password_reset = False
        db.session.commit()
        flash('Sua senha foi definida com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('first_password.html', form=form)

@app.route('/request/new', methods=['GET', 'POST'])
@login_required
def new_request():
    form = AcquisitionRequestForm()
    if form.validate_on_submit():
        # Create new request
        request_obj = AcquisitionRequest()
        request_obj.title = form.title.data
        request_obj.description = form.description.data
        request_obj.status = form.status.data
        request_obj.classe = form.classe.data
        
        # Process categoria checkboxes
        categorias = []
        if form.categoria_material.data:
            categorias.append('material')
        if form.categoria_servico.data:
            categorias.append('servico')
        request_obj.categoria = ','.join(categorias) if categorias else 'material'
        request_obj.observations = form.observations.data
        request_obj.estimated_value = form.estimated_value.data
        request_obj.final_value = form.final_value.data
        request_obj.request_date = form.request_date.data
        request_obj.created_by_id = current_user.id
        request_obj.responsible_id = form.responsible_id.data if form.responsible_id.data > 0 else None
        db.session.add(request_obj)
        db.session.flush()  # Get the ID
        
        # Create initial status change record
        status_change = StatusChange()
        status_change.old_status = None
        status_change.new_status = form.status.data
        status_change.request_id = request_obj.id
        status_change.changed_by_id = current_user.id
        status_change.comments = 'Pedido criado'
        db.session.add(status_change)
        
        # Handle file uploads
        uploaded_files = []
        attachment_data = form.attachments.data or []
        for file in attachment_data:
            if file and file.filename:
                unique_filename, original_filename, file_size = save_file(file)
                if unique_filename:
                    attachment = Attachment()
                    attachment.filename = unique_filename
                    attachment.original_filename = original_filename
                    attachment.file_size = file_size
                    attachment.request_id = request_obj.id
                    attachment.uploaded_by_id = current_user.id
                    db.session.add(attachment)
                    uploaded_files.append(original_filename)
        
        db.session.commit()
        
        flash_message = f'Pedido de aquisição "{request_obj.title}" criado com sucesso!'
        if uploaded_files:
            flash_message += f' Arquivos anexados: {", ".join(uploaded_files)}'
        flash(flash_message, 'success')
        return redirect(url_for('view_request', id=request_obj.id))
    
    return render_template('request_form.html', form=form, request_obj=None, title='Novo Pedido de Aquisição')

@app.route('/request/<int:id>')
@login_required
def view_request(id):
    request_obj = AcquisitionRequest.query.get_or_404(id)
    status_history = StatusChange.query.filter_by(request_id=id).order_by(desc(StatusChange.change_date)).all()
    return render_template('request_detail.html', request_obj=request_obj, status_history=status_history)

@app.route('/request/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_request(id):
    request_obj = AcquisitionRequest.query.get_or_404(id)
    
    # Only admins or the creator can edit
    if not current_user.is_admin and request_obj.created_by_id != current_user.id:
        flash('Você não tem permissão para editar este pedido.', 'danger')
        return redirect(url_for('view_request', id=id))
    
    form = EditRequestForm(obj=request_obj)
    if form.validate_on_submit():
        old_status = request_obj.status
        old_responsible = request_obj.responsible_id
        
        # Update request
        request_obj.title = form.title.data
        request_obj.description = form.description.data
        request_obj.status = form.status.data
        request_obj.classe = form.classe.data
        
        # Process categoria checkboxes
        categorias = []
        if form.categoria_material.data:
            categorias.append('material')
        if form.categoria_servico.data:
            categorias.append('servico')
        request_obj.categoria = ','.join(categorias) if categorias else 'material'
        request_obj.observations = form.observations.data
        request_obj.estimated_value = form.estimated_value.data
        request_obj.final_value = form.final_value.data
        request_obj.request_date = form.request_date.data
        request_obj.responsible_id = form.responsible_id.data if form.responsible_id.data > 0 else None
        request_obj.updated_at = datetime.utcnow()
        
        # Record status change if status changed
        if old_status != request_obj.status:
            status_change = StatusChange()
            status_change.old_status = old_status
            status_change.new_status = request_obj.status
            status_change.request_id = request_obj.id
            status_change.changed_by_id = current_user.id
            status_change.comments = form.change_comments.data
            db.session.add(status_change)
        
        # Handle new file uploads
        uploaded_files = []
        attachment_data = form.attachments.data or []
        for file in attachment_data:
            if file and file.filename:
                unique_filename, original_filename, file_size = save_file(file)
                if unique_filename:
                    attachment = Attachment()
                    attachment.filename = unique_filename
                    attachment.original_filename = original_filename
                    attachment.file_size = file_size
                    attachment.request_id = request_obj.id
                    attachment.uploaded_by_id = current_user.id
                    db.session.add(attachment)
                    uploaded_files.append(original_filename)
        
        db.session.commit()
        
        flash_message = f'Pedido "{request_obj.title}" atualizado com sucesso!'
        if uploaded_files:
            flash_message += f' Novos arquivos anexados: {", ".join(uploaded_files)}'
        flash(flash_message, 'success')
        return redirect(url_for('view_request', id=id))
    
    # Pre-populate form
    if request_obj.responsible_id:
        form.responsible_id.data = request_obj.responsible_id
        
    # Pre-populate categoria checkboxes
    if request_obj.categoria:
        categorias = request_obj.categoria.split(',')
        form.categoria_material.data = 'material' in categorias
        form.categoria_servico.data = 'servico' in categorias
    
    return render_template('request_form.html', form=form, request_obj=request_obj, title='Editar Pedido')

@app.route('/upload/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/attachment/<int:id>/delete', methods=['POST'])
@login_required
def delete_attachment(id):
    attachment = Attachment.query.get_or_404(id)
    request_obj = attachment.request
    
    # Only admins or the uploader can delete
    if not current_user.is_admin and attachment.uploaded_by_id != current_user.id:
        flash('Você não tem permissão para excluir este anexo.', 'danger')
        return redirect(url_for('view_request', id=request_obj.id))
    
    # Delete file from filesystem
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], attachment.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        app.logger.error(f"Error deleting file {attachment.filename}: {e}")
    
    # Delete database record
    db.session.delete(attachment)
    db.session.commit()
    
    flash(f'Anexo "{attachment.original_filename}" removido com sucesso.', 'success')
    return redirect(url_for('view_request', id=request_obj.id))

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('Acesso negado. Apenas administradores podem acessar esta página.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_requests = AcquisitionRequest.query.count()
    
    recent_requests = AcquisitionRequest.query.order_by(desc(AcquisitionRequest.created_at)).limit(5).all()
    recent_changes = StatusChange.query.order_by(desc(StatusChange.change_date)).limit(10).all()
    
    return render_template('admin_panel.html',
                         total_users=total_users,
                         active_users=active_users,
                         total_requests=total_requests,
                         recent_requests=recent_requests,
                         recent_changes=recent_changes)

@app.route('/admin/users')
@login_required
def user_management():
    if not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard'))
    
    users = User.query.order_by(User.full_name).all()
    return render_template('user_management.html', users=users)

@app.route('/admin/user/new', methods=['GET', 'POST'])
@login_required
def new_user():
    if not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = UserForm()
    if form.validate_on_submit():
        # Create new user without password, they will set it on first login
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.full_name = form.full_name.data
        user.is_admin = form.is_admin.data
        user.active = form.is_active.data
        user.needs_password_reset = True  # User must set password on first login
        # Don't set password_hash - it will be None until user sets it
        db.session.add(user)
        db.session.commit()
        flash(f'Usuário "{user.full_name}" criado com sucesso! Ele deverá definir uma senha no primeiro login.', 'success')
        return redirect(url_for('user_management'))
    
    return render_template('user_management.html', form=form, title='Novo Usuário')

@app.route('/admin/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(id)
    form = UserForm(original_user=user, obj=user)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.full_name = form.full_name.data
        user.is_admin = form.is_admin.data
        user.active = form.is_active.data
        
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
            user.needs_password_reset = False
        
        db.session.commit()
        flash(f'Usuário "{user.full_name}" atualizado com sucesso!', 'success')
        return redirect(url_for('user_management'))
    
    return render_template('user_management.html', form=form, user=user, title='Editar Usuário')

@app.route('/admin/user/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_user_status(id):
    if not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Você não pode desativar sua própria conta.', 'warning')
        return redirect(url_for('user_management'))
    
    user.active = not user.active
    db.session.commit()
    
    status = 'ativado' if user.active else 'desativado'
    flash(f'Usuário "{user.full_name}" {status} com sucesso!', 'success')
    return redirect(url_for('user_management'))

@app.route('/request/<int:id>/pdf')
@login_required
def generate_request_pdf_route(id):
    """Gera PDF de um pedido específico"""
    try:
        request_obj = AcquisitionRequest.query.get_or_404(id)
        pdf_buffer = generate_request_pdf(request_obj)
        
        filename = f"Pedido_{request_obj.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return Response(
            pdf_buffer.getvalue(),
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        app.logger.error(f"Erro ao gerar PDF do pedido {id}: {e}")
        flash('Erro ao gerar PDF. Tente novamente.', 'danger')
        return redirect(url_for('view_request', id=id))

@app.route('/reports/filtered-pdf')
@login_required
def generate_filtered_pdf():
    """Gera relatório filtrado em PDF"""
    try:
        # Get the same filter parameters as dashboard
        search = request.args.get('search', '')
        status_filter = request.args.get('status_filter', '')
        classe_filter = request.args.get('classe_filter', '')
        categoria_filter = request.args.get('categoria_filter', '')
        responsible_filter = request.args.get('responsible_filter', 0, type=int)
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # Apply same filters as dashboard
        query = AcquisitionRequest.query
        
        if search:
            query = query.filter(or_(
                AcquisitionRequest.title.contains(search),
                AcquisitionRequest.description.contains(search)
            ))
        
        if status_filter:
            query = query.filter(AcquisitionRequest.status == status_filter)
            
        if classe_filter:
            query = query.filter(AcquisitionRequest.classe == classe_filter)
            
        if categoria_filter:
            query = query.filter(AcquisitionRequest.categoria == categoria_filter)
        
        if responsible_filter > 0:
            query = query.filter(AcquisitionRequest.responsible_id == responsible_filter)
        
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(AcquisitionRequest.request_date >= from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(AcquisitionRequest.request_date <= to_date)
            except ValueError:
                pass
        
        filtered_requests = query.order_by(desc(AcquisitionRequest.updated_at)).all()
        pdf_buffer = generate_general_report(filtered_requests)
        
        filename = f"Relatorio_Filtrado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return Response(
            pdf_buffer.getvalue(),
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        app.logger.error(f"Erro ao gerar relatório filtrado: {e}")
        flash('Erro ao gerar relatório. Tente novamente.', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/request/<int:id>/delete', methods=['POST'])
@login_required
def delete_request(id):
    """Excluir um pedido (apenas administradores)"""
    if not current_user.is_admin:
        flash('Acesso negado. Apenas administradores podem excluir pedidos.', 'danger')
        return redirect(url_for('dashboard'))
    
    request_obj = AcquisitionRequest.query.get_or_404(id)
    
    try:
        # Excluir arquivos anexos do sistema de arquivos
        for attachment in request_obj.attachments:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], attachment.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # O SQLAlchemy cuidará da cascata para anexos e mudanças de status
        db.session.delete(request_obj)
        db.session.commit()
        
        flash(f'Pedido #{request_obj.id} "{request_obj.title}" foi excluído com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro ao excluir pedido {id}: {e}")
        flash('Erro ao excluir o pedido. Tente novamente.', 'danger')
    
    return redirect(url_for('dashboard'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html', error_message='Página não encontrada'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('base.html', error_message='Erro interno do servidor'), 500

@app.route('/export/excel/filtered')
@login_required
def export_excel_filtered():
    """Export filtered requests to Excel"""
    # Get the same filter parameters as dashboard
    search = request.args.get('search', '')
    status_filter = request.args.get('status_filter', '')
    classe_filter = request.args.get('classe_filter', '')
    categoria_filter = request.args.get('categoria_filter', '')
    responsible_filter = request.args.get('responsible_filter', 0, type=int)
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Apply same filters as dashboard
    query = AcquisitionRequest.query
    
    if search:
        query = query.filter(or_(
            AcquisitionRequest.title.contains(search),
            AcquisitionRequest.description.contains(search)
        ))
    
    if status_filter:
        query = query.filter(AcquisitionRequest.status == status_filter)
        
    if classe_filter:
        query = query.filter(AcquisitionRequest.classe == classe_filter)
        
    if categoria_filter:
        query = query.filter(AcquisitionRequest.categoria == categoria_filter)
    
    if responsible_filter > 0:
        query = query.filter(AcquisitionRequest.responsible_id == responsible_filter)
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(AcquisitionRequest.request_date >= from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(AcquisitionRequest.request_date <= to_date)
        except ValueError:
            pass
    
    filtered_requests = query.order_by(desc(AcquisitionRequest.updated_at)).all()
    wb = generate_requests_excel(filtered_requests)
    
    # Create response
    from io import BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    response = Response(output.read(),
                       mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response.headers['Content-Disposition'] = f'attachment; filename=pedidos_filtrados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return response

@app.route('/export/excel/request/<int:id>')
@login_required
def export_excel_request(id):
    """Export specific request to Excel"""
    wb = generate_request_excel(id)
    
    # Create response
    from io import BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    request_obj = AcquisitionRequest.query.get_or_404(id)
    response = Response(output.read(),
                       mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    safe_title = ''.join(c for c in request_obj.title if c.isalnum() or c in (' ', '-', '_')).rstrip()[:30]
    response.headers['Content-Disposition'] = f'attachment; filename=pedido_{id}_{safe_title}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return response

@app.route('/bulk-import')
@login_required
def bulk_import_page():
    """Página para importação em lote"""
    form = BulkImportForm()
    return render_template('bulk_import.html', form=form)

@app.route('/bulk-import/template')
@login_required
def download_import_template():
    """Download do modelo Excel para importação"""
    wb = generate_import_template()
    
    # Create response
    from io import BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    response = Response(output.read(),
                       mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response.headers['Content-Disposition'] = f'attachment; filename=modelo_importacao_pedidos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return response

@app.route('/bulk-import', methods=['POST'])
@login_required
def process_bulk_import():
    """Processa a importação em lote de pedidos"""
    form = BulkImportForm()
    
    if form.validate_on_submit():
        try:
            # Save uploaded file temporarily
            file = form.excel_file.data
            filename = secure_filename(file.filename)
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{secrets.token_hex(8)}_{filename}")
            file.save(temp_path)
            
            # Process the file
            pedidos, erros = process_import_file(temp_path, current_user)
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if not pedidos:
                flash('Nenhum pedido válido encontrado no arquivo.', 'warning')
                return render_template('bulk_import.html', form=form, errors=erros)
            
            # Create requests in database
            created_count = 0
            for pedido_data in pedidos:
                try:
                    # Create new request
                    request_obj = AcquisitionRequest()
                    request_obj.title = pedido_data['titulo']
                    request_obj.description = pedido_data['descricao']
                    request_obj.status = pedido_data['status']
                    request_obj.classe = pedido_data['classe']
                    request_obj.categoria = pedido_data['categoria']
                    request_obj.estimated_value = pedido_data['valor_estimado']
                    request_obj.final_value = pedido_data['valor_final']
                    request_obj.responsible_id = pedido_data['responsible_id']
                    request_obj.observations = pedido_data['observacoes']
                    request_obj.request_date = pedido_data['data_solicitacao']
                    request_obj.created_by_id = current_user.id
                    db.session.add(request_obj)
                    db.session.flush()  # Get the ID
                    
                    # Create initial status change record
                    status_change = StatusChange()
                    status_change.old_status = None
                    status_change.new_status = pedido_data['status']
                    status_change.request_id = request_obj.id
                    status_change.changed_by_id = current_user.id
                    status_change.comments = 'Pedido criado via importação em lote'
                    db.session.add(status_change)
                    
                    created_count += 1
                    
                except Exception as e:
                    erros.append(f"Linha {pedido_data['linha']}: Erro ao criar pedido - {str(e)}")
                    db.session.rollback()
                    continue
            
            if created_count > 0:
                db.session.commit()
                flash(f'{created_count} pedido(s) importado(s) com sucesso!', 'success')
                
                if erros:
                    flash(f'Avisos durante a importação: {len(erros)} problema(s) encontrado(s).', 'warning')
                    return render_template('bulk_import.html', form=BulkImportForm(), errors=erros, success_count=created_count)
                
                return redirect(url_for('dashboard'))
            else:
                flash('Nenhum pedido foi criado devido a erros.', 'danger')
                return render_template('bulk_import.html', form=form, errors=erros)
                
        except Exception as e:
            flash(f'Erro ao processar arquivo: {str(e)}', 'danger')
            return render_template('bulk_import.html', form=form)
    
    return render_template('bulk_import.html', form=form)
