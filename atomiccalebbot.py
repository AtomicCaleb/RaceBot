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

from time import gmtime
from time import mktime
import datetime
import time

import os
import os.path
import discord


##########################VARIABLES#################
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


#race data stuff
class Race:
    def __init__(self):
        self.data = ''
        self.time = ''
        self.row = 0
        self.commentators = []
        self.restreamer = ''
        self.runnerTimes = 'No Time Entered, No Time Entered'
        self.peopleToPing = []
        self.commentatorPinged = False
        self.restreamerPinged = False
        self.peoplePinged = False
        self.message = ''
        self.messageID = ''


sharcordRaces = []
tournamentRaces = []
chessRaces = []
scheduledRaces = []


#text files
sharcordTxtFile = 'sharcordRaces.txt'
sharcordTestTxtFile = 'testSharcordRaces.txt'
tournamentTxtFile = 'tournamentRaces.txt'
chessTxtFile = 'chessRaces.txt'
chessTestTxtFile = 'testChessRaces.txt'


# The ID and range of a sample spreadsheet.
raceDataSampleRange = '\'SHAR Rival Races\'!A2:G'
commentatorsSampleRange = '\'SHAR Rival Races\'!A2:M'
tournamentDataSampleRange = '\'SHAR 2021 ASM Tourney\'!A2:G'
tournamentCommentatorDataSampleRange = '\'SHAR 2021 ASM Tourney\'!A2:M'
chessDataSampleRange = '\Sheet1!A2:E'
chessCommentatorDataSampleRange = 'Sheet1!A2:K'

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

#Race Message Stuff
timeAfterRaceToDelete = 7200
timerAfterMessageToDelete = 10800 

commentatorPingTime = 3600
commentatorPing = '<@&596968452565106688>'

restreamerPingTime = 3600
restreamerPing = '<@&697846193400840343>'

peoplePingTime = 3600

#####################FUNCTIONS################################
def GetTimeDifferenceFromGMT(secondsSinceGMT):
    if not time:
        return 99999999
    try:
        currentTimeGMT = mktime(gmtime())
        return secondsSinceGMT - currentTimeGMT
    except:
        return 99999999

def GetRaceTime(timeString):
    #get the timezone part (last 3 characters in the string)
    length = len(timeString)
    tzString = ''
    for i in range(3):
        letter = timeString[length - (3 - i)]
        tzString += letter

    #remove the timezone from the timeString
    newTimeString = ''
    for i in range(length - 3):
        newTimeString += timeString[i]

    #get the time now that we removed the timezone
    dateTimeFormat = '%d/%m/%y | %I:%M%p '
    newTime = mktime(time.strptime(newTimeString, dateTimeFormat))
    #if it isnt a valid timzeone currently supported default to BST
    if not 'BST' in tzString and not 'GMT' in tzString:
        tzString = 'BST'

    #if its BST add an hour
    if tzString == 'BST':
        newTime -= 3600

    return newTime

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
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
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

def GetRaceData(sheet, sampleRange, hasCategory):
    values = GetSheet(sheet, sampleRange)
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
                    data = row[dateTime] + ',' + row[category] + ',' + row[runnerOne] + ',' + row[runnerTwo]
                    raceData.data = data
                    raceData.row = values.index(row)

            else:
                if row[dateTime] and row[category] and row[runnerOne] and row[runnerTwo]:
                    data = row[dateTime] + ',' + row[runnerOne] + ',' + row[runnerTwo]
                    raceData.data = data
                    raceData.row = values.index(row)
            try:    
                raceData.time = GetRaceTime(row[dateTime])
            except:
                i = 0
                #print(row[dateTime] + ' not a valid raceTime')
            
            raceDatas.append(raceData)
    return raceDatas

