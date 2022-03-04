import os
import sys
import feedparser
from sql import db
from time import sleep, time
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from apscheduler.schedulers.background import BackgroundScheduler


try:
    api_id = int(os.environ["API_ID"])   # Get it from my.telegram.org
    api_hash = os.environ["API_HASH"]   # Get it from my.telegram.org
    feed_urls = list(set(i for i in os.environ["FEED_URLS"].split("|")))  # RSS Feed URL of the site.
    bot_token = os.environ["BOT_TOKEN"]   # Get it by creating a bot on https://t.me/botfather
    log_channel = int(os.environ["LOG_CHANNEL"])   # Telegram Channel ID where the bot is added and have write permission. You can use group ID too.
    log_channel2 = int(os.environ["LOG_CHANNEL2"])
    check_interval = int(os.environ.get("INTERVAL", 10))   # Check Interval in seconds.  
    max_instances = int(os.environ.get("MAX_INSTANCES", 3))   # Max parallel instance to be used.
    mirr_cmd = os.environ.get("MIRROR_CMD", "/qbmir4")    #if you have changed default cmd of mirror bot, replace this.
    # leech_cmd = os.environ.get("LEECH_CMD", "/leech")
except Exception as e:
    print(e)
    print("One or more variables missing or have error. Exiting !")
    sys.exit(1)


for feed_url in feed_urls:
    if db.get_link(feed_url) == None:
        db.update_link(feed_url, "*")


app = Client(":memory:", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

def create_feed_checker(feed_url):
    def check_feed():
        FEED = feedparser.parse(feed_url)
        if len(FEED.entries) == 0:
            return
        entry = FEED.entries[0]
        if entry.id != db.get_link(feed_url).link:
            # ↓ Edit this message as your needs.
            if "eztv.re" in entry.link:   
                message = f"{mirr_cmd} {entry.torrent_magneturi}"   
                message3 = f"**📂 FileName:** `{entry.torrent_filename}`\n\n**📝 Published:** {entry.published}\n\n**📥 DL Link:** `{entry.torrent_magneturi}`"    
            elif "yts.mx" in entry.link:
                message = f"{mirr_cmd} {entry.links[1]['href']}"   
                message3 = f"**📂 FileName:** `{entry.title}`\n\n**📝 Published:** {entry.published}\n\n**📥 DL Link:** `{entry.links[1]['href']}`\n\n#YTSMX #YTS" 
               # message
            elif "rarbg" in entry.link:
                message = f"{mirr_cmd} {entry.link}"
                filename = {entry.title}
                filename.replace(".", " ")
                message3 = f"**📂 FileName:** `{filename}`\n\n**📝 Published:** {entry.published}\n\n**📥 DL Link:** `{entry.link}`\n\n#RARBG" 
               # message
            elif "watercache" in entry.link:
                message = f"{mirr_cmd} {entry.link}"   
                message3 = f"**📂 FileName:** `{entry.title}`\n\n**📝 Published:** {entry.published}\n\n**📥 DL Link:** `{entry.link}`\n\n#TORRENTGALAXY" 
               # message
            elif "limetorrents" in entry.link:
                message = f"{mirr_cmd} {entry.links[1]['href']}"   
                message3 = f"**📂 FileName:** `{entry.title}`\n\n**📝 Published:** {entry.published}\n\n**📥 DL Link:** `{entry.links[1]['href']}`\n\n#LIMETORRENTS" 
               # message
            elif "torlock.com" in entry.link:
                message = f"{mirr_cmd} {entry.links[1]['href']}"   
                message3 = f"**📂 FileName:** `{entry.title}`\n\n**📝 Published:** {entry.published}\n\n**📥 DL Link:** `{entry.links[1]['href']}`\n\n#TORLOCK" 
               # message
            elif "erai-raws.info" in entry.link:
                message = f"{mirr_cmd} {entry.link}"    
                message3 = f"**📂 FileName:** `{entry.title}`\n\n**📝 Published:** {entry.published}\n\n**📥 DL Link:** `{entry.link}`\n\n#ERAIRAWS #ERAI" 
               # message
            elif "nyaa.si" in entry.link:
                message = f"{mirr_cmd} {entry.link}"   
                message3 = f"**📂 FileName:** `{entry.title}`\n\n**📝 Published:** {entry.published}\n\n**💾 FileSize:** `{entry.nyaa_size}`\n\n**📥 DL Link:** `{entry.link}`\n\n#NYAASI #NYAA" 
                # message2 = f"{leech_cmd} {entry.link}"
            elif "psa" in entry.link:
                message = f"Can't Mirror"   
                message3 = f"**📂 FileName:** `{entry.title}`\n\n**📝 Published:** {entry.published}\n\n**📥 DL Link:** `{entry.link}`\n\n#PSA" 
               # message
            else:
                message = f"{mirr_cmd} {entry.link}"
            try:
                msg = app.send_message(log_channel, message)
                if message2:
                     msg2 = app.send_message(log_channel, message2)
                if message3:
                     msg3 = app.send_message(log_channel2, message3)
                else:
                     pass
                db.update_link(feed_url, entry.id)
            except FloodWait as e:
                print(f"FloodWait: {e.x} seconds")
                sleep(e.x)
            except Exception as e:
                print(e)
        else:
            print(f"Checked RSS FEED: {entry.id}")
    return check_feed


scheduler = BackgroundScheduler()
for feed_url in feed_urls:
    feed_checker = create_feed_checker(feed_url)
    scheduler.add_job(feed_checker, "interval", seconds=check_interval, max_instances=max_instances)
scheduler.start()
app.run()
