import discord
import responses
import os
from dotenv import load_dotenv
from PIL import Image
import numpy as np
import io
import sqlite3
import time
load_dotenv()
response_times = {}
TOKEN = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
async def send_message(message, user_message, is_private):
    try:
        user_id = str(message.author.id)
        user_name = str(message.author)
        if user_id in response_times:
            elapsed_time = time.time() - response_times[user_id]
            if elapsed_time < 5:
                await message.author.send(f"Please wait {user_name}!") if is_private else await message.channel.send(f"Please wait {user_name}!")
                return
        response_times[user_id] = time.time()
        response = responses.handle_response(user_message)
        image_data = np.array(response, dtype=np.uint8)
        img_byte_array = io.BytesIO()
        Image.fromarray(image_data, 'RGB').save(img_byte_array, format='PNG')
        img_byte_array.seek(0)
        await message.author.send(file=discord.File(img_byte_array, 'generated_image.png')) if is_private else await message.channel.send(file=discord.File(img_byte_array, 'generated_image.png'))
        with sqlite3.connect("user_db.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS user_usage (
                                id INTEGER PRIMARY KEY,
                                name TEXT,
                                usage_count INTEGER
                            )''')
            connection.commit()
        with sqlite3.connect("user_db.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user_usage WHERE name = ?", (user_name,))
            existing_user = cursor.fetchone()
            if existing_user:
                usage_count = existing_user[2] + 1
                cursor.execute("UPDATE user_usage SET usage_count = ? WHERE name = ?", (usage_count, user_name))
            else:
                cursor.execute("INSERT INTO user_usage (name, usage_count) VALUES (?, 1)", (user_name,))
            connection.commit()
    except Exception as e:
        print(e)

def run_discord_bot():
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
        if user_message:
            if user_message[0] == "!":
                user_message = user_message[1:]
                await send_message(message, user_message, is_private=False)
            elif user_message[0] == "?":
                user_message = user_message[1:]
                await send_message(message, user_message, is_private=True)
        
    client.run(TOKEN)
