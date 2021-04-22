import os
import random
import requests
import json
import asyncio
import discord

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
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return (quote)


def parse_citations():
    citations = []
    textFile = open("citations.txt", "r")

    for quote in textFile:
        citation, author = quote.split(" | ")
        data = {}
        data["c"] = citation.strip()
        data["a"] = author.strip().rstrip("\n")
        citations.append(data)
    textFile.close()
    return citations


def generate_citations_json():
    citations = parse_citations()
    jsonQuotes = open("citations.json", "w")
    json.dump(citations, jsonQuotes, ensure_ascii=False)
    jsonQuotes.close()


class MyClient(discord.Client):

    async def on_member_join(self, member):
        greeting = f"""
Salut *{member.name}*,

Je suis ***{client.user.name}*** et bienvenue sur ***le serveur Discord de l'Ascension***!

Ce serveur est dédiée aux personnes noirs de region parisienne afin de renforcer notre communauté, apprendre sur notre histoire, promouvoir nos business, s'inspirer et s'amuser.

Tu trouveras des channels dédiés a l'apprentissage des langues, un club de lecture, une conversation privé pour femme/homme. Pour y acceder, va dans le channel <#797855506495438868> et appuis sur les icones correspondants aux roles que tu souhaites avoir.

Nous avons aussi tous les vendredis soir des debats sur des sujets qui nous concernent.

Pour toute questions ou suggestions d'amélioration n'hesite pas a faire appel aux admins.

A plus tard sur le serveur! :wave_tone5:
        """
        await member.create_dm()
        await member.dm_channel.send(greeting)

    async def on_ready(self):
        print(
            f'{self.user.name} has connected to Discord!\n'
            f'{self.user.id} is my id'
        )

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


generate_citations_json()
client = MyClient()
client.run(TOKEN)