def GetMessageString(raceInfo, added, hasCategory, chess):
     raceString = ''
     #split up the data
     raceInfoList = raceInfo.split(',')

     #format it correctly
     if added:
         if hasCategory:
            raceString += '**•Race Scheduled** \nDate/Time: %s \nGroup: %s \nRacers: %s VS %s\nCommentators: \nRestreamer: \n' % (raceInfoList[0], raceInfoList[1], raceInfoList[2], raceInfoList[3])
         elif not chess:
            raceString += '**•Tournament Race Scheduled**\nDate/Time:%s\nCategory: ASM \nRacers: %s VS %s\nCommentators: \nRestreamer: \n' % (raceInfoList[0],raceInfoList[1], raceInfoList[2])
         else:
            raceString += '**•Race Scheduled**\nDate/Time:%s\n6 Chess Matches \nRacers: %s VS %s\nCommentators: \nRestreamer: \n' % (raceInfoList[0], raceInfoList[1], raceInfoList[2])
     else:
         if hasCategory:
            raceString += '**•Race Removed** \nDate/Time: %s \nGroup: %s \n Racers: %s VS %s' % (raceInfoList[0], raceInfoList[1], raceInfoList[2], raceInfoList[3])
         elif not chess:
            raceString += '**•Tournament Race Removed**\nDate/Time:%s \nCategory: ASM \nRacers: %s VS %s' % (raceInfoList[0], raceInfoList[1], raceInfoList[2])
         else:
            raceString += '**•Race Removed**\nDate/Time:%s \n6 Chess Matches \nRacers: %s VS %s' % (raceInfoList[0], raceInfoList[1], raceInfoList[2])
             
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
    
    global scheduledRaces
    #check the file data agaisnt race data
    for fileRace in fileRaces:
        #print('checking' + fileRace)
        #for raceData in raceDataStrings:
        #    print(raceData)
        if not fileRace in raceDataStrings:
            #if we cant find it a race has been removed
            newRace = Race()
            scheduledRaces.append(newRace)
            newRace.message = GetMessageString(fileRace, False, hasCategory, chess)

    i = 0
    #check the race data agaisnt the file
    for race in races:
        if len(race.data) == 0:
            continue
        if not race.data + '\n' in fileRaces:
            #if we cant find it a race has been added
            scheduledRaces.append(race)
            race.message = GetMessageString(race.data, True, hasCategory, chess)

async def UpdateCommentators(race, newCommentators):
    print('updating commentators')
    messageContent = ''
    messageContent = race.messageID.content
    
    newCommentatorsString = ''
    count = 0
    for commentator in newCommentators:
        if count > 0:
            newCommentatorsString += 'and '
        newCommentatorsString += commentator + ' ' 
        count += 1

    contentLines = messageContent.split('\n')
    if len(contentLines) > 4:
        contentLines[4] = 'Commentators: ' + newCommentatorsString

    newMessage = ''
    for contentLine in contentLines:
        newMessage += contentLine + '\n'
    
    try:
        await race.messageID.edit(content = newMessage)
    except:
        i = 0
    race.commentators = newCommentators 
    return race
        
async def UpdateRestreamer(race, restreamer):
    print('updating restreamer')
    #get the message contents
    content = race.messageID.content
    contentLines = content.split('\n')
    
    #split it up and change the correct part
    if len(contentLines) > 5:
        contentLines[5] = 'Restreamer: ' + restreamer
    
    #stitch it together
    newMessage = ''
    for contentLine in contentLines:
        newMessage += contentLine + '\n'
    try:
        await race.messageID.edit(content = newMessage)
    except:
        i = 0

async def CheckCommentators(races, sampleRange, sheet, hasCategory):
    #get all values from the sheet
    values = GetSheet(sheet, sampleRange)
    #set variables needed
    raceValueCount = 5 if hasCategory else 4
    commsValueCount = 7 if hasCategory else 6
    racerOneTimeRow = 3 if hasCategory else 2
    raceValues = []
    comsValues = []
    restreamValues = []
    runnerValues = []
    #go through each row and separate into 2 parts
    #TODO: move this into raceData and do both there cause we are doing
    #everything
    for row in values:
        if len(row) < raceValueCount + 1:
            continue
        racePart = ''
        comsPart = ''
        racePart += row[0]
        runnerValues.append(row[racerOneTimeRow] + ',' + row[raceValueCount])
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
    timesSplit = []
    #go through every scheduled race we have sent
    for race in scheduledRaces:
        #reset newcommentators ready for next part
        newCommentators.clear()
        #if its a part of the current set
        for i in range(len(raceValues) - 1):
            count = 0
            #get the commentators row
            commentators = ''
            #if its the correct row
            if(raceValues[i] == race.data):
                count += 1
                timesSplit = runnerValues[i]
                #races[races.index(race)].runnerTimes.clear()
                race.runnerTimes = runnerValues[i]
                #add the restreamer
                race.restreamer = restreamValues[i]
                await UpdateRestreamer(race, restreamValues[i])
                commentators = comsValues[i]
                #split up the commentators found
                commentatorsSplit = commentators.split('/')
                for split in commentatorsSplit:
                    newCommentators.append(split)
                print(race.runnerTimes)
            #print(count)
        #check everything is correct
        for commentator in newCommentators:
            print(commentator)
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
    return races

