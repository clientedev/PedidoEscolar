#!/usr/bin/env python3
"""
Script to populate sample data based on the provided Excel sheet
"""
from app import app, db
from models import User, AcquisitionRequest, StatusChange
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def create_sample_users():
    """Create sample users based on the names from the Excel sheet"""
    users_data = [
        {"username": "ariane", "full_name": "Ariane Santos", "email": "ariane.santos@senaimorvanfigueiredo.edu.br"},
        {"username": "edilson", "full_name": "Edilson Costa", "email": "edilson.costa@senaimorvanfigueiredo.edu.br"},
        {"username": "edson", "full_name": "Edson Oliveira", "email": "edson.oliveira@senaimorvanfigueiredo.edu.br"},
    ]
    
    created_users = []
    
    for user_data in users_data:
        # Check if user already exists
        existing_user = User.query.filter_by(username=user_data["username"]).first()
        if not existing_user:
            user = User()
            user.username = user_data["username"]
            user.full_name = user_data["full_name"]
            user.email = user_data["email"]
            user.password_hash = generate_password_hash("senha123")  # Default password
            user.is_admin = False
            user.active = True
            user.needs_password_reset = False
            
            db.session.add(user)
            created_users.append(user)
            print(f"Created user: {user.full_name}")
        else:
            created_users.append(existing_user)
            print(f"User already exists: {existing_user.full_name}")
    
    return created_users

