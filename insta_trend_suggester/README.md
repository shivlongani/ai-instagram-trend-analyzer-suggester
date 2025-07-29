# Instagram Trend Suggester

An AI-powered system that analyzes Instagram profiles and suggests trending content ideas using Google's Gemini API.

## Features

- **Profile Analysis**: Analyzes Instagram bio and post captions to extract user interests, content style, and audience type
- **Trend Matching**: Matches user interests with current trending hashtags using AI
- **Content Suggestions**: Generates personalized Instagram post ideas based on matched trends
- **Automated Data Collection**: Scheduled background jobs to fetch and refresh trending data
- **REST API**: FastAPI-based endpoints for easy integration
- **Database Storage**: PostgreSQL for persistent data storage

## Architecture

```
├── main.py                 # FastAPI application and API endpoints
├── scheduler.py           # APScheduler for automated trend fetching
├── gemini_utils.py        # Gemini API integration and prompts
├── instagram_scraper.py   # Instagram data fetching using instaloader
├── db.py                  # PostgreSQL database operations
├── models.py              # Pydantic models and database schema
├── mock_data/
│   └── trending.json      # Sample trending data for development
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Google Gemini API key

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd insta_trend_suggester
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database:**
   ```sql
   CREATE DATABASE instagram_trends;
   CREATE USER instagram_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE instagram_trends TO instagram_user;
   ```

5. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your actual values:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key
   DATABASE_URL=postgresql://instagram_user:your_password@localhost:5432/instagram_trends
   ```

6. **Run the application:**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

### Key Endpoints

#### POST `/analyze-profile`
Analyzes an Instagram profile and provides personalized trend suggestions.

**Request:**
```json
{
  "username": "instagram_username",
  "num_posts": 10
}
```

**Response:**
```json
{
  "username": "instagram_username",
  "user_interests": {
    "primary_interests": ["fitness", "lifestyle"],
    "content_style": "motivational",
    "preferred_formats": ["photos", "reels"],
    "audience_type": "fitness enthusiasts",
    "tone": "inspirational"
  },
  "matched_trends": [
    {
      "hashtag": "#fitness",
      "match_score": 95,
      "reasoning": "Perfect match for user's fitness-focused content"
    }
  ],
  "post_suggestions": [
    {
      "trend_hashtag": "#fitness",
      "suggestions": [
        "Share your morning workout routine with #fitness",
        "Before/after transformation post using #fitness",
        "Quick home workout tips with #fitness hashtag"
      ]
    }
  ]
}
```

#### GET `/trends`
Returns current trending Instagram data.

#### GET `/suggestions/{username}`
Gets cached suggestions for a previously analyzed username.

#### GET `/health`
Health check endpoint with system status.

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `HOST` | Server host (default: 0.0.0.0) | No |
| `PORT` | Server port (default: 8000) | No |

### Getting API Keys

1. **Gemini API Key:**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the key to your `.env` file

## Database Schema

### trending_data
- `id`: Primary key
- `hashtag`: Trending hashtag
- `caption`: Sample caption
- `post_url`: URL to original post
- `likes`: Number of likes
- `comments`: Number of comments
- `fetched_at`: Timestamp when data was fetched

### matched_trends
- `id`: Primary key
- `username`: Instagram username
- `hashtag`: Matched hashtag
- `match_score`: AI-generated match score (0-100)
- `reasoning`: AI explanation for the match
- `created_at`: Timestamp when match was created

## Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing with Mock Data

The system includes mock trending data in `mock_data/trending.json` for development and testing. This data is automatically used when real Instagram trending data is not available.

### Adding New Trends

You can add new trending items to the mock data file or implement actual Instagram scraping by modifying the `get_trending_hashtags_mock()` method in `instagram_scraper.py`.

## Scheduling

The system automatically:
- Checks for new trending data every 30 minutes
- Only fetches new data if the last fetch was more than 1 hour ago
- Stores trending data in PostgreSQL for persistence

## Error Handling

The API includes comprehensive error handling for:
- Invalid Instagram usernames
- Missing profile data
- API rate limits
- Database connection issues
- Gemini API errors

## Limitations

- Instagram scraping is subject to rate limits and may require login for some profiles
- Gemini API has usage quotas and rate limits
- Current implementation uses mock trending data (can be extended with real scraping)

## Future Enhancements

- Real-time Instagram trending data scraping
- User authentication and profile management
- Content scheduling integration
- Advanced analytics and reporting
- Multi-platform support (TikTok, Twitter, etc.)

## License

This project is for educational and development purposes. Please ensure compliance with Instagram's Terms of Service and API usage policies when using in production.

## Support

For issues and questions, please check the API documentation at `/docs` endpoint or review the error responses from the API endpoints.
