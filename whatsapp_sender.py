import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from config import Config

class WhatsAppSender:
    def __init__(self, driver):
        self.driver = driver
    
    def setup(self):
        """Open WhatsApp Web in a new tab"""
        print("Opening WhatsApp Web...")
        self.driver.execute_script(f"window.open('{Config.WHATSAPP_URL}', '_blank');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        
        # Wait for manual WhatsApp Web login
        input("Please scan QR code to login to WhatsApp Web and press Enter when done...")
        
        print("🔍 Checking if WhatsApp is loaded...")
        
        # Wait for WhatsApp to load with better feedback
        max_attempts = Config.WHATSAPP_LOAD_TIMEOUT // 2
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Check for multiple possible indicators that WhatsApp is loaded
                if (self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="chat-list"]') or 
                    self.driver.find_elements(By.CSS_SELECTOR, '.app-wrapper-web') or
                    self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="chats-list"]')):
                    print("✅ Successfully logged into WhatsApp Web!")
                    return
                
                attempt += 1
                print(f"⏳ Loading WhatsApp... (attempt {attempt}/{max_attempts})")
                time.sleep(2)
                
            except Exception as e:
                attempt += 1
                print(f"⏳ Waiting for WhatsApp to load... (attempt {attempt}/{max_attempts})")
                time.sleep(2)
        
        print("⚠️ WhatsApp may not be fully loaded, but continuing anyway...")
    
    def send_tweet(self, tweet_data):
        """Send tweet information to WhatsApp group"""
        print(f"Sending tweet from @{tweet_data['username']} to WhatsApp...")
        
        try:
            # Clean the tweet text
            clean_tweet_text = self._clean_text_for_chrome(tweet_data['text'])
            
            # Wait a bit for WhatsApp to be stable
            time.sleep(3)
            
            # Find and click the group
            if not self._find_and_click_group():
                return
            
            # Send the message
            self._send_message(clean_tweet_text, tweet_data['link'])
            
        except Exception as e:
            print(f"❌ Failed to send to WhatsApp: {str(e)}")
            # Take a screenshot for debugging
            try:
                self.driver.save_screenshot("whatsapp_error.png")
                print("📸 Screenshot saved as 'whatsapp_error.png' for debugging")
            except:
                pass
    
    def _find_and_click_group(self):
        """Find and click the WhatsApp group"""
        try:
            # Look for the group name in the chat list
            group_element = self.driver.find_element(
                By.XPATH, f"//span[contains(text(), '{Config.WHATSAPP_GROUP_NAME}')]"
            )
            # Click on the parent container that's clickable
            clickable_parent = group_element.find_element(
                By.XPATH, "./ancestor::div[@role='listitem' or contains(@class, 'chat')]"
            )
            clickable_parent.click()
            print(f"✅ Found and clicked {Config.WHATSAPP_GROUP_NAME} group")
            time.sleep(2)
            return True
        except:
            print(f"❌ Could not find {Config.WHATSAPP_GROUP_NAME} group in chat list")
            return False
    
    def _send_message(self, clean_text, link):
        """Send the actual message"""
        try:
            # Find message input using a more general approach
            message_box = self.driver.find_element(
                By.XPATH, "//div[@contenteditable='true' and @data-tab='10']"
            )
            
            # Click to focus
            message_box.click()
            time.sleep(1)
            
            # Clear any existing content
            message_box.clear()
            time.sleep(0.5)
            
            # Send as one continuous line with pipe separator
            single_line_message = f"{Config.MESSAGE_PREFIX}{clean_text} | {link}"
            
            # Type the entire message at once
            message_box.send_keys(single_line_message)
            
            # Add space for preview
            message_box.send_keys(" ")
            
            # Wait for link preview
            print("⏳ Waiting for link preview to load...")
            time.sleep(5)
            
            # Send the message
            message_box.send_keys(Keys.ENTER)
            
            print(f"✅ Tweet sent to {Config.WHATSAPP_GROUP_NAME} group!")
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Could not send message: {str(e)}")
            # Try alternative approach
            self._send_message_alternative(clean_text, link)
    
    def _send_message_alternative(self, clean_text, link):
        """Alternative method to send message"""
        try:
            message_box = self.driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
            message_box.click()
            time.sleep(1)
            
            # Type header with tweet content
            message_box.send_keys(f"{Config.MESSAGE_PREFIX}{clean_text}")
            # Use Shift+Enter for line breaks
            message_box.send_keys(Keys.SHIFT + Keys.ENTER)
            message_box.send_keys(Keys.SHIFT + Keys.ENTER)
            # Type URL and space
            message_box.send_keys(link)
            message_box.send_keys(" ")
            print("⏳ Waiting for link preview to load...")
            time.sleep(5)  # Wait longer for preview
            message_box.send_keys(Keys.ENTER)  # Send message
            
            print(f"✅ Tweet sent via alternative method!")
        except:
            print("❌ All message sending methods failed")
    
    def _clean_text_for_chrome(self, text):
        """Clean text to remove characters that ChromeDriver can't handle"""
        # Remove emojis and other non-BMP characters
        cleaned = ''.join(char for char in text if ord(char) <= 0xFFFF)
        
        # Replace common problematic characters
        replacements = {
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '–': '-',
            '—': '-',
            '…': '...',
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        # Fix the Twitter copy-paste formatting issue
        cleaned = re.sub(r'\n\s*@', ' @', cleaned)
        cleaned = re.sub(r'@(\w+)\s*\n', r'@\1 ', cleaned)
        
        # Remove any remaining line breaks and normalize spaces
        cleaned = re.sub(r'\n+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Remove any remaining problematic characters
        cleaned = re.sub(r'[^\x00-\x7F]', '', cleaned)
        
        return cleaned