def create_sample_requests(users):
    """Create sample acquisition requests based on the Excel sheet"""
    
    # Get admin user to be creator of some requests
    admin_user = User.query.filter_by(username='admin').first()
    
    # Sample requests based on the Excel data
    requests_data = [
        {
            "title": "piso das escadas - entrada escola",
            "description": "Reforma do piso das escadas na entrada da escola para melhorar segurança e aparência",
            "responsible": "edilson",
            "status": "orcamento",
            "observations": "Aguardando orçamentos"
        },
        {
            "title": "piso laminado - bloco LI",
            "description": "Instalação de piso laminado no bloco LI para renovação das salas",
            "responsible": "ariane",
            "status": "orcamento", 
            "observations": "Aguardando orçamentos"
        },
        {
            "title": "aplicação de rodapé - banheiro funcionários, sala Jefferson, secretaria",
            "description": "Instalação de rodapés nos banheiros dos funcionários, sala Jefferson e secretaria",
            "responsible": "ariane",
            "status": "fase_compra",
            "observations": "Falta aprovação Ariane/José Lúis"
        },
        {
            "title": "barreira paisagística",
            "description": "Construção de barreira paisagística para melhorar o visual da escola",
            "responsible": "ariane",
            "status": "orcamento",
            "observations": "Aguardando entrega"
        },
        {
            "title": "pontos - aula empilhadeira",
            "description": "Instalação de pontos elétricos para as aulas de empilhadeira",
            "responsible": "ariane",
            "status": "fase_compra",
            "observations": "Aguardando entrega"
        },
        {
            "title": "reforma barracão - estacionamento",
            "description": "Reforma do barracão utilizado como estacionamento",
            "responsible": "edson",
            "status": "a_caminho",
            "observations": "Material entregue/iniciou o serviço"
        },
        {
            "title": "privada + vidros - oficina",
            "description": "Instalação de privada e vidros na oficina",
            "responsible": None,
            "status": "orcamento",
            "observations": None
        },
        {
            "title": "cabeamento de rede - sala 207",
            "description": "Instalação de cabeamento de rede na sala 207",
            "responsible": "edilson",
            "status": "orcamento",
            "observations": None
        },
        {
            "title": "cabeamento de rede - metrologia",
            "description": "Instalação de cabeamento de rede no laboratório de metrologia",
            "responsible": "edilson",
            "status": "orcamento",
            "observations": None
        },
        {
            "title": "cabeamento de rede - energia solar",
            "description": "Instalação de cabeamento de rede para sistema de energia solar",
            "responsible": "edilson",
            "status": "orcamento",
            "observations": None
        },
        {
            "title": "bancos de cimento - pátio",
            "description": "Construção de bancos de cimento no pátio da escola",
            "responsible": "ariane",
            "status": "orcamento",
            "observations": None
        },
        {
            "title": "vasos de plantas",
            "description": "Aquisição de vasos de plantas para decoração da escola",
            "responsible": None,
            "status": "orcamento",
            "observations": None
        },
        {
            "title": "plantas",
            "description": "Aquisição de plantas para jardinagem da escola",
            "responsible": None,
            "status": "orcamento",
            "observations": None
        },
        {
            "title": "baião de madeira - oficina 1 e 2",
            "description": "Construção de baião de madeira nas oficinas 1 e 2",
            "responsible": "ariane",
            "status": "orcamento",
            "observations": None
        },
        {
            "title": "SSD - upgrade de computadores",
            "description": "Upgrade de computadores com instalação de SSD",
            "responsible": "ariane",
            "status": "finalizado",
            "observations": "Entrega dia 12/08"
        },
        {
            "title": "armário da pia - copa",
            "description": "Instalação de armário da pia na copa",
            "responsible": "ariane",
            "status": "fase_compra",
            "observations": "Em fase de produção"
        },
        {
            "title": "CFTV(troca das 4 câmeras)",
            "description": "Troca das 4 câmeras do sistema de CFTV",
            "responsible": "ariane",
            "status": "a_caminho",
            "observations": "Entregou o material, falta fazer a instalação"
        },
        {
            "title": "HEADSET JABRA",
            "description": "Aquisição de headsets JABRA para comunicação",
            "responsible": "ariane",
            "status": "finalizado",
            "observations": "Entrega dia 14/08"
        },
        {
            "title": "fechadura eletrônica recepção",
            "description": "Instalação de fechadura eletrônica na recepção",
            "responsible": "ariane",
            "status": "orcamento",
            "observations": "Aguardando orçamentos"
        },
        {
            "title": "Portimão",
            "description": "Materiais e serviços para área do Portimão",
            "responsible": "edilson",
            "status": "a_caminho",
            "observations": "Previsão de entrega até sexta feira 22/08"
        },
        {
            "title": "Bandeiras",
            "description": "Aquisição de bandeiras para eventos e cerimônias",
            "responsible": "edson",
            "status": "orcamento",
            "observations": None
        }
    ]
    
    # Create user lookup dictionary
    user_lookup = {user.username: user for user in users}
    user_lookup["admin"] = admin_user
    
    created_requests = []
    
    for i, req_data in enumerate(requests_data):
        # Check if request already exists (by title)
        existing_request = AcquisitionRequest.query.filter_by(title=req_data["title"]).first()
        if existing_request:
            print(f"Request already exists: {req_data['title']}")
            continue
        
        # Create request
        request_obj = AcquisitionRequest()
        request_obj.title = req_data["title"]
        request_obj.description = req_data["description"]
        request_obj.status = req_data["status"]
        request_obj.observations = req_data.get("observations")
        
        # Assign creator (alternate between admin and users)
        creator_users = [admin_user] + users
        request_obj.created_by_id = creator_users[i % len(creator_users)].id
        
        # Assign responsible user
        if req_data["responsible"]:
            responsible_user = user_lookup.get(req_data["responsible"])
            if responsible_user:
                request_obj.responsible_id = responsible_user.id
        
        # Set creation date (vary dates over last 30 days)
        days_ago = random.randint(1, 30)
        request_obj.created_at = datetime.now() - timedelta(days=days_ago)
        request_obj.updated_at = request_obj.created_at + timedelta(hours=random.randint(1, 48))
        
        db.session.add(request_obj)
        db.session.flush()  # Get ID
        
        # Create initial status change
        status_change = StatusChange()
        status_change.old_status = None
        status_change.new_status = 'orcamento'
        status_change.request_id = request_obj.id
        status_change.changed_by_id = request_obj.created_by_id
        status_change.comments = 'Pedido criado'
        status_change.change_date = request_obj.created_at
        
        db.session.add(status_change)
        
        # Add additional status changes for non-initial status
        if req_data["status"] != "orcamento":
            current_status = req_data["status"]
            
            # Status progression: orcamento -> fase_compra -> a_caminho -> finalizado
            status_progression = {
                "fase_compra": ["orcamento"],
                "a_caminho": ["orcamento", "fase_compra"],
                "finalizado": ["orcamento", "fase_compra", "a_caminho"]
            }
            
            if current_status in status_progression:
                previous_statuses = status_progression[current_status]
                
                for j, prev_status in enumerate(previous_statuses[:-1]):
                    next_status = previous_statuses[j + 1]
                    
                    change_date = request_obj.created_at + timedelta(days=random.randint(1, 5) * (j + 1))
                    
                    status_change = StatusChange()
                    status_change.old_status = prev_status
                    status_change.new_status = next_status
                    status_change.request_id = request_obj.id
                    status_change.changed_by_id = random.choice([admin_user.id] + [u.id for u in users])
                    status_change.comments = f'Status alterado para {next_status}'
                    status_change.change_date = change_date
                    
                    db.session.add(status_change)
                
                # Final status change
                final_change_date = request_obj.created_at + timedelta(days=random.randint(1, 5) * len(previous_statuses))
                
                status_change = StatusChange()
                status_change.old_status = previous_statuses[-1]
                status_change.new_status = current_status
                status_change.request_id = request_obj.id
                status_change.changed_by_id = random.choice([admin_user.id] + [u.id for u in users])
                status_change.comments = req_data.get("observations", f'Status alterado para {current_status}')
                status_change.change_date = final_change_date
                
                db.session.add(status_change)
                
                # Update request updated_at
                request_obj.updated_at = final_change_date
        
        created_requests.append(request_obj)
        print(f"Created request: {request_obj.title}")
    
    return created_requests

def populate_sample_data():
    """Main function to populate all sample data"""
    with app.app_context():
        print("Creating sample users...")
        users = create_sample_users()
        
        print("Creating sample requests...")
        requests = create_sample_requests(users)
        
        db.session.commit()
        print(f"Successfully created {len(users)} users and {len(requests)} requests!")
        
        return users, requests

if __name__ == "__main__":
    populate_sample_data()