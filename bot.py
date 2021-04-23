import os
import random
import requests
import json
import asyncio
import discord
from discord.ext import tasks
from datetime import datetime, timedelta

from sqlalchemy.orm import Session, sessionmaker
from dotenv import load_dotenv

from model import db, Suggestion

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

Session = sessionmaker(bind=db)
session = Session()


def update_suggestion(improve):
    if len(improve) > 0:
        session.add(Suggestion(content=improve))
        session.commit()


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " \n\n \t\t\t-" + json_data[0]['a']
    return (quote)


def parse_citations():
    citations = []
    with open("citations.txt", "r") as textFile:
        for quote in textFile:
            citation, author = quote.split(" | ")
            data = {}
            data["c"] = citation.strip()
            data["a"] = author.strip().rstrip("\n")
            citations.append(data)
    return citations


def generate_citations_json():
    citations = parse_citations()
    with open("citations.json", "w") as jsonQuotes:
        json.dump(citations, jsonQuotes, ensure_ascii=False)
        


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daily_inspiration.start()

    async def on_ready(self):
        print(
            f'{self.user.name} has connected to Discord!\n'
            f'{self.user.id} is my id'
        )

    async def on_member_join(self, member):
        greeting = f"""
Salut *{member.name}*,

Je suis ***{self.user.name}*** et bienvenue sur ***le serveur Discord de l'Ascension***!

Ce serveur est dédiée aux personnes noirs de region parisienne afin de renforcer notre communauté, apprendre sur notre histoire, promouvoir nos business, s'inspirer et s'amuser.

Tu trouveras des channels dédiés a l'apprentissage des langues, un club de lecture, une conversation privé pour femme/homme. Pour y acceder, va dans le channel <#1234> et appuis sur les icones correspondants aux roles que tu souhaites avoir.

Nous avons aussi tous les vendredis soir des debats sur des sujets qui nous concernent.

Pour toute questions ou suggestions d'amélioration n'hesite pas a faire appel aux admins.

A plus tard sur le serveur! :wave_tone5:
        """
        await member.create_dm()
        await member.dm_channel.send(greeting)


    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        msg = message.content

        if msg.startswith('$new'):
            improve = msg.split('$new ', 1)[1]
            update_suggestion(improve)
            await message.channel.send("Votre suggestion d'amélioration a été ajouté.")

        if msg.startswith('$sugg'):
            suggestion = session.query(Suggestion.id, Suggestion.content).all()
            await message.channel.send(suggestion)

        if msg.startswith('$inspire'):
            quote = get_quote()
            await message.channel.send(quote)

    @tasks.loop(hours=24)
    async def daily_inspiration(self):
        ## if you have the channel id uncomment the two lines above and provide it 

        # channel_id = the_channel_id
        # channel = self.get_channel(channel_id)

        ## or just provide the channel name on the line above
        channel = discord.utils.get(self.guilds[0].channels, name='channel_name') 
        quote = get_quote()

        await channel.send(f'\t\t***Quote of the day***\n\n' +  quote)

    @daily_inspiration.before_loop
    async def before_inspiration(self):
        hour = 7
        minute = 0
        await self.wait_until_ready()
        now = datetime.now()
        future = datetime(now.year, now.month, now.day, hour, minute)
        if now.hour >= hour and now.minute > minute:
            future += timedelta(days=1)
        await asyncio.sleep((future-now).seconds)




generate_citations_json()
client = MyClient()
client.run(TOKEN)
