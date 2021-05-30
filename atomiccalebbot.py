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


#race data stuff
class Race:
    data = ''
    raceTime = time.gmtime
    messageID = 0

sharcordRaces = []
chessRaces = []

sharcordTxtFile = 'sharcordRaces.txt'
chessTxtFile = 'chessRaces.txt'

# The ID and range of a sample spreadsheet.
SAMPLE_RANGE_NAME = 'A2:E'

#channels
sharcordChannel = 847495184660955146
chessChannel = 827714631714734160
testChannel = 382486010417643530
testChannelTwo = 848165475925229568

#google sheets
testSheet = '1IM24hRS_giIC5OcNNGBrHfwIZpbOcUyUURgt-q4913w'
sharcordSheet = '1HB6LujCo6R2XeIVrWYdAZ8gQkA7qWrTF9QQlAWblizY'
chessSheet = '1QAFp_BOB1j_0v_8S6ubhAITvKZru0mcZv_amgvpbbYc'


#####################FUNCTIONS################################

def GetRaceTime(timeString):
    dateTimeFormat = '%d/%m/%y | %H:%M%P %Z'
    return datetime.strptime(timeString, dateTimeFormat)

def WriteRacesToFile(races, fileName):
    with open(fileName, 'w') as f:
        for race in races:
            f.write(race.data)

def GetRaceData(sheet, hasCategory):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    sheetToUse = sheet
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
    result = sheet.values().get(spreadsheetId=sheetToUse,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    raceDatas = []
    if not values:
        print('No data found.')
    else:
        dateTime = 0
        category = 1
        runnerOne = 2
        runnerTwo = 4
        if not hasCategory:
            runnerOne -= 1
            runnerTwo -= 1

        for row in values:
        #if there isnt enoughdata dont bother
            raceData = Race()
            if len(row) < 3:
                continue
            if len(row) < 4:
                runnerTwo -= 1

            if hasCategory:
                if row[dateTime] and row[category] and row[runnerOne] and row[runnerTwo]:
                    data = row[dateTime] + ',' + row[category] + ',' + row[runnerOne] +',' + row[runnerTwo] + '\n'
                    raceData.data = data
            else:
                if row[dateTime] and row[category] and row[runnerOne] and row[runnerTwo]:
                    data = row[dateTime] +',' + row[runnerOne] +',' + row[runnerTwo] + '\n'
                    raceData.data = data

            raceDatas.append(raceData)
    return raceDatas

def GetMessageString(raceInfo, added, hasCategory, chess):
     raceString = ''
     raceInfoList = raceInfo.split(',')

     headerPart = '**New Race Scheduled**' if added else '**Race Removed**'
     raceString += headerPart 
     raceString += '\n Date/Time:' + raceInfoList[0]
     if hasCategory:
        raceString += '\n Category: %s \n Racers: %s VS %s\n' % (raceInfoList[1], raceInfoList[2], raceInfoList[3])
     elif not chess:
        raceString += '\n Category: ASM \n Racers: %s VS %s\n' % (raceInfoList[1], raceInfoList[2])
     else:
        raceString += '\n Racers: %s VS %s\n' % (raceInfoList[1], raceInfoList[2])
         
     return raceString


def CompareRaces(races, txtFile, hasCategory, chess):
    with open(txtFile) as f:
        fileRaces = f.readlines()
    raceDataStrings = []
    for race in races:
        raceDataStrings.append(race.data)

    i = 0
    NEWRACES = ''
   
    for race in races:
        if len(race.data) == 0:
            continue
        found = race.data in fileRaces
        if not found:
            NEWRACES += GetMessageString(race.data, True, hasCategory, chess)
         
    for fileRace in fileRaces:
        found = fileRace in raceDataStrings
        if not found:
            NEWRACES += GetMessageString(fileRace, False, hasCategory, chess)
    if len(NEWRACES) == 0:
        NEWRACES = ''
        #NEWRACES = 'No New Races'
    return NEWRACES

########################ACTUAL CODE##############################

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
#client.run(TOKEN)

async def CheckRaces(sheet, txtFile, channel, hasCategory, chess):
    changes = CompareRaces(races, txtFile, hasCategory, chess)
    races = GetRaceData(sheet, hasCategory)
    WriteRacesToFile(races, txtFile)
    if len(changes) != 0:
        for chunk in Chunks(changes, 2000):
            print(chunk)
            await client.get_channel(channel).send(chunk)
    else:
        print('no new races for ' + txtFile)
    return races

async def CheckSharcordRaces():
    sharcordRaces = CheckRaces(sharcordSheet, sharcordTxtFile, sharcordChannel, True, False)

async def CheckTestSharcordRaces():
    sharcordRaces = CheckRaces(testSheet, sharcordTxtFile, testChannel, True, False)

async def CheckChessRaces():
    chessRaces = CheckRaces(chessSheet, chessTxtFile, chessChannel, False, True)

async def CheckTestChessRaces():
    chessRaces = CheckRaces(chessSheet, chessTxtFile, testChannelTwo, False, True)

async def Main():
    while(True):
        await CheckTestSharcordRaces()
        await CheckTestChessRaces()
        time.sleep(15)


def Chunks(s, n):
    """Produce `n`-character chunks from `s`."""
    for start in range(0, len(s), n):
        yield s[start:start+n]
        
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await Main();

@client.event
async def on_message(message):
    if message.author == client.user:
       return
    print(message.author + ':' + message.content);
    if message.content.startswith('races'):
        for chunk in Chunks(RACEDATA, 2000):
            await message.channel.send(chunk)

client.run(TOKEN)
