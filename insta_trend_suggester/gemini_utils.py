import google.generativeai as genai
import json
import os
import time
import asyncio
import concurrent.futures
from typing import List, Dict, Any
from models import UserInterests

class GeminiClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Use the most reliable model with proper configuration
        self.model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,  # More deterministic
                max_output_tokens=1000,  # Limit response size
                top_p=0.8,
                top_k=10
            )
        )
    
    def _make_request_with_retry(self, prompt: str, expected_format: str = "json", max_retries: int = 3) -> str:
        """Make a request to Gemini with retry logic and format validation"""
        for attempt in range(max_retries):
            try:
                print(f"🤖 Gemini API attempt {attempt + 1}/{max_retries}...")
                
                # Make the request with optimized settings
                response = self.model.generate_content(prompt)
                response_text = response.text.strip()
                
                # Clean response text (remove markdown formatting if present)
                if response_text.startswith('```json'):
                    response_text = response_text.replace('```json', '').replace('```', '').strip()
                elif response_text.startswith('```'):
                    response_text = response_text.replace('```', '').strip()
                
                print(f"📝 Raw response: {response_text[:150]}...")
                
                # Validate JSON format if expected
                if expected_format == "json":
                    try:
                        json.loads(response_text)
                        print("✅ Valid JSON format received")
                        return response_text
                    except json.JSONDecodeError as json_error:
                        print(f"❌ JSON validation failed: {json_error}")
                        print(f"Response was: {response_text[:200]}...")
                        if attempt < max_retries - 1:
                            print("🔄 Retrying with corrected prompt...")
                            time.sleep(2)
                            continue
                        else:
                            raise ValueError(f"Failed to get valid JSON after {max_retries} attempts")
                
                return response_text
                
            except Exception as e:
                print(f"❌ Gemini API attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 3 + (attempt * 2)  # 3, 5, 7 seconds
                    print(f"⏳ Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    raise e
    
    def _process_requests_parallel(self, prompts: List[str]) -> List[str]:
        """Process multiple Gemini requests in parallel using ThreadPoolExecutor"""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all requests
            future_to_prompt = {
                executor.submit(self._make_request_with_retry, prompt): prompt 
                for prompt in prompts
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_prompt, timeout=30):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Request failed: {e}")
                    results.append("")  # Empty result for failed requests
        
        return results
    
    def analyze_profile_fast(self, bio: str, post_captions: List[str], trending_hashtags: List[str]) -> tuple:
        """Fast parallel analysis of profile, trend matching, and post suggestions"""
        
        # Limit to only 3 most recent captions for speed
        captions = post_captions[:3]
        captions_text = "\n".join([f"- {caption[:100]}..." if len(caption) > 100 else f"- {caption}" for caption in captions])
        
        # Create 3 optimized prompts for parallel processing
        prompts = [
            # Profile analysis prompt (shorter)
            f"""Analyze this Instagram profile quickly:
Bio: {bio[:200]}
Recent posts: {captions_text}

Return ONLY this JSON format:
{{"primary_interests": ["list", "of", "interests"], "content_style": "style", "preferred_formats": ["formats"], "audience_type": "audience", "tone": "tone"}}""",
            
            # Trend matching prompt (top 10 trends only)
            f"""Match these trends to a user interested in: {bio[:100]}
Trends: {', '.join(trending_hashtags[:10])}

Return ONLY this JSON array with top 5 matches:
[{{"hashtag": "#tag", "match_score": 85, "reasoning": "brief reason"}}]""",
            
            # Post suggestions prompt (simplified)
            f"""Generate 2 quick post ideas for each hashtag: {', '.join(trending_hashtags[:3])}
Based on: {bio[:100]}

Return ONLY this JSON:
[{{"trend_hashtag": "#tag", "suggestions": ["idea1", "idea2"]}}]"""
        ]
        
        # Process all 3 requests in parallel
        try:
            results = self._process_requests_parallel(prompts)
            
            # Parse results
            user_interests = None
            matched_trends = []
            post_suggestions = []
            
            # Parse profile analysis
            if results[0]:
                try:
                    profile_data = json.loads(results[0])
                    user_interests = UserInterests(**profile_data)
                except:
                    pass
            
            # Parse trend matches
            if results[1]:
                try:
                    matched_trends = json.loads(results[1])
                except:
                    pass
            
            # Parse post suggestions
            if results[2]:
                try:
                    post_suggestions = json.loads(results[2])
                except:
                    pass
            
            return user_interests, matched_trends, post_suggestions
            
        except Exception as e:
            print(f"Fast analysis failed: {e}")
            return None, [], []
    
    def analyze_profile_complete(self, bio: str, post_captions: List[str], trending_hashtags: List[str]) -> dict:
        """Complete profile analysis with ALL results in ONE API call"""
        
        # Limit data for faster processing
        captions_text = "\n".join([f"- {caption[:100]}" for caption in post_captions[:3]])
        hashtags_text = ", ".join(trending_hashtags[:10])
        
        prompt = f"""Analyze this Instagram profile and return ONE complete JSON with ALL analysis:

Bio: {bio[:200]}
Recent Posts:
{captions_text}
Available Hashtags: {hashtags_text}

Return ONLY this EXACT JSON structure:
{{
    "user_interests": {{
        "primary_interests": ["interest1", "interest2"],
        "content_style": "casual/professional/artistic",
        "preferred_formats": ["photos", "reels"],
        "audience_type": "target audience",
        "tone": "personal/inspirational/educational"
    }},
    "matched_trends": [
        {{
            "hashtag": "#hashtag1",
            "match_score": 85,
            "reasoning": "why it matches"
        }}
    ],
    "post_suggestions": [
        {{
            "trend_hashtag": "#hashtag1",
            "suggestions": ["idea 1", "idea 2"]
        }}
    ]
}}

IMPORTANT: Return ONLY the JSON above, no other text."""
        
        try:
            response_text = self._make_request_with_retry(prompt, expected_format="json")
            result = json.loads(response_text)
            
            # Ensure all required fields exist
            if "user_interests" not in result:
                result["user_interests"] = {
                    "primary_interests": ["lifestyle"],
                    "content_style": "casual",
                    "preferred_formats": ["photos"],
                    "audience_type": "general",
                    "tone": "personal"
                }
            
            if "matched_trends" not in result:
                result["matched_trends"] = []
            
            if "post_suggestions" not in result:
                result["post_suggestions"] = []
            
            print(f"✅ Complete analysis successful: {len(result['matched_trends'])} trends, {len(result['post_suggestions'])} suggestions")
            return result
            
        except Exception as e:
            print(f"❌ Error in complete analysis: {e}")
            return {
                "user_interests": {
                    "primary_interests": ["lifestyle"],
                    "content_style": "casual",
                    "preferred_formats": ["photos"],
                    "audience_type": "general",
                    "tone": "personal"
                },
                "matched_trends": [],
                "post_suggestions": []
            }
            
            return UserInterests(
                primary_interests=interests,
                content_style="casual",
                preferred_formats=["photos", "reels"],
                audience_type="general",
                tone="personal"
            )
    
    def match_trends_to_interests(self, user_interests: UserInterests, trending_hashtags: List[str]) -> List[Dict[str, Any]]:
        """Match trending hashtags to user interests with enhanced format validation"""
        
        # Limit to top 8 hashtags for faster processing
        limited_hashtags = trending_hashtags[:8]
        interests_text = ", ".join(user_interests.primary_interests)
        hashtags_text = ", ".join(limited_hashtags)
        
        prompt = f"""Match hashtags to user profile:

User: {interests_text}, {user_interests.content_style} style, {user_interests.audience_type} audience

Hashtags: {hashtags_text}

EXPECTED OUTPUT (copy this exact format):
[
    {{"hashtag": "#fitness", "match_score": 85, "reasoning": "matches health interest"}},
    {{"hashtag": "#lifestyle", "match_score": 70, "reasoning": "fits casual style"}}
]

Return ONLY the JSON array above with scores >60. No extra text."""
        
        try:
            response_text = self._make_request_with_retry(prompt, expected_format="json")
            matches = json.loads(response_text)
            # Validate structure
            if isinstance(matches, list) and all(isinstance(m, dict) and 'hashtag' in m and 'match_score' in m for m in matches):
                return matches
            else:
                print("Invalid match structure returned")
                return []
        except Exception as e:
            print(f"Error matching trends: {e}")
            return []
    
    def generate_post_suggestions(self, user_interests: UserInterests, matched_hashtags: List[str]) -> List[Dict[str, Any]]:
        """Generate creative post ideas with enhanced format validation"""
        
        # Limit to top 3 hashtags for faster processing
        top_hashtags = matched_hashtags[:3]
        hashtags_text = ", ".join(top_hashtags)
        
        prompt = f"""Generate post ideas for user profile:

Style: {user_interests.content_style}
Tone: {user_interests.tone}
Hashtags: {hashtags_text}

EXPECTED OUTPUT (copy this exact format):
[
    {{"trend_hashtag": "#fitness", "suggestions": ["Post idea 1 here", "Post idea 2 here"]}},
    {{"trend_hashtag": "#lifestyle", "suggestions": ["Post idea 1 here", "Post idea 2 here"]}}
]

Return ONLY the JSON array above. No extra text."""
        
        try:
            response_text = self._make_request_with_retry(prompt, expected_format="json")
            suggestions = json.loads(response_text)
            # Validate structure
            if isinstance(suggestions, list) and all(isinstance(s, dict) and 'trend_hashtag' in s and 'suggestions' in s for s in suggestions):
                return suggestions
            else:
                print("Invalid suggestions structure returned")
                return []
        except Exception as e:
            print(f"Error generating post suggestions: {e}")
            return []
    
    def generate_post_suggestions_simple(self, hashtags: List[str]) -> List[Dict[str, Any]]:
        """Generate simple post suggestions for hashtags without full user analysis"""
        
        hashtags_text = ", ".join(hashtags[:5])
        
        prompt = f"""
        Generate 2-3 creative Instagram post ideas for each of these trending hashtags: {hashtags_text}
        
        Provide a JSON array in this format:
        [
            {{
                "trend_hashtag": "#hashtag",
                "suggestions": [
                    "Creative post idea 1 that incorporates the hashtag naturally",
                    "Creative post idea 2 with specific content suggestions",
                    "Creative post idea 3 with engagement hooks"
                ]
            }}
        ]
        
        Make each suggestion engaging and trendy.
        Provide only the JSON array, no additional text.
        """
        
        try:
            response_text = self._make_request_with_retry(prompt)
            suggestions = json.loads(response_text)
            return suggestions
        except Exception as e:
            print(f"Error generating simple post suggestions: {e}")
            return []

# Global client instance
gemini_client = None

def get_gemini_client() -> GeminiClient:
    """Get Gemini client instance"""
    global gemini_client
    if gemini_client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        gemini_client = GeminiClient(api_key)
    return gemini_client
