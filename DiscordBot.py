import os
import discord
from discord import app_commands
import asyncio
from mcstatus import JavaServer

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

 

# Minecraft server control
MINECRAFT_DIR = "/home/sputnik/minecraft-server"
MINECRAFT_START_CMD = "java -jar minecraft_server.jar -Xmx6024M -Xms1024M nogui"
MINECRAFT_SESSION = "minecraft"

@tree.command(name="startmc", description="Start the Minecraft Server (currently running CABIN)")
async def startmc(interaction: discord.Interaction):
    await interaction.response.defer()
 
    # Check if a tmux session with this name already exists
    check = await asyncio.create_subprocess_exec(
        "tmux", "has-session", "-t", MINECRAFT_SESSION,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await check.wait()
 
    if check.returncode == 0:
        await interaction.followup.send("Server is already running ! silly goose ! haha : - ) your so silly hahaha. >_<")
        return
 
    # Create a new detached tmux session and start the server inside it
    start = await asyncio.create_subprocess_exec(
        "tmux", "new-session", "-d", "-s", MINECRAFT_SESSION,
        "-c", MINECRAFT_DIR,
        MINECRAFT_START_CMD
    )
    await start.wait()
 
    if start.returncode == 0:
        await interaction.followup.send("Starting server... should be up soon... if i coded this right... haha ..... <:useless:1538644914982883328>")
    else:
        await interaction.followup.send("Failed to start the tmux session. Check the server logs. <:geekbar:1538647146872574115>: Help !!!")

 

MINECRAFT_HOST = "localhost"
MINECRAFT_PORT = 25565

@tree.command(name="server", description="shows information about the ser (currently running CABIN)")
async def server_info(interaction: discord.Interaction):
    await interaction.response.defer()
 
    # First check if it's even running at all via tmux
    check = await asyncio.create_subprocess_exec(
        "tmux", "has-session", "-t", MINECRAFT_SESSION,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await check.wait()
 
    if check.returncode != 0:
        await interaction.followup.send("Server Offline.")
        return
 
    try:
        mc_server = JavaServer.lookup(f"{MINECRAFT_HOST}:{MINECRAFT_PORT}")
        # mcstatus's status() call is blocking (not async-native), so we run it
        # in a separate thread with asyncio.to_thread - this stops it from
        # freezing the whole bot while it waits on the network request.
        status = await asyncio.to_thread(mc_server.status)
 
        if status.players.sample:
            who = ", ".join(p.name for p in status.players.sample)
        else:
            who = "nobody right now"
 
        message = (
            f" **Server Online**\n"
            f"Players: {status.players.online}/{status.players.max} ({who})\n"
            f"Version: {status.version.name}\n"
            f"Ping: {round(status.latency)}ms"
        )
        await interaction.followup.send(message)
 
    except Exception as e:
        await interaction.followup.send(
            f"⚠️ Server process is running, but I couldn't get status from it "
            f"(maybe it's still starting up). Error: {e}"
        )
 
 

    

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