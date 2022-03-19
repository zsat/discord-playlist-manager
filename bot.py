from discord.ext import commands

TOKEN = 'token for this bot in https://discord.com/developers/applications within the "bot" tab'

#this is the flag that our bot will respond too
bot = commands.Bot(command_prefix='~')

startup_extensions = ["music", "music_player"]

@bot.event
async def on_ready():
    print('Hello, world.')
    
    for extension in startup_extensions:
        bot.load_extension(extension)
        

#connects to discord
bot.run(TOKEN)
