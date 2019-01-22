import requests
import discord
from discord.ext import commands
import asyncio

token = 'TOKEN' #Put your token here
prefix = ['.'] #You can change this if you'd like
bot = commands.Bot(command_prefix=prefix)


global url
url = 'https://{0}.api.riotgames.com/lol/'

API = 'YOUR RIOT API' #Get the riot api from riot developer page
global apiurl
apiurl = '?api_key=YOUR RIOT API' #Get the riot api from riot developer page


@bot.event
async def on_ready():
    print('Bot is ready')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

def getsummonerid(region,name):

    posturl = 'summoner/v4/summoners/by-name/{1}'
    fullurl = (url + posturl + apiurl).format(region,name)

    response = requests.get(fullurl)

    return response.json()


@bot.command(pass_context=True)
async def getstats(ctx):
    inputs = ctx.message.content.split()
    region = inputs[1]
    if region.lower() == "na":
        region = "na1"

    name = ' '.join(inputs[2:])

    summoner_name, game_mode, rank, amount_wins= getsummonerstats(region,name)
    if rank == None:
        await bot.say('This player is unranked.')
        return
    champs, champ_points = getchamps(region,name)
    iconurl = geticonurl(region,name)
    s = ''
    for i in range(5):
        s += champs[i] + ' : ' + str(champ_points[i]) + '\n'

    e = discord.Embed(title="League of Legends Stats",color=0x00FFFF)
    e.set_thumbnail(url=iconurl)
    e.add_field(name=name.title(), value=f'[OPGG](http://na.op.gg/summoner/userName={name.replace(" ", "")})', inline=True)
    e.add_field(name='Game Mode', value=game_mode, inline=False)
    e.add_field(name='Rank:', value=rank, inline=False)
    e.add_field(name='Ranked Stats', value=amount_wins, inline=False)
    e.add_field(name="Champions : Mastery", value = s, inline=True)



    await bot.send_message(ctx.message.channel, embed=e)

def getsummonerstats(region,name):
    id = getsummonerid(region,name)['id']

    posturl = 'league/v4/positions/by-summoner/{1}'
    fullurl = (url + posturl + apiurl).format(region,id)

    response = requests.get(fullurl).json()
    try:
        summoner_name = str(response[0]['summonerName']) + ' ' + '-' + ' ' + str(response[0]['leagueName'])
        game_mode = str(response[0]['queueType'])
        rank = str(response[0]['tier']) + ' ' + str(response[0]['rank']) + ' ' + str(response[0]['leaguePoints'])
        amount_wins = 'W:' + str(response[0]['wins']) + ' ' + '/' + ' ' + 'L:' + str(response[0]['losses'])
    except:
        return None, None, None, None
    return summoner_name, game_mode, rank, amount_wins


def geticonurl(region,name):
    id = getsummonerid(region,name)['id']

    posturl = 'summoner/v4/summoners/{1}'
    fullurl = (url + posturl + apiurl).format(region,id)

    response = requests.get(fullurl).json()
    iconid = response['profileIconId']

    iconurl = 'http://ddragon.leagueoflegends.com/cdn/6.24.1/img/profileicon/{0}.png'.format(iconid)

    return iconurl

def getchamps(region, name):
    id = getsummonerid(region,name)['id']
    posturl = 'champion-mastery/v4/champion-masteries/by-summoner/{1}'
    fullurl = (url + posturl + apiurl).format(region,id)

    champ_id = []
    champ_points = []
    response = requests.get(fullurl).json()
    i = 0
    for dict in response:
        champ_id.append(dict['championId'])
        champ_points.append(dict['championPoints'])
        if i == 4:
            break
        i += 1


    champurl = 'http://ddragon.leagueoflegends.com/cdn/6.24.1/data/en_US/champion.json'
    champlist = requests.get(champurl).json()
    champs = []
    for id in champ_id:
        for key in champlist['data'].keys():
            if (int(champlist['data'][key]['key'])) == int(id):
                champs.append(champlist['data'][key]['name'])
    return champs, champ_points

bot.run(token)
