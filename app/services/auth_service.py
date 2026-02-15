from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import os
import traceback

print("🔧 Carregando auth_service.py...")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"

print(f"✅ auth_service.py carregado. SECRET_KEY: {SECRET_KEY[:5]}...")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

    
    try:
        print("📦 Criando sessão do banco...")
        db = SessionLocal()
        print("✅ Sessão criada")
        
        print("🔍 Verificando se usuário já existe...")
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print("❌ Usuário já existe!")
            return {"ok": False, "data": None, "error_key": "auth.email_already_exists"}
        print("✅ Usuário não existe, pode criar")
        
        print("🔐 Gerando hash da senha...")
        hashed_password = get_password_hash(password)
        print(f"✅ Hash gerado: {hashed_password[:20]}...")
        
        print("👤 Criando objeto User...")
        new_user = User(
            email=email,
            name=full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=False,
            created_at=datetime.now()
        )
        print("✅ Objeto User criado")
        
        print("💾 Adicionando ao banco...")
        db.add(new_user)
        print("✅ Adicionado, fazendo commit...")
        db.commit()
        print("✅ Commit realizado, fazendo refresh...")
        db.refresh(new_user)
        print(f"✅ Usuário salvo com ID: {new_user.id}")
        
        return {
            "ok": True,
            "data": {
                "id": new_user.id,
                "email": new_user.email,
                "full_name": new_user.name
            },
            "error_key": None
        }
    except Exception as e:
        print("\n" + "💥"*30)
        print("💥 EXCEÇÃO CAPTURADA!")
        print(f"💥 Tipo: {type(e).__name__}")
        print(f"💥 Mensagem: {str(e)}")
        print("💥 Traceback:")
        traceback.print_exc()
        print("💥"*30 + "\n")
        
        if 'db' in locals():
            print("🔄 Fazendo rollback...")
            db.rollback()
            print("✅ Rollback feito")
        
        return {"ok": False, "data": None, "error_key": "internal_error"}
    finally:
        if 'db' in locals():
            print("🔚 Fechando sessão do banco...")
            db.close()
            print("✅ Sessão fechada")

def login_user(email: str, password: str, organization_slug: str = None):
    print(f"\n🔑 Login attempt: {email}")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return {"ok": False, "data": None, "error_key": "auth.invalid_credentials"}
        
        access_token = create_access_token({"sub": str(user.id), "email": user.email})
        
        return {
            "ok": True,
            "data": {
                "access_token": access_token,
                "token_type": "bearer"
            },
            "error_key": None
        }
    except Exception as e:
        print(f"Erro no login: {e}")
        traceback.print_exc()
        return {"ok": False, "data": None, "error_key": "internal_error"}
    finally:
        db.close()

def approve_user(admin_id: int, email: str):
    return {"ok": True, "data": {"approved": True}, "error_key": None}

print("✅ auth_service.py configurado com logs!")