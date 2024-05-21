import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler

# Get environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Function to scrape website for new posts
def scrape_website():
    url = 'https://newlistedcoins.com/latest'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract post information here
        posts = soup.find_all('div', class_='post')  # Adjust selector based on actual HTML structure
        
        new_posts = []
        for post in posts:
            title = post.find('h2').text.strip()
            url = post.find('a')['href']
            # Implement logic to check if the post is new
            # For example, keep a set of seen URLs
            
            if url not in seen_posts:
                new_posts.append({'title': title, 'url': url})
                seen_posts.add(url)
        
        # Send new posts to Telegram
        bot = Bot(token=BOT_TOKEN)
        for post in new_posts:
            message = f"New post: {post['title']}\n{post['url']}"
            bot.send_message(chat_id=CHAT_ID, text=message)

    except requests.RequestException as e:
        print(f"Error fetching website: {e}")
    except telegram.error.TelegramError as e:
        print(f"Error sending message: {e}")

# Set up scheduler to run scrape_website() every hour
scheduler = BackgroundScheduler()
scheduler.add_job(scrape_website, 'interval', hours=1)
scheduler.start()

# Keep track of seen posts to avoid duplicates
seen_posts = set()

# Keep the script running
try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
