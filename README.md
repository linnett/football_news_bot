# Twitter to WhatsApp Bot

A Python bot that monitors specific Twitter accounts for tweets containing keywords and automatically forwards them to a WhatsApp group.

## 🚀 Features

- **Twitter Monitoring**: Monitors multiple Twitter accounts for new tweets
- **Keyword Filtering**: Only forwards tweets containing specified keywords
- **WhatsApp Integration**: Automatically sends matching tweets to a WhatsApp group
- **Duplicate Prevention**: Tracks processed tweets to avoid sending duplicates
- **Session Recovery**: Automatically recovers from browser crashes or network issues
- **Retweet Filtering**: Skips retweets and only processes original content

## 📋 Prerequisites

- **Python 3.8+** installed on your system
- **Google Chrome** browser installed
- **Twitter account** (for manual login)
- **WhatsApp** account with access to WhatsApp Web
- **A WhatsApp group** where you want to send the tweets

## 🛠 Installation

1. **Clone or download** this repository:
```bash
git clone <repository-url>
cd twitter-whatsapp-bot
```

2. **Create a virtual environment** (recommended):
```bash
`python -m venv venv` / `python3 -m venv venv`

# Activate it:
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Edit the `config.py` file to customize the bot for your needs:

```python
class Config:
    # Twitter accounts to monitor (without @ symbol)
    ACCOUNTS_TO_MONITOR = [
        "David_Ornstein",      # Replace with accounts you want to monitor
        "HandofArsenal", 
        "SamiMokbel_BBC"
    ]
    
    # Keywords to search for in tweets
    KEYWORDS = [
        "Arsenal",             # Replace with your keywords
        "#AFC",
        "Gunners",
        "Emirates"
    ]
    
    # WhatsApp group name (must match exactly!)
    WHATSAPP_GROUP_NAME = "Arteta FC"  # Replace with your group name
    
    # How often to check for new tweets (in seconds)
    CHECK_INTERVAL = 120  # 120 = 2 minutes
```

### Important Configuration Notes:

- **Twitter accounts**: Use the username without the @ symbol
- **WhatsApp group name**: Must match the group name exactly (case-sensitive)
- **Check interval**: Start with 300 seconds (5 minutes) to avoid rate limiting
- **Chrome path**: Update `CHROME_PATH` if Chrome is installed in a different location

## 🚀 Usage

1. **Run the bot**:
```bash
caffeinate -i python3 main.py
```

2. **Follow the setup prompts**:
   - Chrome will open automatically
   - **Log into Twitter** when prompted
   - **Scan the QR code** for WhatsApp Web when prompted
   - The bot will start monitoring automatically

3. **Monitor the console** for logs and status updates

4. **Stop the bot** by pressing `Ctrl+C`

## 📁 Project Structure

```
twitter-whatsapp-bot/
├── config.py              # Configuration settings
├── twitter_scraper.py     # Twitter scraping functionality
├── whatsapp_sender.py     # WhatsApp messaging functionality
├── bot.py                 # Main bot orchestration
├── main.py               # Entry point
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── chrome_profile/      # Chrome user data (auto-created)
└── processed_tweets.json # Processed tweet IDs (auto-created)
```

## 🔧 Customization

### Adding New Accounts
Edit `ACCOUNTS_TO_MONITOR` in `config.py`:
```python
ACCOUNTS_TO_MONITOR = [
    "BBCBreaking",
    "SkySportsNews",
    "YourFavoriteAccount"
]
```

### Changing Keywords
Edit `KEYWORDS` in `config.py`:
```python
KEYWORDS = [
    "football",
    "transfer",
    "Manchester United",
    "#MUFC"
]
```

### Special Account Rules
The bot has special handling for certain accounts:
- **HandofArsenal**: All original tweets are forwarded (regardless of keywords)
- **Other accounts**: Only tweets containing specified keywords are forwarded

To modify this behavior, edit the `_should_include_tweet` method in `twitter_scraper.py`.

## 🐛 Troubleshooting

### Common Issues

**Chrome won't start:**
- Ensure Chrome is installed in the default location
- Update `CHROME_PATH` in `config.py` if needed
- Try running as administrator

**Can't find elements:**
- Twitter/WhatsApp may have changed their interface
- The bot may need updates to element selectors

**Rate limiting:**
- Increase `CHECK_INTERVAL` to 300+ seconds
- Reduce the number of monitored accounts

**Session expires:**
- The bot will attempt automatic recovery
- If it fails repeatedly, restart the bot

**WhatsApp group not found:**
- Ensure `WHATSAPP_GROUP_NAME` matches exactly
- Check that the group is visible in your chat list

### Debug Mode

To run without actually sending messages (for testing):
1. Add a `DEBUG = True` flag to `config.py`
2. Modify the bot to skip sending when in debug mode

### Logs and Screenshots

- The bot saves error screenshots as `whatsapp_error.png`
- Console output shows detailed status information
- Check `processed_tweets.json` to see which tweets have been processed

---

**Disclaimer**: This bot is provided as-is for educational purposes. Users are responsible for ensuring compliance with all applicable terms of service and regulations.