async def CheckRaceTimes(races):
    #for each message we have sent
    for raceTemp in scheduledRaces:
        for race in races:
            if race.data == raceTemp.data:
                if race.time:
                    secondsUntilGMT = GetTimeDifferenceFromGMT(race.time) 
                    if secondsUntilGMT < -timeAfterRaceToDelete:
                        raceData = race.data.split(',')
                        runnerOne = len(raceData) - 1
                        runnerTwo = len(raceData) - 2
                        #get the time delta to compare
                        winner = 0 # 0 = tie, 1 = runner one win, 2 = runner two win
                        runnerTimes = race.runnerTimes.split(',')
                        runnerOneList = runnerTimes[0].split(':')
                        runnerTwoList = runnerTimes[1].split(':')
                        #if its a single digit use highest
                        if(len(runnerOneList) == 1):
                            if runnerOneList[0] != runnerTwoList[0]:
                                winner = 1 if runnerOneList[0] > runnerTwoList[0] else 2
                        #otherwise loop through them to find lowest
                        else:
                            for i in range(len(runnerOneList)):
                                if runnerOneList[i] < runnerTwoList[i]:
                                    winner = 1
                                    break
                                elif runnerOneList[i] > runnerTwoList[i]:
                                    winner = 2 
                                    break
                        newMessage = ''
                        winnerTime = runnerTimes[0] if winner == 1 else runnerTimes[1]
                        loserTime = runnerTimes[1] if winner == 1 else runnerTimes[0]
                        winnerName = raceData[runnerOne] if winner == 2 else raceData[runnerTwo]
                        loserName = raceData[runnerTwo] if winner == 2 else raceData[runnerOne]
                        category = raceData[1] if len(raceData) < 5 or winnerName == raceData[2] or winnerName == raceData[4] else 'Tournament Race'
                        if winner == 0:
                            newMessage = '**Race Completed** (%s)\n%s [%s] (TIE!)\n%s [%s] (TIE!)' % (category, raceData[runnerOne], runnerTimes[0], raceData[runnerTwo], runnerTimes[1])
                        else:
                            newMessage = '**Race Completed** (%s)\n%s [%s] (Winner!)\n%s [%s]' % (category, winnerName, winnerTime, loserName, loserTime)
                        try:
                            await raceTemp.messageID.edit(content = newMessage)
                        except:
                            i = 0
                        scheduledRaces.pop(raceTemp)
                        await CheckRaceTimes(races)
                        return
async def CheckCommentatorPings():
    for race in scheduledRaces:
        secondsUntilGMT = GetTimeDifferenceFromGMT(race.time)
        #if we are passed the time, havent pinged, and need commentators
        if(secondsUntilGMT < commentatorPingTime and not race.commentatorPinged and len(race.commentators) < 2):
            raceDataList = race.data.split(',')
            if len(raceDataList) > 3:
                message = '%s needed in 1 hour for %s vs %s' % (commentatorPing, raceDataList[1], raceDataList[3])
                await scheduledRaces[race].messageID.channel.send(content = message, delete_after = timerAfterMessageToDelete)
                race.commentatorPinged = True

async def CheckRestreamerPings():
    for race in scheduledRaces:
        secondsUntilGMT = GetTimeDifferenceFromGMT(race.time)
        #if we are passed the time, havent pinged, and need commentators
        if(secondsUntilGMT < restreamerPingTime and not race.restreamerPinged and not race.restreamer):
            raceDataList = race.data.split(',')
            if len(raceDataList) > 3:
                message = '%s needed in 1 hour for %s vs %s' % (restreamerPing, raceDataList[1], raceDataList[3])
                await race.messageID.channel.send(content = message, delete_after = timerAfterMessageToDelete)
                race.restreamerPinged = True

