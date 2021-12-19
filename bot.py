import discord
import requests
from io import BytesIO
import os.path
import cv2
import numpy as np
try:
    from PIL import Image
except ImportError:
    import Image
from easyocr import Reader
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser 
from whoosh.writing import AsyncWriter
import logging
logging.basicConfig(level=logging.INFO)

schema = Schema(content=TEXT, message_url=ID(stored=True), img_url=ID(stored=True), server=ID(stored=True))

ix = None
if not os.path.exists("index"):
    os.mkdir("index")
    ix = create_in("index", schema)
else: 
    ix = open_dir("index")


client = discord.Client()
reader = Reader(["en"])
stop_index = {}
def index_image(url, jump_url, guild_id):
            writer = AsyncWriter(ix)
            response = requests.get(url)
            im = np.array(Image.open(BytesIO(response.content)))
            im = cv2.bilateralFilter(im,5, 55,60)
            texts = reader.readtext(im, detail=0, paragraph=True)
            for text in texts:
                print(text)
                writer.add_document(content=text, message_url=jump_url, img_url=url, server=str(guild_id))
            writer.commit()

def check_message_and_index(message):
    for attachment in message.attachments:
        if attachment.content_type.startswith('image'):
            index_image(attachment.url, message.jump_url, message.guild.id)
    if message.content.startswith('https://images-ext'):
            index_image(message.content, message.jump_url, message.guild.id)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    check_message_and_index(message)
    if message.content.startswith('$meme search'):
        with ix.searcher() as searcher:
            querystring = message.content.split(maxsplit=2)[2]
            parser = QueryParser("content", ix.schema)
            query = parser.parse(querystring)
            results = searcher.search(query)
            results_list = []
            for hit in results:
                if hit["server"] == str(message.guild.id):
                    results_list.append(hit["message_url"])

            if len(results_list) > 0:
                await message.channel.send("\n".join(results_list))
            else:
                await message.channel.send("No results")
    elif message.content.startswith('$meme index'): #TODO implement indexing all existing memes
            stop_index[message.channel.id] = False
            await message.channel.send("Starting index, to cancel: `$meme cancel index`")
            counter = 0
            status_msg = await message.channel.send("Messages searched: " + str(counter))
            async for history_message in message.channel.history(limit=None):
                if stop_index[message.channel.id]: 
                    stop_index[message.channel.id] = False
                    await message.channel.send("Cancelled index")
                    break
                check_message_and_index(history_message)
                counter += 1
                status_content = "Messages searched: " + str(counter)
                await status_msg.edit(content=status_content)
    if message.content.startswith('$meme cancel index'):
        stop_index[message.channel.id] = True 

client.run("")
