import discord
from discord.ext import commands
import pandas as pd
import os
from openai import AsyncOpenAI, OpenAI


TOKEN = os.getenv('DS_TOKEN')

intents = discord.Intents.all()
intents.messages = True  # Enable message-related intents

# Create a bot instance with intents
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def fetch_messages(ctx, channel_id: int, limit: int):
    try:
        channel = bot.get_channel(channel_id)
        if channel:
            messages = channel.history(limit=limit)
            messages_list = []
            replies_list = []
            replies_dict = {}
            async for message in messages:
                if message.id in replies_dict.keys():
                    new_message = ""
                    for word in message.content.split():
                        if 'https' in word or (word[0] == '<' and word[-1] == '>'):
                            continue
                        new_message += " " + word
                    message.content = new_message
                    if message.content.replace(" ", ""):
                        for i in range(len(replies_dict[message.id])):
                            messages_list.append(message.content)
                            replies_list.append(replies_dict[message.id][i])
                if message.reference:
                    # print(message.reference)
                    # print(message.content)
                    new_message = ""
                    for word in message.content.split():
                        if 'https' in word or (word[0] == '<' and word[-1] == '>'):
                            continue
                        new_message += " " + word
                    message.content = new_message
                    if message.content.replace(" ", ""):
                        print(message.content)
                        if message.reference.message_id in replies_dict.keys():
                            replies_dict[message.reference.message_id].append(message.content)
                        else:
                            replies_dict[message.reference.message_id] = [message.content]
            df = pd.DataFrame(data={'messages': messages_list, 'replies': replies_list})
            df.to_csv('discord_messages_v2.csv')

        else:
            await ctx.send('Channel not found.')
    except Exception as e:
        print(f'An error occurred: {e}')

client = AsyncOpenAI(api_key=os.getenv('AI_TOKEN'))
async def gpt4(question):
    print(client.models.list())
    response = await client.chat.completions.create(
        messages=[{'role': 'user',
                   'content': str(question)}],
        model='gpt-3.5-turbo'
    )
    return response

@bot.event
async def on_message(message):

    if bot.user in message.mentions:
        user_message = message.content.split("<@")[1].split(">")[1].strip()
    response = await gpt4(user_message)
    print(response)

bot.run(TOKEN)
