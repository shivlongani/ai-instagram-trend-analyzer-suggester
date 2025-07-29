import instaloader
from typing import List, Tuple, Optional
import time
import random

class InstagramScraper:
    def __init__(self):
        self.loader = instaloader.Instaloader()
        # Configure to be faster for testing
        self.loader.sleep = False  # Disable sleep for faster testing
        self.loader.random_sleep_range = [0.1, 0.3]  # Minimal delays
    
    def get_profile_data(self, username: str, num_posts: int = 3) -> Tuple[str, List[str]]:
        """
        Fetch Instagram profile bio and recent post captions
        
        Args:
            username: Instagram username (without @)
            num_posts: Number of recent posts to fetch captions from (default: 3 for speed)
            
        Returns:
            Tuple of (bio, list_of_captions)
        """
        try:
            # Get profile
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            # Get bio
            bio = profile.biography or ""
            
            # Get recent post captions
            captions = []
            post_count = 0
            
            for post in profile.get_posts():
                if post_count >= num_posts:
                    break
                
                caption = post.caption or ""
                if caption.strip():  # Only add non-empty captions
                    captions.append(caption.strip())
                
                post_count += 1
                
                # Minimal delay for testing
                time.sleep(0.1)
            
            return bio, captions
            
        except instaloader.exceptions.ProfileNotExistsException:
            raise ValueError(f"Instagram profile '{username}' does not exist")
        except instaloader.exceptions.LoginRequiredException:
            raise ValueError("Instagram login required for this operation")
        except Exception as e:
            raise ValueError(f"Error fetching Instagram data: {str(e)}")
    
    def get_trending_hashtags_mock(self) -> List[dict]:
        """
        Mock function to get trending hashtags
        In a real implementation, this would scrape trending data
        """
        # This is a placeholder - you would implement actual trending data fetching here
        # For now, we'll use the mock data from the JSON file
        import json
        import os
        
        mock_file = os.path.join(os.path.dirname(__file__), "mock_data", "trending.json")
        
        try:
            with open(mock_file, 'r') as f:
                mock_data = json.load(f)
                return mock_data.get("trends", [])
        except FileNotFoundError:
            # Return some default trends if mock file doesn't exist
            return [
                {
                    "hashtag": "#fitness",
                    "caption": "Transform your body with these simple exercises!",
                    "post_url": "https://instagram.com/p/mock1",
                    "likes": 15420,
                    "comments": 234
                },
                {
                    "hashtag": "#foodie",
                    "caption": "Best pasta recipe you'll ever try! 🍝",
                    "post_url": "https://instagram.com/p/mock2",
                    "likes": 8765,
                    "comments": 156
                },
                {
                    "hashtag": "#travel",
                    "caption": "Hidden gems in Bali that tourists miss ✈️",
                    "post_url": "https://instagram.com/p/mock3",
                    "likes": 23140,
                    "comments": 445
                }
            ]

# Global scraper instance
instagram_scraper = None

def get_instagram_scraper() -> InstagramScraper:
    """Get Instagram scraper instance"""
    global instagram_scraper
    if instagram_scraper is None:
        instagram_scraper = InstagramScraper()
    return instagram_scraper
