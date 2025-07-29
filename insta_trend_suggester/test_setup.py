#!/usr/bin/env python3
"""
Simple test script to verify the Instagram Trend Suggester setup
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import fastapi
        print("✓ FastAPI")
    except ImportError:
        print("✗ FastAPI - run: pip install fastapi")
        return False
    
    try:
        import uvicorn
        print("✓ Uvicorn")
    except ImportError:
        print("✗ Uvicorn - run: pip install uvicorn")
        return False
    
    try:
        import sqlalchemy
        print("✓ SQLAlchemy")
    except ImportError:
        print("✗ SQLAlchemy - run: pip install sqlalchemy")
        return False
    
    try:
        import psycopg2
        print("✓ psycopg2")
    except ImportError:
        print("✗ psycopg2 - run: pip install psycopg2-binary")
        return False
    
    try:
        import google.generativeai
        print("✓ Google Generative AI")
    except ImportError:
        print("✗ Google Generative AI - run: pip install google-generativeai")
        return False
    
    try:
        import instaloader
        print("✓ Instaloader")
    except ImportError:
        print("✗ Instaloader - run: pip install instaloader")
        return False
    
    try:
        import apscheduler
        print("✓ APScheduler")
    except ImportError:
        print("✗ APScheduler - run: pip install apscheduler")
        return False
    
    return True

def test_env_file():
    """Test if .env file exists and has required variables"""
    print("\nTesting environment configuration...")
    
    if not os.path.exists('.env'):
        print("✗ .env file not found")
        print("  Please copy .env.example to .env and configure your API keys")
        return False
    
    print("✓ .env file exists")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    db_url = os.getenv('DATABASE_URL')
    
    if not gemini_key or gemini_key == 'your_gemini_api_key_here':
        print("✗ GEMINI_API_KEY not configured")
        return False
    else:
        print("✓ GEMINI_API_KEY configured")
    
    if not db_url or db_url == 'postgresql://postgres:password@localhost:5432/instagram_trends':
        print("⚠ DATABASE_URL using default/example value")
        print("  Make sure PostgreSQL is running with these credentials")
    else:
        print("✓ DATABASE_URL configured")
    
    return True

def test_mock_data():
    """Test if mock data file exists"""
    print("\nTesting mock data...")
    
    mock_file = os.path.join('mock_data', 'trending.json')
    if not os.path.exists(mock_file):
        print("✗ Mock data file not found")
        return False
    
    try:
        import json
        with open(mock_file, 'r') as f:
            data = json.load(f)
        
        if 'trends' in data and len(data['trends']) > 0:
            print(f"✓ Mock data loaded ({len(data['trends'])} trends)")
            return True
        else:
            print("✗ Mock data file is empty or invalid")
            return False
    except Exception as e:
        print(f"✗ Error reading mock data: {e}")
        return False

def test_database_connection():
    """Test database connection (optional)"""
    print("\nTesting database connection...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from db import get_database
        db = get_database()
        
        # Try to create tables
        db.create_tables()
        print("✓ Database connection successful")
        print("✓ Tables created/verified")
        return True
        
    except Exception as e:
        print(f"⚠ Database connection failed: {e}")
        print("  Make sure PostgreSQL is running and credentials are correct")
        return False

def main():
    """Run all tests"""
    print("Instagram Trend Suggester - Setup Verification")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Required tests
    total_tests += 1
    if test_imports():
        tests_passed += 1
    
    total_tests += 1
    if test_env_file():
        tests_passed += 1
    
    total_tests += 1
    if test_mock_data():
        tests_passed += 1
    
    # Optional test
    total_tests += 1
    if test_database_connection():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! You can run: python main.py")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
