# AI Instagram Trend Analyzer 🚀

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Gemini AI](https://img.shields.io/badge/Gemini_AI-Powered-orange.svg)](https://ai.google.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)](https://postgresql.org)
[![CI](https://github.com/YOUR_GITHUB_USERNAME/ai-instagram-trend-analyzer-suggester/workflows/CI/badge.svg)](https://github.com/YOUR_GITHUB_USERNAME/ai-instagram-trend-analyzer-suggester/actions)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **AI-powered Instagram content recommendation system** that analyzes profiles and suggests trending content ideas using Google's Gemini API.

## 🌟 Features

- **🤖 AI Profile Analysis**: Uses Gemini AI to analyze Instagram bios and post captions
- **📈 Trend Matching**: Smart matching of user interests with trending hashtags
- **💡 Content Suggestions**: Generates personalized post ideas based on matched trends
- **⏰ Automated Scheduling**: Background jobs to refresh trending data
- **🗄️ Data Persistence**: PostgreSQL database for storing analysis results
- **🚀 REST API**: FastAPI-based endpoints for easy integration
- **📱 Real-time Analysis**: Fast response times with optimized AI calls

## 🏗️ Architecture

```
├── main.py                 # FastAPI application and endpoints
├── gemini_utils.py        # Gemini AI integration and prompts
├── instagram_scraper.py   # Instagram data fetching
├── scheduler.py           # Background job scheduling
├── db.py                  # Database operations
├── models.py              # Data models and schemas
├── mock_data/            # Sample trending data
└── requirements.txt      # Dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL or Supabase account
- Google Gemini API key ([Get one here](https://ai.google.dev))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_GITHUB_USERNAME/ai-instagram-trend-analyzer-suggester.git
   cd ai-instagram-trend-analyzer-suggester/insta_trend_suggester
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

Visit `http://localhost:8000/docs` for interactive API documentation.

## 🔧 Configuration

Create a `.env` file with the following variables:

```env
# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration  
DATABASE_URL=postgresql://username:password@host:port/database

# Optional: API Configuration
HOST=0.0.0.0
PORT=8000
```

## 📚 API Endpoints

### **POST** `/analyze-profile`
Analyzes an Instagram profile and provides trending content suggestions.

**Request:**
```json
{
  "username": "instagram_username",
  "num_posts": 3
}
```

**Response:**
```json
{
  "username": "instagram_username",
  "user_interests": {
    "primary_interests": ["technology", "travel"],
    "content_style": "casual",
    "preferred_formats": ["photos", "reels"],
    "audience_type": "Gen Z/Millennials",
    "tone": "personal"
  },
  "matched_trends": [
    {
      "hashtag": "#technology",
      "match_score": 90,
      "reasoning": "Perfect match for tech-focused content"
    }
  ],
  "post_suggestions": [
    {
      "trend_hashtag": "#technology",
      "suggestions": [
        "Showcase latest tech gadgets with unboxing video",
        "Share your coding setup and productivity tips"
      ]
    }
  ]
}
```

### **GET** `/trends`
Returns current trending Instagram hashtags and data.

### **GET** `/suggestions/{username}`
Retrieves cached suggestions for a previously analyzed profile.

### **POST** `/demo-analysis`
Demo endpoint using sample data to test the AI analysis.

## 🎯 Demo

Try the live demo endpoints:

```bash
# Test with sample data
curl -X POST "http://localhost:8000/demo-analysis"

# Check system health
curl -X GET "http://localhost:8000/health"

# View trending hashtags
curl -X GET "http://localhost:8000/trends"
```

## 🧠 How It Works

1. **Profile Analysis**: Fetches Instagram bio and recent post captions
2. **AI Processing**: Gemini AI analyzes content style, interests, and audience
3. **Trend Matching**: Compares user profile with current trending hashtags
4. **Content Generation**: Creates personalized post suggestions for each matched trend
5. **Data Storage**: Saves results in PostgreSQL for future retrieval

## 🔮 AI-Powered Features

- **Smart Interest Detection**: Identifies user interests from minimal text data
- **Contextual Trend Matching**: Uses semantic analysis for better hashtag matching
- **Personalized Content Ideas**: Generates suggestions that match user's unique style
- **Intelligent Scoring**: Provides match confidence scores with reasoning

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **AI/ML**: Google Gemini 1.5 Flash
- **Database**: PostgreSQL / Supabase
- **Scheduling**: APScheduler
- **Data Scraping**: Instaloader
- **Deployment**: Docker support included

## 📈 Performance

- **Response Time**: ~6 seconds average
- **AI Accuracy**: High-quality content suggestions
- **Scalability**: Background job processing
- **Reliability**: Robust error handling and retries

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your_key_here"
export DATABASE_URL="your_database_url"

# Run the application
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

**Issues**: [Report bugs or request features](https://github.com/YOUR_GITHUB_USERNAME/ai-instagram-trend-analyzer-suggester/issues)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **Demo**: `http://localhost:8000/demo-analysis`

## 👨‍💻 Author

**[Your Name]**
- GitHub: [@YOUR_GITHUB_USERNAME](https://github.com/YOUR_GITHUB_USERNAME)
- LinkedIn: [Your LinkedIn Profile](https://linkedin.com/in/yourprofile)

## 🙏 Acknowledgments

- Google Gemini AI for powerful language understanding
- FastAPI for the excellent web framework
- Supabase for reliable database hosting
- Instagram community for inspiration

---

⭐ **Star this repository if you found it useful!**
