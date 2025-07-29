from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Database Models
class TrendingData(Base):
    __tablename__ = "trending_data"
    
    id = Column(Integer, primary_key=True, index=True)
    hashtag = Column(String(255), nullable=False)
    caption = Column(Text, nullable=False)
    post_url = Column(String(255), nullable=True)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    fetched_at = Column(DateTime, default=datetime.utcnow)

class MatchedTrends(Base):
    __tablename__ = "matched_trends"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    hashtag = Column(String(255), nullable=False)
    match_score = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models
class ProfileAnalysisRequest(BaseModel):
    username: str
    num_posts: Optional[int] = 3  # Reduced default for faster processing

class UserInterests(BaseModel):
    primary_interests: List[str]
    content_style: str
    preferred_formats: List[str]
    audience_type: str
    tone: str

class TrendItem(BaseModel):
    hashtag: str
    caption: str
    post_url: Optional[str] = None
    likes: int = 0
    comments: int = 0
    fetched_at: datetime

class MatchedTrend(BaseModel):
    hashtag: str
    match_score: float
    reasoning: str

class PostSuggestion(BaseModel):
    trend_hashtag: str
    suggestions: List[str]

class ProfileAnalysisResponse(BaseModel):
    username: str
    user_interests: UserInterests
    matched_trends: List[MatchedTrend]
    post_suggestions: List[PostSuggestion]

class TrendsResponse(BaseModel):
    trends: List[TrendItem]
    total_count: int

class SuggestionsResponse(BaseModel):
    matched_trends: List[MatchedTrend]
    post_suggestions: List[PostSuggestion]
