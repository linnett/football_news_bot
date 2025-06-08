import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Twitter accounts to monitor
    ACCOUNTS_TO_MONITOR = [
        "David_Ornstein",
        "HandofArsenal", 
        "SamiMokbel_BBC"
    ]
    
    # Keywords to search for
    KEYWORDS = [
        "Arsenal",
        "#AFC",
        "Gunners",
        "Emirates"
    ]
    
    # WhatsApp settings
    WHATSAPP_GROUP_NAME = "Arteta FC"
    
    # Bot settings
    CHECK_INTERVAL = 120  # seconds
    PROCESSED_TWEETS_FILE = "processed_tweets.json"
    
    # Chrome settings
    CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
    # URLs
    TWITTER_URL = "https://twitter.com"
    WHATSAPP_URL = "https://web.whatsapp.com"
    
    # Timeouts
    WHATSAPP_LOAD_TIMEOUT = 30
    
    # Message settings
    MESSAGE_PREFIX = "*AUTOMATED*: "