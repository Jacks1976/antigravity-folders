#!/usr/bin/env python3
"""
Seed script for PIBG (Primeira Igreja Brasileira de Greenville)
Populates realistic church data for development and testing.
"""
import sys
import os
import sqlite3
from datetime import datetime, timedelta
import hashlib
import json

# Add parent dirs to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execution.db import get_db_connection

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def seed_users():
    """Create seed users with various roles and statuses"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        users = [
            # Admin
            {
                'email': 'admin@pibg.church',
                'password': hash_password('Admin123!@#'),
                'full_name': 'Pastor João Silva',
                'role': 'Admin',
                'status': 'Active',
                'language_pref': 'pt-BR'
            },
            # Staff
            {
                'email': 'staff@pibg.church',
                'password': hash_password('Staff123!@#'),
                'full_name': 'Diaconisa Maria Santos',
                'role': 'Staff',
                'status': 'Active',
                'language_pref': 'pt-BR'
            },
            # Musicians/Volunteers
            {
                'email': 'musica@pibg.church',
                'password': hash_password('Music123!@#'),
                'full_name': 'João Louvor',
                'role': 'Volunteer',
                'status': 'Active',
                'language_pref': 'pt-BR'
            },
            {
                'email': 'teclado@pibg.church',
                'password': hash_password('Teclado123!@#'),
                'full_name': 'Ana Ministério Musical',
                'role': 'Volunteer',
                'status': 'Active',
                'language_pref': 'pt-BR'
            },
            {
                'email': 'bateria@pibg.church',
                'password': hash_password('Bateria123!@#'),
                'full_name': 'Carlos Ritmo',
                'role': 'Volunteer',
                'status': 'Active',
                'language_pref': 'pt-BR'
            },
            # Regular members
            {
                'email': 'membro1@pibg.church',
                'password': hash_password('Member123!@#'),
                'full_name': 'Pedro Oliveira',
                'role': 'Member',
                'status': 'Active',
                'language_pref': 'pt-BR'
            },
            {
                'email': 'membro2@pibg.church',
                'password': hash_password('Member123!@#'),
                'full_name': 'Fernanda Costa',
                'role': 'Member',
                'status': 'Active',
                'language_pref': 'pt-BR'
            },
            {
                'email': 'membro3@pibg.church',
                'password': hash_password('Member123!@#'),
                'full_name': 'Ricardo Alves',
                'role': 'Member',
                'status': 'Active',
                'language_pref': 'pt-BR'
            },
            # Pending members
            {
                'email': 'visitante1@pibg.church',
                'password': hash_password('Visitor123!@#'),
                'full_name': 'Lucas Novo Membro',
                'role': 'Member',
                'status': 'Pending',
                'language_pref': 'pt-BR'
            },
            {
                'email': 'visitante2@pibg.church',
                'password': hash_password('Visitor123!@#'),
                'full_name': 'Beatriz Igreja',
                'role': 'Member',
                'status': 'Pending',
                'language_pref': 'pt-BR'
            },
        ]
        
        for user in users:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO users 
                    (email, password_hash, role, status, language_pref, created_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'))
                """, (
                    user['email'],
                    user['password'],
                    user['role'],
                    user['status'],
                    user['language_pref']
                ))
            except Exception as e:
                print(f"  Warning creating user {user['email']}: {e}")
        
        conn.commit()
        cursor.execute("SELECT COUNT(*) FROM users WHERE status='Active'")
        count = cursor.fetchone()[0]
        print(f"✓ Created/updated {count} active users")


