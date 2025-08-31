#!/usr/bin/env python3
"""
Diagnostic script for the admin interface
"""

import os
import sys
import sqlite3
from pathlib import Path

def check_python_version():
    """Check Python version."""
    print("🐍 Python Version Check")
    print(f"   Version: {sys.version}")
    print(f"   Executable: {sys.executable}")
    
    if sys.version_info < (3, 7):
        print("   ❌ Python 3.7+ required")
        return False
    else:
        print("   ✅ Python version OK")
        return True

def check_flask():
    """Check Flask installation."""
    print("\n🌐 Flask Check")
    try:
        import flask
        print(f"   ✅ Flask version: {flask.__version__}")
        return True
    except ImportError as e:
        print(f"   ❌ Flask not installed: {e}")
        print("   💡 Install with: pip install flask==3.0.0")
        return False

def check_database():
    """Check database status."""
    print("\n🗄️ Database Check")
    
    # Check possible database paths
    possible_paths = [
        "data/faqs.db",
        "backend/data/faqs.db",
        "../data/faqs.db",
        "./data/faqs.db"
    ]
    
    db_found = False
    for path in possible_paths:
        if os.path.exists(path):
            print(f"   ✅ Database found at: {os.path.abspath(path)}")
            db_found = True
            
            # Check database integrity
            try:
                conn = sqlite3.connect(path)
                cursor = conn.execute("SELECT COUNT(*) FROM faqs")
                count = cursor.fetchone()[0]
                print(f"   ✅ Database has {count} FAQs")
                
                # Check table structure
                cursor = conn.execute("PRAGMA table_info(faqs)")
                columns = cursor.fetchall()
                print(f"   ✅ Table has {len(columns)} columns")
                
                conn.close()
            except Exception as e:
                print(f"   ❌ Database error: {e}")
            
            break
    
    if not db_found:
        print("   ⚠️ No database file found")
        print("   💡 Will be created when admin interface starts")
    
    return db_found

def check_json_file():
    """Check JSON file status."""
    print("\n📄 JSON File Check")
    
    possible_paths = [
        "data/custom_faq.json",
        "backend/data/custom_faq.json",
        "../data/custom_faq.json"
    ]
    
    json_found = False
    for path in possible_paths:
        if os.path.exists(path):
            print(f"   ✅ JSON file found at: {os.path.abspath(path)}")
            
            # Check JSON content
            try:
                import json
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                faqs = data.get('faqs', [])
                print(f"   ✅ JSON has {len(faqs)} FAQs")
                json_found = True
            except Exception as e:
                print(f"   ❌ JSON error: {e}")
            
            break
    
    if not json_found:
        print("   ⚠️ No JSON file found")
    
    return json_found

def check_ports():
    """Check port availability."""
    print("\n🔌 Port Check")
    
    import socket
    
    ports_to_check = [5000, 5001, 8080, 3001, 8000]
    
    for port in ports_to_check:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"   ⚠️ Port {port} is busy")
            else:
                print(f"   ✅ Port {port} is available")
        except Exception as e:
            print(f"   ❌ Could not check port {port}: {e}")

def check_file_permissions():
    """Check file permissions."""
    print("\n🔐 File Permissions Check")
    
    current_dir = Path.cwd()
    print(f"   Current directory: {current_dir}")
    
    # Check if we can write to current directory
    try:
        test_file = current_dir / "test_write.tmp"
        test_file.write_text("test")
        test_file.unlink()
        print("   ✅ Can write to current directory")
    except Exception as e:
        print(f"   ❌ Cannot write to current directory: {e}")

def main():
    """Run all diagnostics."""
    print("🔍 FAQ Admin Interface Diagnostics")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Flask Installation", check_flask),
        ("Database Status", check_database),
        ("JSON File Status", check_json_file),
        ("Port Availability", check_ports),
        ("File Permissions", check_file_permissions)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ {name} check failed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! The admin interface should work.")
        print("\n🚀 To start the admin interface:")
        print("   python admin_interface_fixed.py")
        print("   or")
        print("   start_admin_fixed.bat")
    else:
        print("\n⚠️ Some checks failed. Please fix the issues above.")
        print("\n💡 Common solutions:")
        print("   1. Install Flask: pip install flask==3.0.0")
        print("   2. Make sure you're in the backend directory")
        print("   3. Check if ports are available")
        print("   4. Ensure you have write permissions")

if __name__ == "__main__":
    main()























