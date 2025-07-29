import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, TrendingData, MatchedTrends
from typing import List, Optional
from datetime import datetime, timedelta

class Database:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    def insert_trending_data(self, trends: List[dict]):
        """Insert trending data into database"""
        session = self.SessionLocal()
        try:
            for trend in trends:
                existing = session.query(TrendingData).filter(
                    TrendingData.hashtag == trend['hashtag'],
                    TrendingData.caption == trend['caption']
                ).first()
                
                if not existing:
                    trend_obj = TrendingData(
                        hashtag=trend['hashtag'],
                        caption=trend['caption'],
                        post_url=trend.get('post_url'),
                        likes=trend.get('likes', 0),
                        comments=trend.get('comments', 0),
                        fetched_at=datetime.utcnow()
                    )
                    session.add(trend_obj)
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_latest_trends(self, limit: int = 50) -> List[TrendingData]:
        """Get latest trending data"""
        session = self.SessionLocal()
        try:
            trends = session.query(TrendingData).order_by(
                TrendingData.fetched_at.desc()
            ).limit(limit).all()
            return trends
        finally:
            session.close()
    
    def get_last_fetch_time(self) -> Optional[datetime]:
        """Get the time of last trend fetch"""
        session = self.SessionLocal()
        try:
            last_trend = session.query(TrendingData).order_by(
                TrendingData.fetched_at.desc()
            ).first()
            return last_trend.fetched_at if last_trend else None
        finally:
            session.close()
    
    def should_fetch_trends(self) -> bool:
        """Check if trends should be fetched (last fetch > 1 hour ago)"""
        last_fetch = self.get_last_fetch_time()
        if not last_fetch:
            return True
        
        return datetime.utcnow() - last_fetch > timedelta(hours=1)
    
    def save_matched_trends(self, username: str, matched_trends: List[dict]):
        """Save matched trends for a user"""
        session = self.SessionLocal()
        try:
            # Clear existing matches for this user
            session.query(MatchedTrends).filter(
                MatchedTrends.username == username
            ).delete()
            
            # Insert new matches
            for match in matched_trends:
                match_obj = MatchedTrends(
                    username=username,
                    hashtag=match['hashtag'],
                    match_score=match['match_score'],
                    reasoning=match['reasoning'],
                    created_at=datetime.utcnow()
                )
                session.add(match_obj)
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_matched_trends(self, username: str) -> List[MatchedTrends]:
        """Get matched trends for a user"""
        session = self.SessionLocal()
        try:
            matches = session.query(MatchedTrends).filter(
                MatchedTrends.username == username
            ).order_by(MatchedTrends.match_score.desc()).all()
            return matches
        finally:
            session.close()

# Global database instance
db = None

def get_database() -> Database:
    """Get database instance"""
    global db
    if db is None:
        database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/instagram_trends")
        db = Database(database_url)
        db.create_tables()
    return db