def seed_member_profiles():
    """Create member profiles with full names"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email FROM users
            WHERE deleted_at IS NULL
        """)
        users = cursor.fetchall()
        
        names_map = {
            'admin@pibg.church': 'Pastor João Silva',
            'staff@pibg.church': 'Diaconisa Maria Santos',
            'musica@pibg.church': 'João Louvor',
            'teclado@pibg.church': 'Ana Ministério Musical',
            'bateria@pibg.church': 'Carlos Ritmo',
            'membro1@pibg.church': 'Pedro Oliveira',
            'membro2@pibg.church': 'Fernanda Costa',
            'membro3@pibg.church': 'Ricardo Alves',
            'visitante1@pibg.church': 'Lucas Novo Membro',
            'visitante2@pibg.church': 'Beatriz Igreja',
        }
        
        for user_id, email in users:
            name = names_map.get(email, 'Membro da Igreja')
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO member_profiles 
                    (user_id, full_name) 
                    VALUES (?, ?)
                """, (user_id, name))
            except Exception as e:
                print(f"  Warning creating profile for {email}: {e}")
        
        conn.commit()
        print("✓ Created member profiles")


def seed_events():
    """Create realistic church events"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get an admin user for event creation
        cursor.execute("SELECT id FROM users WHERE role='Admin' LIMIT 1")
        result = cursor.fetchone()
        admin_id = result[0] if result else None
        
        today = datetime.now()
        
        events = [
            {
                'title': 'Culto Matutino - Domingo',
                'start_at': (today + timedelta(days=3)).isoformat() + 'T09:00:00Z',
                'end_at': (today + timedelta(days=3)).isoformat() + 'T10:30:00Z',
                'description': 'Culto de adoração e pregação da palavra',
                'location': 'PIBG - Greenville, SC',
                'is_public': True,
                'created_by': admin_id or 1,
            },
            {
                'title': 'Culto Noturno - Quarta',
                'start_at': (today + timedelta(days=2)).isoformat() + 'T19:00:00Z',
                'end_at': (today + timedelta(days=2)).isoformat() + 'T20:30:00Z',
                'description': 'Estudo bíblico e oração',
                'location': 'PIBG - Greenville, SC',
                'is_public': True,
                'created_by': admin_id or 1,
            },
            {
                'title': 'Ensaio do Louvor',
                'start_at': (today + timedelta(days=1)).isoformat() + 'T18:00:00Z',
                'end_at': (today + timedelta(days=1)).isoformat() + 'T19:30:00Z',
                'description': 'Ensaio para domingo - repertório de louvor',
                'location': 'PIBG Salão - Greenville, SC',
                'is_public': False,
                'created_by': admin_id or 1,
            },
            {
                'title': 'Reunião de Pastores',
                'start_at': (today + timedelta(days=5)).isoformat() + 'T14:00:00Z',
                'end_at': (today + timedelta(days=5)).isoformat() + 'T15:30:00Z',
                'description': 'Reunião mensal do corpo pastoral',
                'location': 'PIBG - Sala de reuniões',
                'is_public': False,
                'created_by': admin_id or 1,
            },
            {
                'title': 'Classe de Novos Convertidos',
                'start_at': (today + timedelta(days=4)).isoformat() + 'T10:00:00Z',
                'end_at': (today + timedelta(days=4)).isoformat() + 'T11:30:00Z',
                'description': 'Aula para recém-convertidos - Fundações da Fé',
                'location': 'PIBG - Sala de aula',
                'is_public': False,
                'created_by': admin_id or 1,
            },
        ]
        
        for event in events:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO events 
                    (title, start_at, end_at, description, location, is_public, created_by, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    event['title'],
                    event['start_at'],
                    event['end_at'],
                    event['description'],
                    event['location'],
                    event['is_public'],
                    event['created_by'],
                ))
            except Exception as e:
                print(f"  Warning creating event {event['title']}: {e}")
        
        conn.commit()
        cursor.execute("SELECT COUNT(*) FROM events")
        count = cursor.fetchone()[0]
        print(f"✓ Created/updated {count} events")


