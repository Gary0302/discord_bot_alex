import discord
from discord.ext import commands
from discord import Intents, Client, Message

# 初始化 Bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
intents : Intents = Intents.default()
intents.message_content = True
client : Client = Client(intents=intents)

# Bot 啟動事件
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# 發送通知指令
@bot.command()
async def notify(ctx, *, message):
    await ctx.send(f"Notification: {message}")

# 啟動 Bot
def run_discord_bot(token):
    bot.run(token)
