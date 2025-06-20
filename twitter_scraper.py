import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import Config

class TwitterScraper:
    def __init__(self, driver):
        self.driver = driver
    
    def login(self):
        """Navigate to Twitter - manual login required on first run"""
        print("📱 Opening X.com...")
        login_url = f"{Config.TWITTER_URL}/login"
        print(f"🔗 Navigating to: {login_url}")
        
        try:
            self.driver.get(login_url)
            print("✅ Successfully navigated to X.com login page")
        except Exception as e:
            print(f"❌ Failed to navigate to X.com: {e}")
            raise
        
        # Wait for manual login if needed
        input("Please log in to X.com manually and press Enter when done...")
        
        # Wait for home page to load
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="primaryColumn"]'))
            )
            print("✅ Successfully logged into X.com!")
        except TimeoutException:
            print("❌ Failed to detect X.com login. Please ensure you're logged in.")
            print("💡 Make sure you can see your timeline/home feed")
    
    def check_account_tweets(self, username):
        """Check recent tweets from a specific account"""
        print(f"Checking tweets from @{username}...")
        
        # Navigate to user profile
        self.driver.get(f"https://x.com/{username}")
        
        try:
            # Wait for tweets to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweet"]'))
            )
            
            # Get recent tweets
            tweets = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')[:5]
            
            new_arsenal_tweets = []
            
            for tweet in tweets:
                try:
                    # Check if this is a retweet
                    is_retweet = self._is_retweet(tweet)
                    
                    if is_retweet:
                        print(f"⏭️ Skipping retweet from @{username}")
                        continue
                    
                    # Get tweet text and link
                    tweet_text_element = tweet.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                    tweet_text = tweet_text_element.text
                    
                    tweet_link_element = tweet.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]')
                    tweet_link = tweet_link_element.get_attribute('href')
                    
                    # Create unique tweet ID
                    tweet_id = tweet_link.split('/')[-1] if tweet_link else hash(tweet_text)
                    
                    # Check if should include tweet
                    should_include = self._should_include_tweet(username, tweet_text)
                    
                    if should_include:
                        new_arsenal_tweets.append({
                            'id': tweet_id,
                            'text': tweet_text,
                            'link': tweet_link,
                            'username': username
                        })
                        print(f"📝 Found relevant tweet from @{username}")
                
                except (NoSuchElementException, Exception) as e:
                    continue
            
            return new_arsenal_tweets
            
        except TimeoutException:
            print(f"Could not load tweets for @{username}")
            return []
    
    def _is_retweet(self, tweet):
        """Check if this is a retweet"""
        is_retweet = False
        
        # Method 1: Look for retweet indicators
        try:
            retweet_indicators = tweet.find_elements(By.CSS_SELECTOR, '[data-testid="socialContext"]')
            for indicator in retweet_indicators:
                if "retweeted" in indicator.text.lower() or "reposted" in indicator.text.lower():
                    is_retweet = True
                    break
        except:
            pass
        
        # Method 2: Check if tweet text starts with "RT @"
        try:
            tweet_text_element = tweet.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
            tweet_text = tweet_text_element.text
            if tweet_text.startswith("RT @"):
                is_retweet = True
        except:
            pass
        
        return is_retweet
    
    def _contains_keywords(self, text):
        """
        Check if text contains related keywords with precise matching.
        Prevents false positives like #AFC matching #AFCB.
        """
        text_lower = text.lower()
        
        for keyword in Config.KEYWORDS:
            keyword_lower = keyword.lower()
            
            if keyword.startswith('#'):
                # For hashtags, ensure it's followed by space, punctuation, or end of string
                # This prevents #AFC from matching #AFCB
                pattern = re.escape(keyword_lower) + r'(?=\s|[^\w]|$)'
                if re.search(pattern, text_lower):
                    return True
            else:
                # For regular words, use word boundaries
                pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                if re.search(pattern, text_lower):
                    return True
        
        return False
    
    def _should_include_tweet(self, username, tweet_text):
        """Determine if tweet should be included based on filtering rules"""
        if username == "HandofArsenal":
            # Include ALL original tweets from HandofArsenal
            return True
        else:
            # For other accounts, check for Arsenal keywords with precise matching
            return self._contains_keywords(tweet_text)