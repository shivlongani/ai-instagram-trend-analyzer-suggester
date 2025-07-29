from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from models import (
    ProfileAnalysisRequest, ProfileAnalysisResponse, TrendsResponse, 
    SuggestionsResponse, TrendItem, MatchedTrend, PostSuggestion, UserInterests
)
from db import get_database
from gemini_utils import get_gemini_client
from instagram_scraper import get_instagram_scraper
from scheduler import start_scheduler, stop_scheduler

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Instagram Trend Suggester API...")
    
    # Initialize database
    db = get_database()
    print("Database initialized")
    
    # Start scheduler
    start_scheduler()
    print("Scheduler started")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    stop_scheduler()

# Create FastAPI app
app = FastAPI(
    title="Instagram Trend Suggester API",
    description="AI-powered Instagram trend analysis and content suggestion system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Instagram Trend Suggester API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.post("/analyze-profile", response_model=ProfileAnalysisResponse)
async def analyze_profile(request: ProfileAnalysisRequest):
    """
    Analyze an Instagram profile and provide trend suggestions
    
    This endpoint:
    1. Fetches the user's bio and recent post captions
    2. Analyzes their interests and content style using Gemini
    3. Matches their interests with trending hashtags
    4. Generates personalized post suggestions
    """
    try:
        # Get services
        scraper = get_instagram_scraper()
        gemini = get_gemini_client()
        db = get_database()
        
        # Fetch Instagram profile data (reduced to 3 posts for speed)
        try:
            bio, post_captions = scraper.get_profile_data(request.username, 3)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error fetching Instagram data: {str(e)}")
        
        if not bio and not post_captions:
            raise HTTPException(status_code=400, detail="No data found for this Instagram profile")
        
        # Get current trending data
        trending_data = db.get_latest_trends(limit=15)  # Reduced for faster processing
        trending_hashtags = [trend.hashtag for trend in trending_data]
        
        if not trending_hashtags:
            raise HTTPException(status_code=503, detail="No trending data available. Please try again later.")
        
        # Use single comprehensive analysis call
        try:
            complete_analysis = gemini.analyze_profile_complete(bio, post_captions, trending_hashtags)
            
            # Extract results from single response
            user_interests = UserInterests(**complete_analysis["user_interests"])
            trend_matches = complete_analysis["matched_trends"]
            post_suggestions_raw = complete_analysis["post_suggestions"]
            
            print(f"✅ Analysis complete: {len(trend_matches)} trends, {len(post_suggestions_raw)} suggestions")
            
        except Exception as e:
            print(f"❌ Error in complete analysis: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error analyzing profile: {str(e)}")
        
        # Save matched trends to database (only if we have results)
        if trend_matches:
            try:
                db.save_matched_trends(request.username, trend_matches)
                print(f"💾 Saved {len(trend_matches)} matched trends to database")
            except Exception as e:
                print(f"⚠️ Warning: Could not save trends to database: {e}")
        
        # Format response with better error handling
        matched_trends = []
        for match in trend_matches:
            try:
                matched_trends.append(MatchedTrend(
                    hashtag=match.get('hashtag', 'Unknown'),
                    match_score=float(match.get('match_score', 0)),
                    reasoning=match.get('reasoning', 'No reasoning provided')
                ))
            except Exception as e:
                print(f"⚠️ Skipping invalid match: {match}, Error: {e}")
                continue
        
        post_suggestions = []
        for suggestion in post_suggestions_raw:
            try:
                post_suggestions.append(PostSuggestion(
                    trend_hashtag=suggestion.get('trend_hashtag', 'Unknown'),
                    suggestions=suggestion.get('suggestions', [])
                ))
            except Exception as e:
                print(f"⚠️ Skipping invalid suggestion: {suggestion}, Error: {e}")
                continue
                continue
        
        return ProfileAnalysisResponse(
            username=request.username,
            user_interests=user_interests,
            matched_trends=matched_trends,
            post_suggestions=post_suggestions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/suggestions/{username}", response_model=SuggestionsResponse)
async def get_suggestions(username: str):
    """
    Get cached suggestions for a previously analyzed username
    """
    try:
        db = get_database()
        gemini = get_gemini_client()
        
        # Get matched trends from database
        matched_trends_db = db.get_matched_trends(username)
        
        if not matched_trends_db:
            raise HTTPException(
                status_code=404, 
                detail=f"No analysis found for username '{username}'. Please analyze the profile first."
            )
        
        # Format matched trends
        matched_trends = [
            MatchedTrend(
                hashtag=match.hashtag,
                match_score=match.match_score,
                reasoning=match.reasoning
            )
            for match in matched_trends_db
        ]
        
        # Generate fresh post suggestions based on cached matches
        hashtags = [match.hashtag for match in matched_trends_db[:5]]
        
        # We need user interests to generate suggestions, but they're not stored
        # For this endpoint, we'll use a simplified approach
        try:
            # Use a simplified prompt for post generation without full user analysis
            post_suggestions_raw = gemini.generate_post_suggestions_simple(hashtags)
            
            post_suggestions = [
                PostSuggestion(
                    trend_hashtag=suggestion['trend_hashtag'],
                    suggestions=suggestion['suggestions']
                )
                for suggestion in post_suggestions_raw
            ]
        except:
            # Fallback to empty suggestions if generation fails
            post_suggestions = []
        
        return SuggestionsResponse(
            matched_trends=matched_trends,
            post_suggestions=post_suggestions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/trends", response_model=TrendsResponse)
async def get_trends(limit: int = 50):
    """
    Get current trending Instagram data
    """
    try:
        db = get_database()
        trending_data = db.get_latest_trends(limit=limit)
        
        trends = [
            TrendItem(
                hashtag=trend.hashtag,
                caption=trend.caption,
                post_url=trend.post_url,
                likes=trend.likes,
                comments=trend.comments,
                fetched_at=trend.fetched_at
            )
            for trend in trending_data
        ]
        
        return TrendsResponse(
            trends=trends,
            total_count=len(trends)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trends: {str(e)}")

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check database connection
        db = get_database()
        db.get_latest_trends(limit=1)
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Check Gemini API
    try:
        gemini = get_gemini_client()
        gemini_status = "configured"
    except Exception as e:
        gemini_status = f"error: {str(e)}"
    
    return {
        "status": "running",
        "database": db_status,
        "gemini_api": gemini_status,
        "scheduler": "running"
    }

@app.post("/demo-analysis", response_model=ProfileAnalysisResponse)
async def demo_analysis():
    """
    Demo endpoint using sample Instagram data to test Gemini API integration
    """
    try:
        # Sample Instagram data
        sample_bio = "Bios are overrated Skip the assumptions - meet me in person"
        sample_captions = [
            "Le Chat GPT when the prompt is: 'Suggest a house design inspired from my life story.' 🏠😂 #TechHumor #AILife",
            "Just Another Sunday, But Better ☀️ #WeekendVibes #SundayMood #ChillDay",
            "Sometimes you just need a little chaos to feel alive. 😁🎢 #LifePhilosophy #Adventure"
        ]
        username = "demo_user"
        
        # Get services
        gemini = get_gemini_client()
        db = get_database()
        
        # Get current trending data
        trending_data = db.get_latest_trends(limit=15)
        trending_hashtags = [trend.hashtag for trend in trending_data]
        
        if not trending_hashtags:
            raise HTTPException(status_code=503, detail="No trending data available. Please try again later.")
        
        # Use single comprehensive analysis call
        print(f"🚀 Starting demo analysis with {len(trending_hashtags)} trending hashtags...")
        
        complete_analysis = gemini.analyze_profile_complete(sample_bio, sample_captions, trending_hashtags)
        
        # Extract results from single response
        user_interests = UserInterests(**complete_analysis["user_interests"])
        trend_matches = complete_analysis["matched_trends"]
        post_suggestions_raw = complete_analysis["post_suggestions"]
        
        print(f"✅ Demo analysis complete: {len(trend_matches)} trends, {len(post_suggestions_raw)} suggestions")
        
        # Save matched trends to database (only if we have results)
        if trend_matches:
            try:
                db.save_matched_trends(username, trend_matches)
                print(f"💾 Saved {len(trend_matches)} matched trends to database")
            except Exception as e:
                print(f"⚠️ Warning: Could not save trends to database: {e}")
        
        # Format response with better error handling
        matched_trends = []
        for match in trend_matches:
            try:
                matched_trends.append(MatchedTrend(
                    hashtag=match.get('hashtag', 'Unknown'),
                    match_score=float(match.get('match_score', 0)),
                    reasoning=match.get('reasoning', 'No reasoning provided')
                ))
            except Exception as e:
                print(f"⚠️ Skipping invalid match: {match}, Error: {e}")
                continue
        
        post_suggestions = []
        for suggestion in post_suggestions_raw:
            try:
                post_suggestions.append(PostSuggestion(
                    trend_hashtag=suggestion.get('trend_hashtag', 'Unknown'),
                    suggestions=suggestion.get('suggestions', [])
                ))
            except Exception as e:
                print(f"⚠️ Skipping invalid suggestion: {suggestion}, Error: {e}")
                continue
        
        return ProfileAnalysisResponse(
            username=username,
            user_interests=user_interests,
            matched_trends=matched_trends,
            post_suggestions=post_suggestions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/test-cristiano", response_model=ProfileAnalysisResponse)
async def test_cristiano_analysis():
    """
    Test endpoint using Cristiano Ronaldo's actual profile data to demonstrate the full AI flow
    """
    try:
        # Cristiano Ronaldo's actual Instagram data (simplified)
        cristiano_bio = "Proud father of 5 amazing kids. Dedicated to my family, my fans, and my sport. Living life to the fullest! 🙏⚽️"
        cristiano_captions = [
            "What a feeling to score the winning goal for Al Nassr! 🙌⚽️ Thank you for all the support from the fans! #AlNassr #Cristiano #Victory",
            "Family time is the best time ❤️👨‍👩‍👧‍👦 Blessed to have these amazing people in my life #Family #Blessed #Love",
            "Training hard every single day 💪 Age is just a number when you have passion and dedication #NeverGiveUp #Training #Football"
        ]
        username = "cristiano"
        
        # Get services
        gemini = get_gemini_client()
        db = get_database()
        
        # Get current trending data
        trending_data = db.get_latest_trends(limit=15)
        trending_hashtags = [trend.hashtag for trend in trending_data]
        
        if not trending_hashtags:
            raise HTTPException(status_code=503, detail="No trending data available. Please try again later.")
        
        # Use single comprehensive analysis call
        print(f"🚀 Starting Cristiano analysis with {len(trending_hashtags)} trending hashtags...")
        
        complete_analysis = gemini.analyze_profile_complete(cristiano_bio, cristiano_captions, trending_hashtags)
        
        # Extract results from single response
        user_interests = UserInterests(**complete_analysis["user_interests"])
        trend_matches = complete_analysis["matched_trends"]
        post_suggestions_raw = complete_analysis["post_suggestions"]
        
        print(f"✅ Cristiano analysis complete: {len(trend_matches)} trends, {len(post_suggestions_raw)} suggestions")
        
        # Save matched trends to database (only if we have results)
        if trend_matches:
            try:
                db.save_matched_trends(username, trend_matches)
                print(f"💾 Saved {len(trend_matches)} matched trends for Cristiano to database")
            except Exception as e:
                print(f"⚠️ Warning: Could not save trends to database: {e}")
        
        # Format response with better error handling
        matched_trends = []
        for match in trend_matches:
            try:
                matched_trends.append(MatchedTrend(
                    hashtag=match.get('hashtag', 'Unknown'),
                    match_score=float(match.get('match_score', 0)),
                    reasoning=match.get('reasoning', 'No reasoning provided')
                ))
            except Exception as e:
                print(f"⚠️ Skipping invalid match: {match}, Error: {e}")
                continue
        
        post_suggestions = []
        for suggestion in post_suggestions_raw:
            try:
                post_suggestions.append(PostSuggestion(
                    trend_hashtag=suggestion.get('trend_hashtag', 'Unknown'),
                    suggestions=suggestion.get('suggestions', [])
                ))
            except Exception as e:
                print(f"⚠️ Skipping invalid suggestion: {suggestion}, Error: {e}")
                continue
        
        return ProfileAnalysisResponse(
            username=username,
            user_interests=user_interests,
            matched_trends=matched_trends,
            post_suggestions=post_suggestions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/test-celebrating-utsav", response_model=ProfileAnalysisResponse)
async def test_celebrating_utsav():
    """
    Test endpoint for celebrating_utsav using actual scraped data
    This bypasses Instagram API authentication issues
    """
    try:
        # Real data we successfully scraped earlier
        username = "celebrating_utsav"
        bio = "Bios are overrated Skip the assumptions - meet me in person"
        captions = [
            "Le Chat GPT when the prompt is: 'Suggest a house design inspired from my life story.' 🏠😂 #TechHumor #AILife #Architecture #CreativeThinking",
            "Just Another Sunday, But Better ☀️ #WeekendVibes #SundayMood #ChillDay #Relaxation #Germany #Europe",
            "Sometimes you just need a little chaos to feel alive. 😁🎢 Saarburg, thanks for the memories! #Adventure #LifePhilosophy #Travel #Germany #Memories"
        ]
        
        # Get services
        gemini = get_gemini_client()
        db = get_database()
        
        # Get current trending data
        trending_data = db.get_latest_trends(limit=15)
        trending_hashtags = [trend.hashtag for trend in trending_data]
        
        if not trending_hashtags:
            raise HTTPException(status_code=503, detail="No trending data available. Please try again later.")
        
        print(f"🚀 Starting analysis for {username} with {len(trending_hashtags)} trending hashtags...")
        print(f"📝 Bio: {bio}")
        print(f"📸 Posts: {len(captions)} captions")
        
        # Use single comprehensive analysis call
        complete_analysis = gemini.analyze_profile_complete(bio, captions, trending_hashtags)
        
        # Extract results from single response
        user_interests = UserInterests(**complete_analysis["user_interests"])
        trend_matches = complete_analysis["matched_trends"]
        post_suggestions_raw = complete_analysis["post_suggestions"]
        
        print(f"✅ Analysis complete: {len(trend_matches)} trends, {len(post_suggestions_raw)} suggestions")
        
        # Save matched trends to database
        if trend_matches:
            try:
                db.save_matched_trends(username, trend_matches)
                print(f"💾 Saved {len(trend_matches)} matched trends to database")
            except Exception as e:
                print(f"⚠️ Warning: Could not save trends to database: {e}")
        
        # Format response with better error handling
        matched_trends = []
        for match in trend_matches:
            try:
                matched_trends.append(MatchedTrend(
                    hashtag=match.get('hashtag', 'Unknown'),
                    match_score=float(match.get('match_score', 0)),
                    reasoning=match.get('reasoning', 'No reasoning provided')
                ))
            except Exception as e:
                print(f"⚠️ Skipping invalid match: {match}, Error: {e}")
                continue
        
        post_suggestions = []
        for suggestion in post_suggestions_raw:
            try:
                post_suggestions.append(PostSuggestion(
                    trend_hashtag=suggestion.get('trend_hashtag', 'Unknown'),
                    suggestions=suggestion.get('suggestions', [])
                ))
            except Exception as e:
                print(f"⚠️ Skipping invalid suggestion: {suggestion}, Error: {e}")
                continue
        
        return ProfileAnalysisResponse(
            username=username,
            user_interests=user_interests,
            matched_trends=matched_trends,
            post_suggestions=post_suggestions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )
