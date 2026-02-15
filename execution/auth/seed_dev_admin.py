"""
Script to seed development admin user.
This runs automatically on startup when DEV_MODE=true.
"""
import os
import sys
from datetime import datetime

def seed_dev_admin():
    """Create development admin user if not exists"""
    print("🌱 Seeding development admin user...")
    
    # Verificar se está em modo de desenvolvimento
    dev_mode = os.getenv("DEV_MODE", "false").lower() == "true"
    
    if dev_mode:
        # Aqui você pode implementar a lógica real de criação do admin
        # Por enquanto, apenas uma simulação
        print("✅ Dev admin seeded successfully (simulated)")
    else:
        print("ℹ️ Not in dev mode, skipping admin seed")
    
    return True

if __name__ == "__main__":
    seed_dev_admin()