async def CheckPeoplePing():
    for race in scheduledRaces:
        secondsUntilGMT  = GetTimeDifferenceFromGMT(race.time)
        print(secondsUntilGMT)
        if secondsUntilGMT < peoplePingTime and not race.peoplePinged:
            print('pinging people')
            message = ''
            for people in race.peopleToPing:
                print(people.name)
                if message:
                    message += ', '
                if people.name != 'AtomicCalebBot':
                    message += people.mention
            raceDataList = race.data.split(',')
            message +=  '\n%s vs %s is starting in an hour' % (raceDataList[2], raceDataList[3])
            print(message)
            race.peoplePinged = True
            await race.messageID.channel.send(content = message, delete_after = timerAfterMessageToDelete)


########################ACTUAL CODE##############################
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client(activity=discord.Game(name='https://github.com/AtomicCaleb/RaceBot'))
#client.run(TOKEN)
async def CheckRaces(sheet, sampleRange, comsSampleRange, txtFile, channel, hasCategory, chess):
    races = GetRaceData(sheet, sampleRange, hasCategory)
    changes = CompareRaces(races, txtFile, hasCategory, chess)
    WriteRacesToFile(races, txtFile)
    empty = True
    #go through every change
    for race in scheduledRaces:
        if race.message and not race.messageID:
            for chunk in Chunks(race.message, 2000):
                #print the change
                print(chunk)
                #update the message ID
                race.messageID = await client.get_channel(channel).send(chunk)
                await race.messageID.add_reaction('\N{eyes}')
                empty = False
    #if its empty print for debug
    if empty:
        print('no new races for ' + txtFile)

    races = await CheckCommentators(races, comsSampleRange, sheet, hasCategory)

    return races

#Dict<Race, string>
#List<Race>
async def CheckSharcordRaces():
    return await CheckRaces(sharcordSheet, raceDataSampleRange, commentatorsSampleRange, sharcordTxtFile, sharcordChannel, True, False)

async def CheckTournamentSharcordRaces():
    return await CheckRaces(sharcordSheet, tournamentDataSampleRange, tournamentCommentatorDataSampleRange, tournamentTxtFile, testChannel, True, False)

async def CheckTestSharcordRaces():
    return await CheckRaces(testSheet, raceDataSampleRange, commentatorsSampleRange, sharcordTxtFile, testChannel, True, False)

async def CheckChessRaces():
    return await CheckRaces(chessSheet, raceDataSampleRange, commentatorsSampleRange, chessTxtFile, chessChannel, False, True)

async def CheckTestChessRaces():
    return await CheckRaces(testSheetTwo, raceDataSampleRange, commentatorsSampleRange, chessTxtFile, testChannelTwo, False, True)


async def Main():
    while(True):
        #print(GetRaceTime('20/05/21 | 9:00PM GMT'))
        tournamentRaces = await CheckTournamentSharcordRaces()
        #sharcordRaces = await CheckTestSharcordRaces()
        #chessRaces = await CheckTestChessRaces()

        await CheckRaceTimes(tournamentRaces)
        #await CheckRaceTimes(chessRaces)
        #await CheckRaceTimes(sharcordRaces)

        await CheckCommentatorPings()
        await CheckRestreamerPings()
        await CheckPeoplePing()
        time.sleep(10)


def Chunks(s, n):
    """Produce `n`-character chunks from `s`."""
    for start in range(0, len(s), n):
        yield s[start:start + n]
        
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await Main()

@client.event
async def on_message(message):
    if message.author == client.user:
       return
    #print(message.author + ':' + message.content);

    print(message.content)

    if 'sharcord races' in message.content:
        for chunk in Chunks(sharcordRaces, 2000):
            await message.channel.send(chunk)

    if 'chess races' in message.content:
        for chunk in Chunks(chessRaces, 2000):
            await message.channel.send(chunk)

    if 'boat jump' in message.content and 'help' in message.content:
        await message.channel.send('https://media.discordapp.net/attachments/580364471130783744/843613945235505182/image0.png')

@client.event
async def on_reaction_add(reaction, user):
    print("on reaction")
    for race in scheduledRaces:
        if reaction.message == race.messageID:
            print(reaction.me)
            if not user in race.peopleToPing:
                print('adding to list')
                race.peopleToPing.append(user)
            
@client.event
async def on_raw_reaction_remove(payload):
    print("on reaction remove")
    for race in scheduledRaces:
        print(payload.message_id)
        if payload.message_id == race.messageID.id:
            print(payload.user_id)
            for user in race.peopleToPing:
                if user.id == payload.user_id:
                    race.peopleToPing.remove(user)
                    print(race.peopleToPing)
                    return;

client.run(TOKEN)
    