import discord
import time
import os.path
import os
import configparser

client = discord.Client()

global version

# Setting the start time

global startTimeStr
startTime = time.gmtime(time.time())
startTimeStr = str(startTime[3]) + ":" + str(startTime[4]) + ":" + str(startTime[5]) + " " + str(startTime[2]) + "/" + str(startTime[1]) + "/" + str(startTime[0])

# Makes the global variables

global story
global recently_submitted
global people_between
global moderator_roles
global word_game_channel
global help_string
global info_string
global paused
global saved_stories
story = []
recently_submitted = []
people_between = 2
moderator_roles = []
word_game_channel = ""
help_string = """**Help for Word Game Bot:**


!help - displays this help message
!info - displays info about the bot
!current - writes out the current story
!load - loads a given story
!list - Lists the current stories


** - Moderator Commands -**


!resetstory - resets the current story
!moderatorroles - Manages moderator roles
!wordgamechannel - Sets the channel for this bot to use
!save - Saves a story
!pause - Toggles pause

Use !help [command] for more information
"""
info_string = """
Word Game Bot was developed by MrRiptide#7025
paused = "false"
saved_stories = []


# Logging into the bot

tokenFile = open("token", "r")
token = tokenFile.readline().strip("\t\n\r")
# print(token)
print(tokenFile)
tokenFile.close()


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")
    print("This process of the bot was started at " + startTimeStr)


@client.event
async def on_message(message):
    global story
    global recently_submitted
    global people_between
    global moderator_roles
    global word_game_channel
    global help_string
    global info_string
    global paused
    if str(message.author.bot) == "False":
        load(message.server.id)
        if message.content.startswith("*") or message.content.startswith("("):
            return
        if message.content.startswith("!"):
            if message.content.startswith("!help"):
                parts = message.content.split(" ")
                if len(parts) == 1:
                    await client.send_message(message.channel, help_string)
                elif len(parts) == 2:
                    await client.send_message(message.channel, command_help(parts[1]))
                else:
                    await client.send_message(message.channel, "Invalid Syntax, please use !help help for the correct syntax")
            if message.content.startswith("!list"):
                if saved_stories[0] != "":
                    await client.send_message(message.channel, """Saved Stories:
                    """ + ", ".join(saved_stories))
                    print(saved_stories)
                else:
                    await client.send_message(message.channel, "There are no saved stories at this time.")
            if message.content.startswith("!info"):
                await client.send_message(message.channel, info_string)
            if message.content.startswith("!pause"):
                if [moderator_roles[x] for x in range(len(moderator_roles))] in [y.name.lower() for y in message.author.roles] or message.author.id == message.server.owner.id:
                    paused = "true"

            if message.content.startswith("!load"):
                parts = message.content.split(" ")
                if len(parts) == 2:
                    await client.send_message(message.channel, load_story(message.server.id, parts[1]))
                else:
                    await client.send_message(message.channel, "Incorrect syntax, use !help load for the correct syntax")
            if message.content.startswith("!resetstory"):
                if [moderator_roles[x] for x in range(len(moderator_roles))] in [y.name.lower() for y in message.author.roles] or message.author.id == message.server.owner.id:
                    story = []
                    save()
                    await client.send_message(message.channel, "The story has been reset")
            if message.content.startswith("!moderatorroles"):
                if [moderator_roles[x] for x in range(len(moderator_roles))] in [y.name.lower() for y in message.author.roles] or message.author.id == message.server.owner.id:
                    parts = message.content.split(" ")
                    if len(parts) == 1:
                        await client.send_message(message.channel, "Incorrect syntax, use !help moderatorroles for the correct syntax")

                    if parts[1] == "add" and len(parts) == 3:
                        if "," in parts[2]:
                            await client.send_message(message.channel, 'Moderator Role cannot contain ","')
                        else:
                            moderator_roles.append(parts[2])
                            if moderator_roles[0] == "":
                                moderator_roles.pop(0)
                            await client.send_message(message.channel, "The role " + parts[2] + " is now a moderator role")
                    elif parts[1] == "delete" and len(parts) == 3:
                        moderator_roles.remove(parts[2])
                        await client.send_message(message.channel, "The role " + parts[2] + " is no longer a moderator role")
                    elif parts[1] == "list" and len(parts) == 2:
                        try:
                            await client.send_message(message.channel, ", ".join(moderator_roles))
                        except discord.errors.HTTPException:
                            await client.send_message(message.channel, "There are currently no moderator roles")
                    else:
                        await client.send_message(message.channel, "Incorrect syntax, use !help moderatorroles for the correct syntax")
            if message.content.startswith("!wordgamechannel"):
                if [moderator_roles[x] for x in range(len(moderator_roles))] in [y.name.lower() for y in message.author.roles] or message.author.id == message.server.owner.id:
                    word_game_channel = message.channel.id
                    await client.send_message(message.channel, "Set this channel as the channel for the word game!")
                else:
                    await client.send_message(message.channel, "You do not have sufficient permissions!")
            if message.content.startswith("!current"):
                print(story)
                print(str(story))
                await client.send_message(message.channel, form_story())
            if message.content.startswith("!save"):
                print("Starting Save Process")
                if [moderator_roles[x] for x in range(len(moderator_roles))] in [y.name.lower() for y in message.author.roles] or message.author.id == message.server.owner.id:
                    parts = message.content.split(" ")
                    print(str(len(parts)))
                    if len(parts) != 2:
                        print("Error: bad syntax")
                        await client.send_message(message.channel, 'Be sure to use the correct syntax: "!save <Story Name>"')
                    else:
                        if "," in parts[1]:
                            await client.send_message(message.channel, 'The story name cannot contain a ","')
                            return
                        if not os.path.isdir("./servers/" + message.server.id + "/stories/"):
                            print("Stories folder does not exist!")
                            if not os.path.isdir("./servers/" + message.server.id + "/"):
                                print("Server folder does not exist!")
                                os.mkdir("./servers/" + message.server.id + "/")
                            os.mkdir("./servers/" + message.server.id + "/stories/")
                        if os.path.isfile("./servers/" + message.server.id + "/stories/" + parts[1] + ".txt"):
                            print("The story already exists!")
                            await client.send_message(message.channel, "That story already exists!")
                        else:
                            print("File creation started")
                            temp_file = open("./servers/" + message.server.id + "/stories/" + parts[1] + ".txt", "w+")
                            temp_file.write(form_story())
                            await client.send_message(message.channel, "File successfully saved")
                            saved_stories.append(parts[1])
                            if saved_stories[0] == "":
                                saved_stories.pop(0)
                            story = []
#                            print("File successfully saved")
                            temp_file.close()
                else:
                    await client.send_message(message.channel, "You do not have sufficient permissions!")
        elif message.channel.id == word_game_channel and paused == "false":
            words = message.content.split(" ")
#            if message.author.id in recently_submitted:
#                await client.delete_message(message)
#                await client.send_message(message.channel, "Please wait for at least " + str(people_between) + " people to contribute before you contribute to the story again!")
#                return
            over_length = len(words) > 4
            is_four = len(words) == 4 and "." not in words
            under_length = len(words) < 3
            if over_length or is_four or under_length:
                await client.delete_message(message)
                await client.send_message(message.channel, "Please keep your messages to the appropriate size!")
                return
            recently_submitted.append(message.author.id)
            if len(recently_submitted) > people_between:
                recently_submitted.pop(0)
#            print(len(story))
#            print(story)
#            print("testing for an empty first line")
            story.append(str(message.content))
        save(message.server.id)


def form_story():
#    print("Forming Story")
    story_string = " ".join(story)
#    print(story)
#    print("Story: " + str(story))
#    print("Story_string: " + story_string)
    return story_string
#    x = 0
#    while x < len(story_list):
#        x += 1


def save(server_id):
    print("Saving Story")
    global story
    global recently_submitted
    global people_between
    global moderator_roles
    global word_game_channel
    global paused
    global saved_stories
    global version
    print(story)
    config = configparser.ConfigParser()
    config["Saved"] = {"Saved Stories": ",".join(saved_stories)}
    with open("./servers/" + server_id + "/config.yml", "w") as configfile:
        config.write(configfile)
    temp = open("./servers/" + server_id + "/current_story.txt", "w+")
#    print("\n".join(story))
    temp.write("\n".join(story))
    temp.close()


def load(server_id):
    if os.path.isdir("./servers/" + server_id + "/"):
        print("Loading Story")
        global story
        global recently_submitted
        global people_between
        global moderator_roles
        global word_game_channel
        global paused
        global saved_stories
        config = configparser.ConfigParser()
        config.read("./servers/" + server_id + "/config.yml")
            word_game_channel = config["General"]["Channel"]
            moderator_roles = config["General"]["Moderator Roles"].split(",")
            paused = config["General"]["Paused"]
            saved_stories = config["Saved"]["Saved Stories"].split(",")
            temp = open("./servers/" + server_id + "/current_story.txt", "a+")
            temp.seek(0, 0)
            story = []
            for line in temp:
        #        print(line)
                story.append(line.strip("\n"))
                if story[0] == "":
                    story.pop(0)
            temp.close()
        else:
            try:
                word_game_channel = config["General"]["Channel"]
            except KeyError:
                word_game_channel = ""
            try:
                moderator_roles = config["General"]["Moderator Roles"]
            except KeyError:
                moderator_roles = []
            try:
                paused = config["General"]["Paused"]
            except KeyError:
                paused = "false"
            try:
                saved_stories = config["Saved"]["Saved Stories"]
            except KeyError:
                saved_stories = []
            save(server_id)
            temp = open("./servers/" + server_id + "/current_story.txt", "a+")
            temp.seek(0, 0)
            story = []
            for line in temp:
                #        print(line)
                story.append(line.strip("\n"))
                if story[0] == "":
                    story.pop(0)
            temp.close()
    else:
        story = []
        recently_submitted = []
        people_between = 2
        moderator_roles = []
        word_game_channel = ""
        paused = "false"
        saved_stories = []
        save(server_id)


def load_story(server_id, story_to_load):
    if os.path.isfile("./servers/" + server_id + "/stories/" + story_to_load + ".txt"):
        temp = open("./servers/" + server_id + "/stories/" + story_to_load + ".txt")
        for line in temp:
            story = line
        return(story)


def command_help(command):
    if command == "help":
        return("""Usage: "!help [command]"
        Returns the help for the given command.""")
    elif command == "info":
        return("""Usage: "!info"
        Returns the info about the bot.""")
    elif command == "current":
        return("""Usage: "!current"
        Returns the currently active story.""")
    elif command == "load":
        return("""Usage: "!load [story]"
        Returns the requested story.
        Note: Will fail if story does not exist""")
    elif command == "list":
        return("""Usage: "!list"
        Lists all the saves stories.""")
    elif command == "resetstory":
        return("""Usage: "!resetstory"
        Resets the current story.
        Note: Requires moderator privileges
        WARNING: Story cannot be recovered""")
    elif command == "moderatorroles":
        return("""Usage: "!moderatorroles [add, remove, list] [role]"
        Manages roles marked as moderator roles.
        Note: Requires moderator privileges""")
    elif command == "wordgamechannel":
        return("""Usage: "!wordgamechannel"
        Sets the current channel as word game channel.
        Note: Requires moderator privileges""")
    elif command == "save":
        return("""Usage: "!save [story_name]"
        Saves the current story as a loadable story.
        Warning: Will fail if story already exists.
        Note: Requires moderator privileges""")
    elif command == "pause":
        return("""Usage: "!pause"
        Toggles pause.
        Warning: When paused, the story will not be recorded.
        Note: Requires moderator privileges""")


client.run(token)
