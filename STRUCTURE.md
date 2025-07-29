# 🏗️ Project Structure

```
instagram-trend-suggester/
├── .github/                    # GitHub configuration
│   └── workflows/
│       └── ci.yml             # CI/CD pipeline
├── insta_trend_suggester/     # Main application directory
│   ├── mock_data/             # Sample data for testing
│   │   └── trending.json      # Mock trending hashtags
│   ├── __pycache__/          # Python cache (auto-generated)
│   ├── db.py                 # Database operations and models
│   ├── docker-compose.yml    # Docker services configuration
│   ├── Dockerfile            # Container configuration
│   ├── gemini_utils.py       # Google Gemini AI integration
│   ├── instagram_scraper.py  # Instagram data fetching
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # Pydantic data models
│   ├── requirements.txt     # Python dependencies
│   ├── scheduler.py         # Background job scheduling
│   ├── setup.py            # Package setup configuration
│   ├── start.sh            # Startup script
│   ├── test_setup.py       # Setup verification script
│   ├── .env.example        # Environment variables template
│   ├── .gitignore          # Git ignore rules
│   └── README.md           # Project documentation
├── CONTRIBUTING.md          # Contribution guidelines
├── LICENSE                  # MIT License
├── README.md               # Main project documentation
└── .gitignore             # Global git ignore rules
```

## 📁 Directory Descriptions

### **Root Directory**
- Configuration files for the entire project
- Documentation and licensing information
- GitHub-specific configurations

### **insta_trend_suggester/**
The main application package containing all source code and configurations.

#### **Core Files**
- **`main.py`** - FastAPI application with all API endpoints
- **`models.py`** - Pydantic models for request/response validation
- **`db.py`** - Database connection, operations, and SQLAlchemy models
- **`gemini_utils.py`** - Google Gemini AI integration and prompt management
- **`instagram_scraper.py`** - Instagram profile data fetching utilities
- **`scheduler.py`** - Background job scheduling for trend updates

#### **Configuration Files**
- **`requirements.txt`** - Python package dependencies
- **`.env.example`** - Template for environment variables
- **`Dockerfile`** - Docker container configuration
- **`docker-compose.yml`** - Multi-service Docker setup
- **`start.sh`** - Application startup script

#### **Utilities**
- **`test_setup.py`** - Environment and dependency verification
- **`setup.py`** - Package installation configuration

#### **Data**
- **`mock_data/trending.json`** - Sample trending hashtags for development

## 🔧 Key Components

### **API Layer (`main.py`)**
- FastAPI application setup
- Route definitions and handlers
- Request/response processing
- Error handling and validation

### **AI Integration (`gemini_utils.py`)**
- Google Gemini API client
- Prompt engineering and optimization
- Response parsing and validation
- Retry logic and error handling

### **Data Layer (`db.py`)**
- PostgreSQL database connections
- SQLAlchemy ORM models
- CRUD operations
- Migration support

### **Business Logic (`models.py`)**
- Pydantic data validation models
- Type definitions
- Schema enforcement
- API documentation support

### **External Integration (`instagram_scraper.py`)**
- Instagram profile data fetching
- Rate limiting and error handling
- Data cleaning and processing
- Mock data fallbacks

### **Background Processing (`scheduler.py`)**
- APScheduler job management
- Trend data refresh logic
- Automated maintenance tasks
- System health monitoring

## 🚀 Deployment Structure

### **Development**
```bash
insta_trend_suggester/
├── .env                    # Local environment variables
├── venv/                   # Virtual environment
└── logs/                   # Application logs
```

### **Production (Docker)**
```bash
/app/                       # Container working directory
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
└── ...                     # All source files
```

## 📊 Data Flow

```
User Request → FastAPI → Instagram Scraper → Gemini AI → Database → Response
                ↑                                           ↓
           API Validation                              Background Jobs
```

1. **Request Processing**: FastAPI validates and routes requests
2. **Data Fetching**: Instagram scraper retrieves profile data
3. **AI Analysis**: Gemini processes and analyzes content
4. **Data Storage**: Results saved to PostgreSQL database
5. **Response**: Formatted results returned to user
6. **Background**: Scheduler maintains fresh trending data

## 🔐 Security Considerations

- **Environment Variables**: Sensitive data in `.env` files
- **API Keys**: Secured and not committed to version control
- **Database**: Connection strings and credentials protected
- **Dependencies**: Regular security scanning with GitHub Actions
- **Input Validation**: Pydantic models ensure data integrity
