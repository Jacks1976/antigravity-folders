#!/usr/bin/env python3
"""
Complete database initialization script
Runs all schema setup in correct order
"""
import subprocess
import sys
import os

def run_script(script_name):
    """Run a Python script and report status"""
    filepath = os.path.join('execution', f'{script_name}.py')
    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print('='*60)
    
    try:
        result = subprocess.run(
            [sys.executable, filepath],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {script_name} completed successfully")
            return True
        else:
            print(f"❌ {script_name} failed with code {result.returncode}")
            return False
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

if __name__ == '__main__':
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "Complete Database Setup - PIBG Church Application".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    scripts = [
        'setup_database',  # Core auth tables
        'update_schema_members',  # Member profiles
        'update_schema_announcements',  # Announcements
        'update_schema_events',  # Events
        'update_schema_worship_files',  # Worship files
        'update_schema_worship_repertoire',  # Songs
        'update_schema_worship_schedule',  # Schedule
        'seed_pibg_data',  # Populate with test data
    ]
    
    results = {}
    for script in scripts:
        results[script] = run_script(script)
    
    print("\n" + "="*60)
    print("SUMMARY".center(60))
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for script, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {script:<40}")
    
    print("="*60)
    print(f"Result: {passed}/{total} scripts completed")
    
    if passed == total:
        print("\n🎉 Database initialization complete!")
        print("\nNext steps:")
        print("  1. Start backend: python -m uvicorn app.main:app --reload")
        print("  2. Start frontend: npm run dev (from web folder)")
        print("  3. Open: http://localhost:3000")
    else:
        print("\n⚠️  Some scripts failed. Check output above.")
        sys.exit(1)
