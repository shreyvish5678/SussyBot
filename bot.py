import discord
import responses
import os
from dotenv import load_dotenv
from PIL import Image
import numpy as np
import io
import time
load_dotenv()
response_times = {}
async def send_message(message, user_message, is_private):
    try:
        user_id = str(message.author.id)
        if user_id in response_times:
            elapsed_time = time.time() - response_times[user_id]
            if elapsed_time < 5:
                await message.author.send(f"Please wait {message.author}!") if is_private else await message.channel.send(f"Please wait {message.author}!")
                return
        response_times[user_id] = time.time()
        response = responses.handle_response(user_message)
        if isinstance(response, str):
            await message.author.send(response) if is_private else await message.channel.send(response)
        else:
            image_data = np.array(response, dtype=np.uint8)
            img_byte_array = io.BytesIO()
            Image.fromarray(image_data, 'RGB').save(img_byte_array, format='PNG')
            img_byte_array.seek(0)
            await message.author.send(file=discord.File(img_byte_array, filename='image.png')) if is_private else await message.channel.send(file=discord.File(img_byte_array, filename='image.png'))
    except Exception as e:
        print(e)

def run_discord_bot():
    TOKEN = os.getenv("BOT_TOKEN")
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    @client.event
    async def on_ready():
        print(f'{client.user} has connected to Discord!')
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        print(f"{username}: {user_message} ({channel})")
        if user_message:
            if user_message[0] == "!":
                user_message = user_message[1:]
                await send_message(message, user_message, is_private=False)
            elif user_message[0] == "?":
                user_message = user_message[1:]
                await send_message(message, user_message, is_private=True)
        
    client.run(TOKEN)