def seed_announcements():
    """Create realistic announcements"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get a staff user for announcements
        cursor.execute("SELECT id FROM users WHERE role IN ('Admin', 'Staff') LIMIT 1")
        poster = cursor.fetchone()
        poster_id = poster[0] if poster else 1
        
        today = datetime.now()
        
        announcements = [
            {
                'title': 'Bem-vindo à PIBG!',
                'body': 'Bem-vindo à Primeira Igreja Brasileira de Greenville. Que alegria tê-lo(a) aqui! Este é um espaço onde você encontrará comunhão, aprendizado e crescimento espiritual.',
                'target_type': 'Global',
                'target_id': None,
                'expires_at': (today + timedelta(days=30)).isoformat(),
                'is_pinned': True,
                'created_by': poster_id,
            },
            {
                'title': 'Cultos da Semana',
                'body': '📅 Domingo 09:00 - Culto Matutino\n🕘 Quarta 19:00 - Estudo Bíblico\n\nVenha participar e trazer um amigo!',
                'target_type': 'Global',
                'target_id': None,
                'expires_at': (today + timedelta(days=7)).isoformat(),
                'is_pinned': True,
                'created_by': poster_id,
            },
            {
                'title': 'Equipe de Louvor - Ensaio Amanhã',
                'body': 'Pessoal, não esquecer do ensaio amanhã às 18h. Vamos preparar um louvor lindo para domingo. Tragam seus instrumentos!',
                'target_type': 'Global',
                'target_id': None,
                'expires_at': (today + timedelta(days=1)).isoformat(),
                'is_pinned': False,
                'created_by': poster_id,
            },
            {
                'title': 'Visita Pastoral - Fique Atento',
                'body': 'Nesta semana faremos visitas pastorais. Fique em casa ou avise se puder receber um pastor.',
                'target_type': 'Global',
                'target_id': None,
                'expires_at': (today + timedelta(days=7)).isoformat(),
                'is_pinned': False,
                'created_by': poster_id,
            },
            {
                'title': 'Oportunidade de Voluntariado',
                'body': 'Procuramos voluntários para ajudar na estrutura do templo. Se você pode contribuir, contacte a liderança.',
                'target_type': 'Global',
                'target_id': None,
                'expires_at': (today + timedelta(days=14)).isoformat(),
                'is_pinned': False,
                'created_by': poster_id,
            },
        ]
        
        for announcement in announcements:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO announcements 
                    (title, body, target_type, target_id, expires_at, is_pinned, created_by, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    announcement['title'],
                    announcement['body'],
                    announcement['target_type'],
                    announcement['target_id'],
                    announcement['expires_at'],
                    announcement['is_pinned'],
                    announcement['created_by'],
                ))
            except Exception as e:
                print(f"  Warning creating announcement {announcement['title']}: {e}")
        
        conn.commit()
        cursor.execute("SELECT COUNT(*) FROM announcements")
        count = cursor.fetchone()[0]
        print(f"✓ Created/updated {count} announcements")


def seed_songs():
    """Create worship repertoire"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        songs = [
            {'title': 'Grande é o Senhor', 'artist': 'Lourceilson Lemos', 'bpm': 80, 'default_key': 'D'},
            {'title': 'Magnificência do Senhor', 'artist': 'Eyshila', 'bpm': 90, 'default_key': 'C'},
            {'title': 'Vencedor', 'artist': 'Thalles Roberto', 'bpm': 85, 'default_key': 'G'},
            {'title': 'Acreditar', 'artist': 'Bruna Karla', 'bpm': 88, 'default_key': 'Bm'},
            {'title': 'Força Eterna', 'artist': 'Allan Gois', 'bpm': 92, 'default_key': 'A'},
            {'title': 'Glória e Honra', 'artist': 'Maria Marçal', 'bpm': 75, 'default_key': 'F'},
            {'title': 'Te Louvarei', 'artist': 'Aline Barros', 'bpm': 95, 'default_key': 'Eb'},
            {'title': 'Canção Eterna', 'artist': 'Midian Lima', 'bpm': 72, 'default_key': 'C'},
        ]
        
        for song in songs:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO songs 
                    (title, artist, bpm, default_key, created_by, created_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'))
                """, (
                    song['title'],
                    song['artist'],
                    song['bpm'],
                    song['default_key'],
                    1,  # Default to first admin user as creator
                ))
            except Exception as e:
                print(f"  Warning creating song {song['title']}: {e}")
        
        conn.commit()
        cursor.execute("SELECT COUNT(*) FROM songs")
        count = cursor.fetchone()[0]
        print(f"✓ Created/updated {count} songs in repertoire")


def main():
    """Run all seed functions"""
    print("\n[*] Populando dados da PIBG...\n")
    
    try:
        seed_users()
        seed_member_profiles()
        seed_events()
        seed_announcements()
        seed_songs()
        
        print("\n[+] Seed data criado com sucesso!\n")
        print("[-] Dados de Teste para Login:")
        print("   Admin: admin@pibg.church / Admin123!@#")
        print("   Staff: staff@pibg.church / Staff123!@#")
        print("   Member: membro1@pibg.church / Member123!@#")
        print("   Visitor: visitante1@pibg.church / Visitor123!@#")
        print("\n")
        
    except Exception as e:
        print(f"\n[-] Erro durante seed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
