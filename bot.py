import discord
import responses
import os
from dotenv import load_dotenv
from PIL import Image
import numpy as np
import io
import numpy
import time
import tensorflow as tf
import json
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
            with open('feedback.json', 'r') as file:
                feedback_data = json.load(file)
        except FileNotFoundError:
            feedback_data = {}
        key = max([int(digit) for digit in list(feedback_data.keys())], default=-1) + 1 if feedback_data else 0
        async def button_1_callback(interaction: discord.Interaction):
            await interaction.response.edit_message(content="You rated it 1/5", view=None)
            feedback_data[key] = {"noise": noise, "rating": 1}
            with open('feedback.json', 'w') as file:
                json.dump(feedback_data, file)
        async def button_2_callback(interaction: discord.Interaction):
            await interaction.response.edit_message(content="You rated it 2/5", view=None)
            feedback_data[key] = {"noise": noise, "rating": 2}
            with open('feedback.json', 'w') as file:
                json.dump(feedback_data, file)
        async def button_3_callback(interaction: discord.Interaction):
            await interaction.response.edit_message(content="You rated it 3/5", view=None)
            feedback_data[key] = {"noise": noise, "rating": 3}
            with open('feedback.json', 'w') as file:
                json.dump(feedback_data, file)
        async def button_4_callback(interaction: discord.Interaction):
            await interaction.response.edit_message(content="You rated it 4/5", view=None)
            feedback_data[key] = {"noise": noise, "rating": 4}
            with open('feedback.json', 'w') as file:
                json.dump(feedback_data, file)
        async def button_5_callback(interaction: discord.Interaction):
            await interaction.response.edit_message(content="You rated it 5/5", view=None)
            feedback_data[key] = {"noise": noise, "rating": 5}
            with open('feedback.json', 'w') as file:
                json.dump(feedback_data, file)
        button1.callback = button_1_callback
        button2.callback = button_2_callback
        button3.callback = button_3_callback
        button4.callback = button_4_callback
        button5.callback = button_5_callback
        try:
            with open('user.json', 'r') as file:
                user_data = json.load(file)
        except FileNotFoundError:
            user_data = {}
        if user_name not in user_data:
            user_data[user_name] = 1
        else:
            user_data[user_name] += 1
        with open('user.json', 'w') as file:
            json.dump(user_data, file)
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
