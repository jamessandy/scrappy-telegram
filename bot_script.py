import requests
from bs4 import BeautifulSoup
import telegram
from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import html
import os
import pickle

# Environment variables
BOT_TOKEN = '6735157620:AAH18RSB6bmzmudTxxF4bFRB6AzTZs4cdBU'
CHAT_ID = '-1002106850029'
SEEN_POSTS_FILE = 'seen_posts.pkl'

# Load seen posts from a file
if os.path.exists(SEEN_POSTS_FILE):
    with open(SEEN_POSTS_FILE, 'rb') as f:
        seen_posts = pickle.load(f)
else:
    seen_posts = set()

async def scrape_website(url, box_class):
    global seen_posts  # Use the global seen_posts set
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract post information
        posts = soup.find_all('div', class_=box_class)
        new_posts = []
        for post in posts:
            title = post.find('h2').text.strip()
            post_url = post.find('a')['href']
            image_url = post.find('img')['src']

            # Check if the post is new
            if post_url not in seen_posts:
                new_posts.append({'title': title, 'url': post_url, 'image': image_url})
                seen_posts.add(post_url)

        # Send new posts to Telegram
        bot = Bot(token=BOT_TOKEN)
        for post in new_posts:
            escaped_title = html.escape(post['title'])
            escaped_url = html.escape(post['url'])
            escaped_image = html.escape(post['image'])

            message = f"""
- {escaped_image}
- New Airdrop: {escaped_title}
- Action: Claim Rewards

Airdrop Link: [Click here]({escaped_url})

Complete all tasks of the airdrop

Done ✅ Done ✅ Done ✅ Done ✅

Note: We are airdrop hunters and only participate in free legit airdrops.

Follow us on:
- [Facebook](https://www.facebook.com/profile.php?id=61558793561598&mibextid=LQQJ4d)
- [Twitter](https://x.com/newlistedcoins?s=21)
- [Instagram](https://www.instagram.com/newlistedcoins?igsh=ajZsNzIxYmcwMGJk)
"""
            try:
                await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
                print(f"Sent message: {message}")
            except telegram.error.TelegramError as e:
                print(f"Error sending message: {e}")

        # Save the updated seen_posts set to a file
        with open(SEEN_POSTS_FILE, 'wb') as f:
            pickle.dump(seen_posts, f)

    except requests.RequestException as e:
        print(f"Error fetching website: {e}")

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.add_job(lambda: asyncio.run(scrape_website('https://newlistedcoins.com/latest', 'latest-box')), 'interval', hours=1)
scheduler.add_job(lambda: asyncio.run(scrape_website('https://newlistedcoins.com/hot', 'hot-box')), 'interval', hours=1)
scheduler.add_job(lambda: asyncio.run(scrape_website('https://newlistedcoins.com/potential', 'potential-box')), 'interval', hours=1)
scheduler.start()
print("Scheduler started.")

# Direct calls for immediate testing
asyncio.run(scrape_website('https://newlistedcoins.com/latest', 'latest-box'))
asyncio.run(scrape_website('https://newlistedcoins.com/hot', 'hot-box'))
asyncio.run(scrape_website('https://newlistedcoins.com/potential', 'potential-box'))

# Keep the script running
try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    print("Scheduler shutdown.")
