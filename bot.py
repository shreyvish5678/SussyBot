import discord
import responses
import os
from dotenv import load_dotenv
from PIL import Image
import numpy as np
import io
import time
import tensorflow as tf
import json
import redis
load_dotenv()
response_times = {}
TOKEN = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
redis_client = redis.StrictRedis(host="usw1-major-platypus-33840.upstash.io", port='33840', password=os.getenv("PASSWORD"), decode_responses=True)
async def send_message(message, user_message, is_private):
    try:
        user_id = str(message.author.id)
        user_name = str(message.author)
        try:
            spam_json = redis_client.get('spam_data')
            if spam_json is not None:
                spam = json.loads(spam_json)
            else:
                spam = {}
        except Exception:
            spam = {}
        if user_id in spam:
            if spam[user_id][0] >= 15:
                if time.time() - spam[user_id][1] <= 86400:
                    return
                else:
                    del spam[user_id]
        if user_id in response_times:
            elapsed_time = time.time() - response_times[user_id]
            if elapsed_time < 5:
                if user_id in spam:
                    spam[user_id][0] += 1
                    spam[user_id][1] = time.time()
                else:
                    spam[user_id] = (0, 0)
                    spam[user_id][0] = 1
                    spam[user_id][1] = time.time()
                if spam[user_id][0] >= 15:
                    await message.author.send(f"User {user_name} has been banned from using the bot for a day!") if is_private else await message.channel.send(f"User {user_name} has been banned from using the bot for a day!")
                else:
                    await message.author.send(f"Please wait {user_name}!") if is_private else await message.channel.send(f"Please wait {user_name}!")
                return
        response_times[user_id] = time.time()
        redis_client.set('spam_data', json.dumps(spam))
        response = responses.handle_response(user_message)
        if isinstance(response, dict):
            image_data = np.array(response["image"], dtype=np.uint8)
            noise = tf.reshape(response["noise"], shape=(100,)).numpy().tolist()
            img_byte_array = io.BytesIO()
            Image.fromarray(image_data, 'RGB').resize((400, 400)).save(img_byte_array, format='PNG')
            img_byte_array.seek(0)
            button1 = discord.ui.Button(label="1", style=discord.ButtonStyle.green)
            button2 = discord.ui.Button(label="2", style=discord.ButtonStyle.green)
            button3 = discord.ui.Button(label="3", style=discord.ButtonStyle.green)
            button4 = discord.ui.Button(label="4", style=discord.ButtonStyle.green, row=0)
            button5 = discord.ui.Button(label="5", style=discord.ButtonStyle.green, row=0)
            view = discord.ui.View()
            view.add_item(button1)
            view.add_item(button2)
            view.add_item(button3)
            view.add_item(button4)
            view.add_item(button5)
            await message.author.send(file=discord.File(img_byte_array, 'generated_image.png'), view=view) if is_private else await message.channel.send(file=discord.File(img_byte_array, 'generated_image.png'), view=view)
            try:
                feedback_data = json.loads(redis_client.get('feedback_data'))
            except Exception:
                feedback_data = {}
            key = max([int(digit) for digit in list(feedback_data.keys())], default=-1) + 1 if feedback_data else 0
            async def button_1_callback(interaction: discord.Interaction):
                if interaction.user.name == user_name:
                    await interaction.response.edit_message(content="You rated it 1/5", view=None)
                    feedback_data[key] = {"noise": noise, "rating": 1}
                    redis_client.set('feedback_data', json.dumps(feedback_data))
                else:
                    pass
            async def button_2_callback(interaction: discord.Interaction):
                if interaction.user.name == user_name:
                    await interaction.response.edit_message(content="You rated it 2/5", view=None)
                    feedback_data[key] = {"noise": noise, "rating": 2}
                    redis_client.set('feedback_data', json.dumps(feedback_data))
                else:
                    pass
            async def button_3_callback(interaction: discord.Interaction):
                if interaction.user.name == user_name:
                    await interaction.response.edit_message(content="You rated it 3/5", view=None)
                    feedback_data[key] = {"noise": noise, "rating": 3}
                    redis_client.set('feedback_data', json.dumps(feedback_data))
                else:
                    pass
            async def button_4_callback(interaction: discord.Interaction):
                if interaction.user.name == user_name:
                    await interaction.response.edit_message(content="You rated it 4/5", view=None)
                    feedback_data[key] = {"noise": noise, "rating": 4}
                    redis_client.set('feedback_data', json.dumps(feedback_data))
                else:
                    pass
            async def button_5_callback(interaction: discord.Interaction):
                if interaction.user.name == user_name:
                    await interaction.response.edit_message(content="You rated it 5/5", view=None)
                    feedback_data[key] = {"noise": noise, "rating": 5}
                    redis_client.set('feedback_data', json.dumps(feedback_data))
                else:
                    pass
            button1.callback = button_1_callback
            button2.callback = button_2_callback
            button3.callback = button_3_callback
            button4.callback = button_4_callback
            button5.callback = button_5_callback
            try:
                user_data_json = redis_client.get('user_data')
                if user_data_json is not None:
                    user_data = json.loads(user_data_json)
                else:
                    user_data = {}
            except Exception:
                user_data = {}
            if user_name not in user_data:
                user_data[user_name] = 1
            else:
                user_data[user_name] += 1
            redis_client.set('user_data', json.dumps(user_data))
        elif isinstance(response, str):
            await message.author.send(response) if is_private else await message.channel.send(response)
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
        user_message = str(message.content)
        if user_message:
            if user_message[0] == "!":
                user_message = user_message[1:]
                await send_message(message, user_message, is_private=False)
            elif user_message[0] == "?":
                user_message = user_message[1:]
                await send_message(message, user_message, is_private=True)
        
    client.run(TOKEN)
