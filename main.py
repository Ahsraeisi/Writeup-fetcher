import configparser
import feedparser
from discord_webhook import DiscordWebhook, DiscordEmbed
from pymongo import MongoClient

#Reading Config from the file.
config = configparser.ConfigParser()
config.read('config.ini')

host = config.get('MongoDB', 'host')
port = config.get('MongoDB', 'port')
connetion_string = f"mongodb://{host}:{port}"
client = MongoClient(connetion_string)
Writeups_db = client.writeups
collection = Writeups_db.medium

def fetch_urls():
    urls = []
    with open('URLs.txt','r') as u:
        for url in u:
            url = url.strip()
            urls.append(url)
    return urls
        
Webhook = config.get('Discord', 'webhook')

def feed():
    writeups = []
    for i in fetch_urls():
        feed = feedparser.parse(i)
        for entry in feed.entries:

            title = entry.title
            link = entry.link.split('?')[0]

            writeups.append({"title": title, "link": link})

    return writeups


def insert_data(data):
    
    if 'writeups' in client.list_database_names():
        print("platforms DB Already exists!")
        return
    try:
         collection.insert_many(data)
         print("Successfully added to DB.")
         return True
    except Exception as e:
        print(e)

def Check_for_changes():

    new_data = feed()

    for writeup in new_data:
        old_data = collection.find_one({"link":writeup['link']})
        
        if old_data == None:
            title = writeup['title']
            link = writeup['link']
            push_program(title, link)
            collection.insert_one(writeup)

def push_program(title, link):

    author = {
    'name': 'AmirRaeisi',
    'url': 'https://twitter.com/Ahsraeisi',
    'icon_url': 'https://pbs.twimg.com/profile_images/1658796700742426627/nZu6oOBU_400x400.jpg'
    }
    
    webhook_url = Webhook

    embed = DiscordEmbed(title=title, color='0x00FFFF')
    embed.set_author(name=author['name'], url=author['url'], icon_url=author['icon_url'])
    embed.url = link

    webhook = DiscordWebhook(url=webhook_url,embeds=[embed])
    response = webhook.execute()

def main():
 
    data = feed()
    insert_data(data)
    Check_for_changes()

if __name__ == "__main__":
    main()
