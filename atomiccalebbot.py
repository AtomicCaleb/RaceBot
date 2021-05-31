# bot.py
##################IMPORTS#######################################
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


##########################VARIABLES#################
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


#race data stuff
class Race:
    data = ''
    raceTime = time.gmtime
    row = 0
    commentators = []

sharcordRaces = []
chessRaces = []

raceMessages = {}

#text files
sharcordTxtFile = 'sharcordRaces.txt'
sharcordTestTxtFile = 'testSharcordRaces.txt'
chessTxtFile = 'chessRaces.txt'
chessTestTxtFile = 'testChessRaces.txt'


# The ID and range of a sample spreadsheet.
raceDataSampleRange = 'A2:E'
commentatorsSampleRange = 'A2:H'

#channels
sharcordChannel = 847495184660955146
chessChannel = 827714631714734160
testChannel = 382486010417643530
testChannelTwo = 848165475925229568

#google sheets
testSheet = '1IM24hRS_giIC5OcNNGBrHfwIZpbOcUyUURgt-q4913w'
testSheetTwo = '18AnEII0BIMht0-eZn3-eHqWsqav8LbRmaFH_6T-H4gM'
sharcordSheet = '1HB6LujCo6R2XeIVrWYdAZ8gQkA7qWrTF9QQlAWblizY'
chessSheet = '1QAFp_BOB1j_0v_8S6ubhAITvKZru0mcZv_amgvpbbYc'


#####################FUNCTIONS################################

def GetRaceTime(timeString):
    dateTimeFormat = '%d/%m/%y | %H:%M%P %Z'
    return datetime.strptime(timeString, dateTimeFormat)

def WriteRacesToFile(races, fileName):
    with open(fileName, 'w') as f:
        for race in races:
            f.write(race.data + '\n')

def WriteExtrasToFile(races, fileName):
    with open(fileName, 'w') as f:
        for race in races:
            if race.commentators:
                print(race.commentators)
            commentators = race.data
            for commentator in race.commentators:
                commentators += '|' + commentator
            commentators += '\n'
            f.write(commentators)

