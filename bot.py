import os, random, requests, json, asyncio

from sqlalchemy.orm import Session, sessionmaker

# In a .env file create a variable where you store the discord bot token
import discord
from dotenv import load_dotenv

from model import db, Suggestion

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

Session = sessionmaker(bind=db)

session = Session()


sad_words = ["triste", "déprimer", "mécontent", "colère", "miserable"]
starter_encoragements = [
    "Courage!",
    "Tiens le coup",
    "La vie est faite de haut et de bas"
]

def update_suggestion(improve):
    if len(improve) > 0:
        session.add(Suggestion(content=improve))
        session.commit()

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return (quote)


class MyClient(discord.Client):
    greeting_words = ['bonjour', 'salut', 'hello']

    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(
            f'Salut {member.name}, \nje suis {client.user.name} bienvenue sur Ascension'
            f'Pense à choisir ton rôle et '
        )

    
    async def on_ready(self):
        print(
            f'{self.user.name} has connected to Discord!\n'
            f'{self.user.id} is my id'
        )
        

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        msg = message.content

        if msg.startswith('$Salut'):
            await message.reply('Hello!', mention_author=True)
        
        if any(word in message.content for word in self.greeting_words):
            await message.reply('Bonjour!', mention_author=True)

        if msg.startswith('!editme'):
            msg = await message.channel.send('10')
            await asyncio.sleep(3.0)
            await msg.edit(content='40')

        if msg.startswith('!deletme'):
            msg = await message.channel.send('I will delete myself now...')
            await msg.delete()
            await message.channel.send('Goodbye in 10 seconds...', delete_after=10.0)
        
        if msg.startswith('$new'):
            improve = msg.split('$new ', 1)[1]
            update_suggestion(improve)
            await message.channel.send("Votre suggestion d'amélioration a été ajouté.")

        if msg.startswith('$sugg'):
            suggestion = session.query(Suggestion.id, Suggestion.content).all()
            await message.channel.send(suggestion)
        
        if any(word in msg for word in sad_words):
            await message.channel.send(random.choice(starter_encoragements))

        if msg.startswith('$inspire'):
            quote = get_quote()
            await message.channel.send(quote)

        

    async def on_message_edit(self, before, after):
        fmt = '**{0.author}** edited their message:\n{0.content} -> {1.content}'
        await before.channel.send(fmt.format(before, after))

    async def on_message_delete(self, message):
        fmt = '{0.author} has deleted the message: {0.content}'
        await message.channel.send(fmt.format(message))


client = MyClient()
client.run(TOKEN)