import os
import discord
from discord import app_commands
import asyncio

token = os.environ.get("DISCORD_TOKEN")
if not token:
    raise SystemExit("DISCORD_TOKEN environment variable is not set!")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)  # this is what makes slash commands possible

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} slash command(s) globally (can take up to an hour to appear)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@tree.command(name="ping", description="Check if the bot is online and responding")
async def ping(interaction: discord.Interaction):
    latency_ms = round(client.latency * 1000)
    await interaction.response.send_message(f":-) Pong! Bot is online. Latency: {latency_ms}ms")

@tree.command(name="ily", description="I Love You")
async def ily(interaction: discord.Interaction):
    await interaction.response.send_message("I Love You Too <3")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # New: reply if a specific user says a specific word
    if message.author.id == 660865929391112212 and "ontologically" in message.content.lower():
        await message.channel.send("<@660865929391112212> your not allowed to say that word.")

    if "jerk off poop ijbol" in message.content.lower():
        await message.add_reaction("<:evilchudsmile:1529903849597571132>")



client.run(token)