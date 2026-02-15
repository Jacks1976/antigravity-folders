#!/usr/bin/env python3
"""Verify database contents"""
import sqlite3

conn = sqlite3.connect('church_app.db')
cursor = conn.cursor()

print('='*60)
print('     Database Verification - PIBG Church Application')
print('='*60)

cursor.execute('SELECT COUNT(*) FROM users WHERE deleted_at IS NULL')
users = cursor.fetchone()[0]
print(f'\n✓ Total Users: {users}')

cursor.execute('SELECT COUNT(*) FROM users WHERE status = "Active" AND deleted_at IS NULL')
active = cursor.fetchone()[0]
print(f'  • Active Users: {active}')

cursor.execute('SELECT COUNT(*) FROM users WHERE status = "Pending" AND deleted_at IS NULL')
pending = cursor.fetchone()[0]
print(f'  • Pending Users: {pending}')

cursor.execute('SELECT COUNT(*) FROM events WHERE deleted_at IS NULL')
events = cursor.fetchone()[0]
print(f'\n✓ Events: {events}')

cursor.execute('SELECT COUNT(*) FROM announcements WHERE deleted_at IS NULL')
announcements = cursor.fetchone()[0]
print(f'✓ Announcements: {announcements}')

cursor.execute('SELECT COUNT(*) FROM songs WHERE deleted_at IS NULL')
songs = cursor.fetchone()[0]
print(f'✓ Worship Songs: {songs}')

cursor.execute('SELECT COUNT(*) FROM member_profiles')
profiles = cursor.fetchone()[0]
print(f'✓ Member Profiles: {profiles}')

print('\n' + '='*60)
print('Test Credentials (All Active)')
print('='*60)

cursor.execute('''
    SELECT email, u.role, p.full_name 
    FROM users u
    LEFT JOIN member_profiles p ON u.id = p.user_id
    WHERE u.status = "Active" AND u.deleted_at IS NULL
    ORDER BY u.role DESC, u.email ASC
    LIMIT 10
''')

print('\nEmail                          | Role        | Name')
print('-' * 60)
for email, role, name in cursor.fetchall():
    name_display = name if name else '(no profile)'
    print(f'{email:30} | {role:11} | {name_display}')

print('\n' + '='*60)
print('Sample Events')
print('='*60)

cursor.execute('''
    SELECT title, start_at, description
    FROM events
    WHERE deleted_at IS NULL
    ORDER BY start_at ASC
    LIMIT 5
''')

print('\nTitle                          | Start Date         | Description')
print('-' * 60)
for title, start, desc in cursor.fetchall():
    desc_short = (desc[:20] + '...') if desc and len(desc) > 20 else (desc or '')
    print(f'{title:30} | {start:18} | {desc_short}')

print('\n' + '='*60)
print('Sample Announcements')
print('='*60)

cursor.execute('''
    SELECT title, body
    FROM announcements
    WHERE deleted_at IS NULL
    ORDER BY created_at DESC
    LIMIT 5
''')

print('\nTitle                          | Body')
print('-' * 60)
for title, body in cursor.fetchall():
    body_short = (body[:25] + '...') if body and len(body) > 25 else (body or '')
    print(f'{title:30} | {body_short}')

print('\n' + '='*60)
print('✅ Database Ready for Testing!')
print('='*60)
print('\nStart the application with:')
print('  1. Backend:  python -m uvicorn app.main:app --reload')
print('  2. Frontend: npm run dev (from web folder)')
print('  3. Browser:  http://localhost:3000')
print('\nUse any credential above to log in.')
print('='*60 + '\n')

conn.close()
