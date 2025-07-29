#!/usr/bin/env python3
"""
Setup script for the Instagram Trend Suggester project.
This script helps you configure the project and test basic functionality.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def create_env_file():
    """Create a .env file with required environment variables."""
    env_file = project_dir / ".env"
    
    if env_file.exists():
        print("✓ .env file already exists")
        return
    
    print("Creating .env file...")
    
    # Get user input for environment variables
    gemini_api_key = input("Enter your Gemini API Key (get it from https://makersuite.google.com/app/apikey): ")
    
    print("\nDatabase connection options:")
    print("1. Local PostgreSQL (recommended for development)")
    print("2. Cloud PostgreSQL (Supabase, AWS RDS, etc.)")
    print("3. Use SQLite for testing (simpler setup)")
    
    db_choice = input("Choose database option (1-3): ").strip()
    
    if db_choice == "3":
        db_url = "sqlite:///./instagram_trends.db"
    elif db_choice == "1":
        db_user = input("PostgreSQL username (default: postgres): ").strip() or "postgres"
        db_password = input("PostgreSQL password: ")
        db_host = input("PostgreSQL host (default: localhost): ").strip() or "localhost"
        db_port = input("PostgreSQL port (default: 5432): ").strip() or "5432"
        db_name = input("Database name (default: instagram_trends): ").strip() or "instagram_trends"
        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        db_url = input("Enter your PostgreSQL connection URL: ")
    
    env_content = f"""# Gemini API Configuration
GEMINI_API_KEY={gemini_api_key}

# Database Configuration
DATABASE_URL={db_url}

# Optional: Instagram credentials (for real scraping instead of mock data)
# INSTAGRAM_USERNAME=your_username
# INSTAGRAM_PASSWORD=your_password

# API Configuration
API_HOST=localhost
API_PORT=8000
DEBUG=true
"""
    
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print(f"✓ Created .env file at {env_file}")
    print("⚠️  Make sure to keep your .env file secure and never commit it to version control!")

async def test_database_connection():
    """Test database connection."""
    try:
        from db import get_database, init_database
        
        print("Testing database connection...")
        
        # Initialize database
        await init_database()
        print("✓ Database initialized successfully")
        
        # Test connection
        db = await get_database()
        await db.execute("SELECT 1")
        print("✓ Database connection test successful")
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your DATABASE_URL in .env file")
        print("3. Ensure the database exists")
        print("4. Verify your credentials")
        return False
    
    return True

def test_gemini_connection():
    """Test Gemini API connection."""
    try:
        from gemini_utils import GeminiClient
        
        print("Testing Gemini API connection...")
        
        # Load API key from environment
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("✗ GEMINI_API_KEY not found in environment")
            return False
        
        client = GeminiClient(api_key)
        # Test with a simple profile analysis
        result = client.analyze_profile(
            bio="Test bio for API testing",
            post_captions=["Test caption for API testing"]
        )
        
        if result:
            print("✓ Gemini API connection test successful")
            return True
        else:
            print("✗ Gemini API returned empty result")
            return False
            
    except Exception as e:
        print(f"✗ Gemini API connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your GEMINI_API_KEY in .env file")
        print("2. Ensure you have internet connection")
        print("3. Verify your API key is valid")
        return False

async def main():
    """Main setup function."""
    print("🚀 Instagram Trend Suggester Setup")
    print("=" * 40)
    
    # Step 1: Create .env file
    create_env_file()
    print()
    
    # Step 2: Test database connection
    db_success = await test_database_connection()
    print()
    
    # Step 3: Test Gemini API connection
    gemini_success = test_gemini_connection()
    print()
    
    # Summary
    print("Setup Summary:")
    print("=" * 40)
    print(f"✓ Environment file created")
    print(f"{'✓' if db_success else '✗'} Database connection")
    print(f"{'✓' if gemini_success else '✗'} Gemini API connection")
    
    if db_success and gemini_success:
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run the application: python main.py")
        print("2. Open http://localhost:8000/docs to see the API documentation")
        print("3. Try the /analyze-profile endpoint with an Instagram username")
    else:
        print("\n⚠️  Some components need attention. Please fix the issues above.")
    
    print(f"\nProject files are located in: {project_dir}")

if __name__ == "__main__":
    asyncio.run(main())
