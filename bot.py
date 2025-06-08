import time
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from config import Config
from twitter_scraper import TwitterScraper
from whatsapp_sender import WhatsAppSender

class TwitterWhatsAppBot:
    def __init__(self):
        self.processed_tweets = self.load_processed_tweets()
        self.driver = None
        self.twitter_scraper = None
        self.whatsapp_sender = None
    
    def load_processed_tweets(self):
        """Load previously processed tweets to avoid duplicates"""
        if os.path.exists(Config.PROCESSED_TWEETS_FILE):
            try:
                with open(Config.PROCESSED_TWEETS_FILE, 'r') as f:
                    content = f.read().strip()
                    if content:  # Check if file has content
                        return set(json.loads(content))
                    else:
                        print("⚠️ processed_tweets.json is empty, starting fresh")
                        return set()
            except (json.JSONDecodeError, Exception) as e:
                print(f"⚠️ Could not load processed_tweets.json: {e}")
                print("Starting with fresh tweet tracking...")
                return set()
        return set()
    
    def save_processed_tweets(self):
        """Save processed tweets to file"""
        with open(Config.PROCESSED_TWEETS_FILE, 'w') as f:
            json.dump(list(self.processed_tweets), f)
    
    def setup_driver(self):
        """Initialize Chrome driver"""
        print("🔧 Setting up Chrome driver...")
        chrome_options = self._setup_chrome_options()
        
        try:
            print("🔧 Installing/updating ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            print("🔧 Starting Chrome with webdriver-manager...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ Chrome driver started successfully")
        except Exception as e:
            print(f"❌ Could not start Chrome: {e}")
            print("💡 Troubleshooting steps:")
            print("   1. Close all Chrome windows")
            print("   2. Update Chrome to latest version")
            print("   3. Run: pip install --upgrade selenium webdriver-manager")
            raise
        
        print("🔧 Configuring driver...")
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Test that driver is working
        print("🔧 Testing driver...")
        try:
            current_url = self.driver.current_url
            print(f"✅ Driver working, current URL: {current_url}")
        except Exception as e:
            print(f"❌ Driver not responding: {e}")
            raise
        
        # Initialize scrapers
        print("🔧 Initializing scrapers...")
        self.twitter_scraper = TwitterScraper(self.driver)
        self.whatsapp_sender = WhatsAppSender(self.driver)
        print("✅ Driver setup complete")
    
    def _setup_chrome_options(self):
        """Set up Chrome options for the webdriver"""
        options = Options()
        
        # Essential options only
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Profile directory
        options.add_argument("--user-data-dir=./chrome_profile")
        
        return options
    
    def check_and_recover_session(self):
        """Check if browser session is still valid and recover if needed"""
        try:
            self.driver.current_url
            return True
        except Exception as e:
            print(f"⚠️ Browser session lost: {str(e)}")
            print("🔄 Attempting to recover session...")
            
            try:
                if self.driver:
                    self.driver.quit()
            except:
                pass
            
            # Setup new driver
            self.setup_driver()
            
            # Re-login to services
            print("🔄 Re-establishing connections...")
            self.twitter_scraper.login()
            self.whatsapp_sender.setup()
            
            return True
    
    def run_monitoring_cycle(self):
        """Run one cycle of monitoring all accounts"""
        print(f"\n🔍 Starting monitoring cycle at {datetime.now().strftime('%H:%M:%S')}")
        
        # Check if session is still valid
        if not self.check_and_recover_session():
            print("❌ Could not recover browser session")
            return
        
        for username in Config.ACCOUNTS_TO_MONITOR:
            try:
                # Switch to Twitter tab
                self.driver.switch_to.window(self.driver.window_handles[0])
                
                new_tweets = self.twitter_scraper.check_account_tweets(username)
                
                for tweet in new_tweets:
                    # Check if already processed
                    if tweet['id'] in self.processed_tweets:
                        continue
                    
                    print(f"📱 Found new tweet from @{username}!")
                    
                    # Switch to WhatsApp tab
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    
                    self.whatsapp_sender.send_tweet(tweet)
                    self.processed_tweets.add(tweet['id'])
                    time.sleep(5)  # Delay between messages
                
                if not new_tweets:
                    print(f"✅ No new tweets from @{username}")
                
                time.sleep(5)  # Delay between accounts
                
            except Exception as e:
                error_msg = str(e)
                if "invalid session id" in error_msg or "chrome not reachable" in error_msg:
                    print(f"⚠️ Session lost while checking @{username}, will recover on next cycle")
                    break
                else:
                    print(f"❌ Error checking @{username}: {error_msg}")
        
        # Save processed tweets
        self.save_processed_tweets()
        print(f"✅ Monitoring cycle completed at {datetime.now().strftime('%H:%M:%S')}")
    
    def start_monitoring(self):
        """Start the main monitoring loop"""
        print("🚀 Starting Arsenal Twitter to WhatsApp Bot...")
        
        try:
            self.setup_driver()
            self.twitter_scraper.login()
            self.whatsapp_sender.setup()
            
            print(f"\n✅ Setup complete! Starting monitoring every {Config.CHECK_INTERVAL} seconds...")
            print("Press Ctrl+C to stop the bot\n")
            
            while True:
                try:
                    self.run_monitoring_cycle()
                    print(f"😴 Waiting {Config.CHECK_INTERVAL} seconds until next check...\n")
                    time.sleep(Config.CHECK_INTERVAL)
                    
                except KeyboardInterrupt:
                    print("\n👋 Stopping bot...")
                    break
                except Exception as e:
                    print(f"❌ Error in monitoring cycle: {str(e)}")
                    print("⏳ Waiting 60 seconds before retrying...")
                    time.sleep(60)
        
        finally:
            if self.driver:
                self.driver.quit()
            print("🛑 Bot stopped.")