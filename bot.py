import discord
from discord.ext import commands
import datetime
import json
from ext.formatter import EmbedHelp
import inspect
import os

def run_wizard():
    print('------------------------------------------')
    print('WELCOME TO THE VERIX-SELFBOT SETUP WIZARD!')
    print('------------------------------------------')
    token = input('Enter your token:\n> ')
    print('------------------------------------------')
    prefix = input('Enter a prefix for your selfbot:\n> ')
    data = {
        "BOT": {
            "TOKEN" : token,
            "PREFIX" : prefix
            },
        "FIRST" : False
        }
    with open('data/config.json','w') as f:
        f.write(json.dumps(data, indent=4))
    print('------------------------------------------')
    print('Successfully saved your data!')
    print('------------------------------------------')
    


if 'TOKEN' in os.environ:
    heroku = True
    TOKEN = os.environ['TOKEN']
else:
    with open('data/config.json') as f:
        if json.load(f)['FIRST']:
            run_wizard()
    with open('data/config.json') as f:  
        TOKEN = json.load(f)["BOT"]['TOKEN']

async def get_pre(bot, message):
    with open('data/config.json') as f:
        config = json.load(f)
    try:
        return config["BOT"]['PREFIX']
    except:
        return 's.'

bot = commands.Bot(command_prefix=get_pre, self_bot=True, formatter=EmbedHelp())
bot.remove_command('help')

_extensions = [

    'cogs.misc',
    'cogs.info',
    'cogs.utils',
    'cogs.mod'

    ]

@bot.event
async def on_ready():
    bot.uptime = datetime.datetime.now()
    print('------------------------------------------\n'
    	  'Self-Bot Ready\n'
    	  'Author: verix#7220\n'
    	  '------------------------------------------\n'
    	  'Username: {}\n'
          'User ID: {}\n'
          '------------------------------------------'
    	  .format(bot.user, bot.user.id))
    if heroku:
        print('Hosting on heroku.')



@bot.command(pass_context=True)
async def ping(ctx):
    """Pong! Check your response time."""
    msgtime = ctx.message.timestamp.now()
    await (await bot.ws.ping())
    now = datetime.datetime.now()
    ping = now - msgtime
    pong = discord.Embed(title='Pong! Response Time:', 
    					 description=str(ping.microseconds / 1000.0) + ' ms',
                         color=0x00ffff)

    await bot.say(embed=pong)

@bot.command(name='presence')
async def _set(Type=None,*,thing=None):
    """Change your discord game/stream!"""
    if Type is None:
            await bot.say('Usage: `.presence [game/stream] [message]`')
    else:
        if Type.lower() == 'stream':
            await bot.change_presence(game=discord.Game(name=thing,type=1,url='https://www.twitch.tv/a'),status='online')
            await bot.say('Set presence to. `Streaming {}`'.format(thing))
        elif Type.lower() == 'game':
            await bot.change_presence(game=discord.Game(name=thing))
            await bot.say('Set presence to `Playing {}`'.format(thing))
        elif Type.lower() == 'clear':
            await bot.change_presence(game=None)
            await bot.say('Cleared Presence')
        else:
            await bot.say('Usage: `.presence [game/stream] [message]`')

async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            print(page)
            await bot.send_message(ctx.message.channel, embed=page)
        print('Sent command help')
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            print(page)
            await bot.send_message(ctx.message.channel, embed=page)
        print('Sent command help')

@bot.event
async def on_command_error(error, ctx):
   print(error)
   channel = ctx.message.channel
   if isinstance(error, commands.MissingRequiredArgument):
       await send_cmd_help(ctx)
       print('Sent command help')
   elif isinstance(error, commands.BadArgument):
       await send_cmd_help(ctx)
       print('Sent command help')
   elif isinstance(error, commands.DisabledCommand):
       await bot.send_message(channel, "That command is disabled.")
       print('Command disabled.')
   elif isinstance(error, commands.CommandInvokeError):
       # A bit hacky, couldn't find a better way
       no_dms = "Cannot send messages to this user"
       is_help_cmd = ctx.command.qualified_name == "help"
       is_forbidden = isinstance(error.original, discord.Forbidden)
       if is_help_cmd and is_forbidden and error.original.text == no_dms:
           msg = ("I couldn't send the help message to you in DM. Either"
                  " you blocked me or you disabled DMs in this server.")
           await bot.send_message(channel, msg)
           return




@bot.command(pass_context=True,name='reload')
async def _reload(ctx,*, module : str):
    """Reloads a module."""
    channel = ctx.message.channel
    module = 'cogs.'+module
    try:
        bot.unload_extension(module)
        x = await bot.send_message(channel,'Successfully Unloaded.')
        bot.load_extension(module)
        x = await bot.edit_message(x,'Successfully Reloaded.')
    except Exception as e:
        x = await bot.edit_message(x,'\N{PISTOL}')
        await bot.say('{}: {}'.format(type(e).__name__, e))
    else:
        x = await bot.edit_message(x,'Done. \N{OK HAND SIGN}')

@bot.command(pass_context=True)
async def load(ctx, *, module):
    '''Loads a module.'''
    module = 'cogs.'+module
    try:
        bot.load_extension(module)
        x = await bot.say('Successfully Loaded.')
    except Exception as e:
        x = await bot.edit_message(x,'\N{PISTOL}')
        await bot.say('{}: {}'.format(type(e).__name__, e))

@bot.command(pass_context=True)
async def unload(ctx, *, module):
    '''Unloads a module.'''
    module = 'cogs.'+module
    try:
        bot.unload_extension(module)
        x = await bot.say('Successfully Unloaded.')
    except Exception as e:
        x = await bot.edit_message(x,'\N{PISTOL}')
        await bot.say('{}: {}'.format(type(e).__name__, e))


if __name__ == "__main__":
    for extension in _extensions:
        try:
            bot.load_extension(extension)
            print('Loaded: {}'.format(extension))
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Error on load: {}\n{}'.format(extension, exc))

try:   
    bot.run(TOKEN, bot=False)
except Exception as e:
    print('\n[ERROR]: \n{}\n'.format(e))

    











    
    