def GetSheet(sheetToUse, sampleRange):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet."""
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
                                range=sampleRange).execute()
    return result.get('values', [])

def GetRaceData(sheet, hasCategory):
    values = GetSheet(sheet, raceDataSampleRange)
    raceDatas = []
    
    if not values:
        print('No data found.')
    else:
        #get where all the data 'should' be
        dateTime = 0
        category = 1
        runnerOne = 2
        runnerTwo = 4
        rowsNeeded = 4
        #then fix it
        if not hasCategory:
            runnerOne -= 1
            runnerTwo -= 1
            rowsNeeded -= 1

        for row in values:
        #if there isnt enoughdata dont bother
            raceData = Race()
            if len(row) < rowsNeeded:
                continue
            #update it again
            if len(row) < rowsNeeded - 1:
                runnerTwo -= 1

            #add the data based on hasCategory
            if hasCategory:
                if row[dateTime] and row[category] and row[runnerOne] and row[runnerTwo]:
                    data = row[dateTime] + ',' + row[category] + ',' + row[runnerOne] +',' + row[runnerTwo]
                    raceData.data = data
                    raceData.row = values.index(row)

            else:
                if row[dateTime] and row[category] and row[runnerOne] and row[runnerTwo]:
                    data = row[dateTime] +',' + row[runnerOne] +',' + row[runnerTwo]
                    raceData.data = data
                    raceData.row = values.index(row)

            raceDatas.append(raceData)
    return raceDatas

def GetMessageString(raceInfo, added, hasCategory, chess):
     raceString = ''
     #split up the data 
     raceInfoList = raceInfo.split(',')

     #format it correctly
     headerPart = '**New Race Scheduled**' if added else '**Race Removed**'
     raceString += headerPart 
     raceString += '\n Date/Time: ' + raceInfoList[0]
     if hasCategory:
        raceString += '\n Category: %s \n Racers: %s VS %s\n Commentators: \n Restreamer: \n' % (raceInfoList[1], raceInfoList[2], raceInfoList[3])
     elif not chess:
        raceString += '\n Tournament Race \n Racers: %s VS %s\n Commentators: \n Restreamer: \n' % (raceInfoList[1], raceInfoList[2])
     else:
        raceString += '\n 6 Chess Matches \n Racers: %s VS %s\n Commentators: \n Restreamer: \n' % (raceInfoList[1], raceInfoList[2])
         
    #return the formatted string for use
     return raceString


def CompareRaces(races, txtFile, hasCategory, chess):
    #get both datas
    with open(txtFile) as f:
        fileRaces = f.readlines()
    raceDataStrings = []
    #get the info data
    for race in races:
        raceDataStrings.append(race.data + '\n')

    i = 0
    NEWRACES = {}
   
    #check the race data agaisnt the file
    for race in races:
        if len(race.data) == 0:
            continue
        if not race.data + '\n' in fileRaces:
            #if we cant find it a race has been added
            NEWRACES[race] = GetMessageString(race.data, True, hasCategory, chess)
         
    #check the file data agaisnt race data
    for fileRace in fileRaces:
        if not fileRace in raceDataStrings:
            #if we cant find it a race has been removed
            NEWRACES[fileRace] = GetMessageString(fileRace, False, hasCategory, chess)
    return NEWRACES

async def UpdateCommentators(race, newCommentators):
    print('updating commentators')
    messageContent = ''
    if raceMessages[race]:
        messageContent = raceMessages[race].content
    
    newCommentatorsString = ''
    for commentator in newCommentators:
        newCommentatorsString += commentator + ' ' 

    contentLines = messageContent.split('\n')
    if len(contentLines) > 4:
        contentLines[4] = 'Commentators: ' + newCommentatorsString

    newMessage = ''
    for contentLine in contentLines:
        newMessage += contentLine + '\n'
    
    if raceMessages[race]:
        await raceMessages[race].edit(content = newMessage)
    
    race.commentators = newCommentators 
    return race
        
async def UpdateRestreamer(race, restreamer):
    print('updating restreamer')
    #get the message contents
    content = raceMessages[race].content
    contentLines = content.split('\n')
    
    #split it up and change the correct part
    if len(contentLines) > 5:
        contentLines[5] = 'Restreamer: ' + restreamer
    
    #stitch it together
    newMessage = ''
    for contentLine in contentLines:
        newMessage += contentLine + '\n'

    await raceMessages[race].edit(content = newMessage)

async def CheckCommentators(races, sheet, hasCategory):
    #get all values from the sheet
    values = GetSheet(sheet, commentatorsSampleRange)
    #set variables needed
    raceValueCount = 5 if hasCategory else 4
    commsValueCount = 7 if hasCategory else 6
    racerOneTimeRow = 3 if hasCategory else 2
    raceValues = []
    comsValues = []
    restreamValues = []
    #go through each row and separate into 2 parts
    #TODO: move this into raceData and do both there cause we are doing everything
    for row in values:
        if len(row) < raceValueCount + 1:
            continue
        racePart = ''
        comsPart = ''
        racePart += row[0]
        comsPart += row[raceValueCount]
        #add the restreamer part if its there
        if len(row) > commsValueCount:
            restreamValues.append(row[commsValueCount])
        #loop through each part of the row
        for i in range(len(row) - 1):
            #check if its a race part
            if i + 1 < raceValueCount and i + 1 != racerOneTimeRow:
                racePart += ',' + row[i + 1]
            #check if its a comms part
            elif i + 1 > raceValueCount and i + 1 < commsValueCount:
                comsPart += row[i + 1]
        raceValues.append(racePart)
        comsValues.append(comsPart)

    newCommentators = []
    #go through every scheduled race we have sent
    for race in raceMessages:
        #reset newcommentators ready for next part
        newCommentators.clear()
        #if its a part of the current set
        if race in raceMessages:
            for i in range(len(raceValues) - 1):
                #get the commentators row
                commentators = ''
                if(raceValues[i] == race.data):
                    #add the restreamer
                    if restreamValues:
                        await UpdateRestreamer(race, restreamValues[i])
                    commentators = comsValues[i]
                    #split up the commentators found
                    commentatorsSplit = commentators.split('/')
                    for split in commentatorsSplit:
                        newCommentators.append(split)
        
        #check everything is correct
        for commentator in newCommentators:
            print (commentator)
        if len(newCommentators) < 1:
            continue
        
        await UpdateCommentators(race, newCommentators)
#        if race in races:
#            print('race in races')
#            #if it is update commentators
#            index = 0
#            if races.index(race):
#                index = races.index(race)
#            races[index] = await UpdateCommentators(race, newCommentators)
#    return races

########################ACTUAL CODE##############################

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
#client.run(TOKEN)


async def CheckRaces(sheet, txtFile, channel, hasCategory, chess):
    races = GetRaceData(sheet, hasCategory)
    changes = CompareRaces(races, txtFile, hasCategory, chess)
    WriteRacesToFile(races, txtFile)
    empty = True
    #go through every change
    for change in changes:
        for chunk in Chunks(changes[change], 2000):
            #print the change
            print(chunk)
            #update the message ID
            if type(change) != type(' '):
                raceMessages[change] = await client.get_channel(channel).send(chunk)
            else:
               await client.get_channel(channel).send(chunk)
            empty = False
    #if its empty print for debug
    if empty:
        print('no new races for ' + txtFile)

    await CheckCommentators(races, sheet, hasCategory)
    #races = await CheckCommentators(races, sheet, hasCategory)
    #WriteExtrasToFile(races)

    return races

async def CheckSharcordRaces():
    return await CheckRaces(sharcordSheet, sharcordTxtFile, sharcordChannel, True, False)

async def CheckTestSharcordRaces():
    return await CheckRaces(testSheet, sharcordTxtFile, testChannel, True, False)

async def CheckChessRaces():
    return await CheckRaces(chessSheet, chessTxtFile, chessChannel, False, True)

async def CheckTestChessRaces():
    return await CheckRaces(testSheetTwo, chessTxtFile, testChannelTwo, False, True)


async def Main():
    while(True):
        sharcordRaces = await CheckTestSharcordRaces()
        chessRaces = await CheckTestChessRaces()
        time.sleep(10)


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
    #print(message.author + ':' + message.content);
    
    if message.content.startswith('sharcord races'):
        for chunk in Chunks(sharcordRaces, 2000):
            await message.channel.send(chunk)

    if message.content.startswith('chess races'):
        for chunk in Chunks(chessRaces, 2000):
            await message.channel.send(chunk)

client.run(TOKEN)
