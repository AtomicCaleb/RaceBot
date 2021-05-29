# bot.py
##################VARIABLES#######################################
from __future__ import print_function
from dotenv import load_dotenv

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import os.path
import discord
import time

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


# The ID and range of a sample spreadsheet.

SAMPLE_RANGE_NAME = 'A2:E'

sharcordChannel = 847495184660955146
testChannel = 382486010417643530
chessChannel = 827714631714734160

testSheet = '1IM24hRS_giIC5OcNNGBrHfwIZpbOcUyUURgt-q4913w'
sharcordSheet = '1HB6LujCo6R2XeIVrWYdAZ8gQkA7qWrTF9QQlAWblizY'

class race:
    raceData = ''
    raceTime = time.gmtime
    messageID = 0

#####################FUNCTIONS################################

def GetRaceTime(timeString):
    dateTimeFormat = '%d/%m/%y | %H:%M%P %Z'
    return datetime.strptime(timeString, dateTimeFormat)

def WriteRacesToFile():
    with open('Races.txt', 'w') as f:
        for race in Races:
            f.write(race)

def GetRaceData():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=testSheet,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    RaceData = ['']
    if not values:
        print('No data found.')
    else:
        for row in values:
            runnerTwoRow = 4
            if len(row) < 3:
                continue;
            elif len(row) < 4:
                runnerTwoRow = 3         
        # Print columns A and E, which correspond to indices 0 and 4.
            if row[0] and row[1] and row[2] and row[runnerTwoRow]:
                data = row[0] + ',' + row[1] + ',' + row[2] +',' + row[runnerTwoRow] + '\n'
                RaceData.append(data)
    return RaceData

def CompareRaces():
    with open('Races.txt') as f:
        fileRaces = f.readlines()
    raceData = GetRaceData()
    i = 0
    
    global NEWRACES
    NEWRACES = ''
   
    for sheetsRace in raceData:
        if(len(sheetsRace)) == 0:
            continue
        found = sheetsRace in fileRaces
        if not found:
            print(sheetsRace)
            raceInfo = sheetsRace.split(',')
            NEWRACES += '**New Race Scheduled**\n Date/Time: %s\n Category: %s' % (raceInfo[0], raceInfo[1])
            NEWRACES += '\n Racers: %s VS %s\n' % (raceInfo[2], raceInfo[3])
         
    for fileRace in fileRaces:
        found = fileRace in raceData
        if not found:
            raceInfo = fileRace.split(',')
            NEWRACES += '**Race Removed**\n Date/Time: %s\n Category: %s' % (raceInfo[0], raceInfo[1])
            NEWRACES += '\n Racers: %s VS %s\n' % (raceInfo[2], raceInfo[3])
    if len(NEWRACES) == 0:
        NEWRACES = ''
        #NEWRACES = 'No New Races'

########################ACTUAL CODE##############################

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
#client.run(TOKEN)

async def func():
    while(True):
        CompareRaces()
        global Races
        Races = GetRaceData()
        WriteRacesToFile()
        if len(NEWRACES) != 0:
            for chunk in chunks(NEWRACES, 2000):
            	await client.get_channel(testChannel).send(chunk)
        else:
            print('no new races')
        time.sleep(15)


def chunks(s, n):
    """Produce `n`-character chunks from `s`."""
    for start in range(0, len(s), n):
        yield s[start:start+n]
        
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await func();

@client.event
async def on_message(message):
    if message.author == client.user:
       return
    print(message.content);
    if message.content.startswith('races'):
        for chunk in chunks(RACEDATA, 2000):
            await message.channel.send(chunk)

client.run(TOKEN)
