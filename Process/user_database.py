print("User Database Loaded")
#from main import *

## Only SQL Imports here and TP Client Data... 
##### SQL IMPORTS  #####
import sqlite3
import os.path
from sqlite3.dbapi2 import OperationalError
##### SQL IMPORTS  #####
from tpclient import *
from pprint import pprint


##################################################################
################   START OF OF DATABASE MAIN  ####################
##################################################################

local = (os.getenv('APPDATA'))
db_folder = "\\TouchPortal\\plugins\\TwitchExtras\\user_database.db"
the_database = local + db_folder
conn = sqlite3.connect(the_database, check_same_thread=False)   ### I turned off this check same thread stuff and was able to overcome the error ProgrammingError('SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 44420 and this is thread id 45000.')
cur = conn.cursor()

############################################################
################ Creating Table + Columns ##################
############################################################
cur.execute("""CREATE TABLE IF NOT EXISTS user_db (
            'id' INTEGER PRIMARY KEY,
            'broadcaster_type' text,
            'display_name' text,
            'login' text,
            'description' text,
            'offline_image_url' text,
            'profile_image_url' text,
            'type' text, 
            'view_count' INTEGER,
            'created_at' text,
            'follow_months' INTEGER,
            'total_messages' INTEGER, 
            'months_subscribed' INTEGER,
            'total_bits' INTEGER,
            'level' INTEGER,
            'badges' text,
            'gifted_subs' INTEGER
        )""")
conn.commit()  ### Save the Database

###     try:
###         addColumn = "ALTER TABLE user_db ADD COLUMN gifted_subs INTEGER"
###         cur.execute(addColumn)
###     except OperationalError:
###         #print("adding column issues")
###         pass

from os import path
import json

#### Loading up the Points from chat config ####
#### Loading up the Points from chat config ####
save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras')
chat_config = open(save_path +"\chat_config.json", "r")
the_chatconfig_dict = json.load(chat_config)
###paranoid close below
chat_config.close()

points_dict = the_chatconfig_dict[0]
Chat_Msg_Points = (float(points_dict.get('Chat Message Points')))
Follow_Age_Points = (float(points_dict.get('Follow Age Points')))
Sub_Months_Points = (float(points_dict.get('Sub Months Points')))
Points_Per_Bit = (float(points_dict.get('Bit Points')))
Points_Per_Level = (float(points_dict.get('Points Needed Per Level')))
Points_Per_Gifted_Sub = (float(points_dict.get('Gifted Sub Points')))
maxlevel = int(points_dict.get('Max Level'))

#### Loading up the Points from chat config ####
#### Loading up the Points from chat config ####

save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras\lists')
#### Loading VIP List File into a List to check when calculating level
vip_list_file = open(save_path +"\VIP_Chat_List.txt", "r")
with vip_list_file as f:
    lines = f.readlines()
    vip_list = []
    for line in lines:
        stripped_line = line.rstrip()
        vip_list.append(stripped_line.lower())
    f.close()
    
    ##Paranoid close 
    vip_list_file.close()

    #print("VIP LIST: ", vip_list)


### if during stream, a person chats whom is VIP and not in VIP list, they will be added to .txt file and then added to active VIP list here..
def add_vip_list(username):
    global vip_list
    vip_list.append(username)
    print("VIP LIST UPDATED: ", vip_list)



############# SAMPLE DEFAULT DICT #####################
user_dict ={
 'broadcaster_type': 'affiliate',
 'description': 'O hi there',
 'display_name': 'GitagoGaming',
 'id': 55555,
 'login': 'GitagoGaming',
 'offline_image_url': 'https://static-cdn.jtvnw.net/jtv_user_pictures/e5d9ea09-1b07-416b-b354-9d57cadfe-channel_offline_image-1920x1080.png',
 'profile_image_url': 'https://static-cdn.jtvnw.net/jtv_user_pictures/9b79dd0b-39fd-44a0-b1f0-92ac963f3-profile_image-300x300.png',
 'type': 'thisistype',
 'view_count': 893,
 'level': 99,
 'total_messages': 15,
 'created_at': "2021-06-15T21:21:08Z",
 'follow_months': 25,
 'months_subscribed': 15,
 'total_bits': 4200, 
 'badges': "vip/1,subscriber/3,bits/100",
 }
conn.commit()



###Using USER-ID to check if in DB, check if points.. etc..
def check_db(theuser, action):
    cur.execute(f'SELECT * FROM user_db WHERE id= {theuser}') 
    check_exists = (cur.fetchone())
    #print('this is the check ', check_exists)
    if not check_exists:
        pass
    elif check_exists:

        user_name = check_exists[2]
        profile_image = check_exists[6]
        #type = check_exists[7]
        views = check_exists[8]
        total_messages = check_exists[11]
        total_bits = check_exists[13]

        #print("we made it")
        if total_messages == "null":
            total_messages = 0
            #### how to update that section of database now...

    ### This is used when checking levels
    if check_exists:
        return True

    if action =="on_message":
        print("take total messages and increment it..")
        #### currently every pub message looks in DB, checks if in database, then adds..

    if not check_exists:
        print(" Person is NOT in the list")
#check_db('25296216', "ok")




#lets enter every single person into database every single time.. and when we run out of Twitch Quota, then we will worry?
def enter_user_dict(dict2):   ##dict2 refers to the user_dict sent thru from a request..
    ### Try and put user in database
    try:
        columns = ', '.join(dict2.keys())
        placeholders = ':'+', :'.join(dict2.keys())
        query = 'INSERT OR REPLACE INTO user_db (%s) VALUES (%s)' % (columns, placeholders)
        cur.execute(query, dict2)
        conn.commit()
        ### this is taking the dict and inputting it..

    except sqlite3.IntegrityError as err:
        ## If ID not Unique, then Error and lets replace it with the new info... ## Maybe  only we update if views are different perhaps save on CPU usage??       
        print("")
        print('ERROR: ', err)
        print("")
        
        current_views = (dict2['view_count']) # Shows current channel views of this person
        query = 'REPLACE INTO user_db (%s) VALUES (%s)' % (columns, placeholders)  ## we could do insert or replace above, but instead do error handling then replace
        conn.commit()

        ### DO WE NEED con.close()  ?????
       # conn.close()

enter_user_dict(user_dict) ## Do Twitch API call for user info, then use this function to enter it into DB   - before we add it.. should we calculate total points first??




################# ERROR HERE ###################
################# ERROR HERE ###################
### Trying to get calculate points to use the command followage in order to return the months followed
## It is giving a Circular Import Error   ## I instead run followage in nothing.py instead then send the total months over here..

###import twitch_api
def calculate_points(theuser, follow_age_dict, full_user_dict):
    ### Does person exist in Database?  If not.. PASS...
    cur.execute(f'SELECT * FROM user_db WHERE id= {theuser}') 
    check_exists = (cur.fetchone())

    new_follow_months = follow_age_dict.get('Total Months')
    gifted_subs = 0 ## Setting gifted subs to 0 by default here...



    ### so if this doesnt exist then lets add
    if not check_exists:
        #   If user does NOT EXIST - > Submit User Dic to DB Then Recalculate
        print("Person NOT In the Database, we are adding them now..")
        display_name = full_user_dict['display_name']
        profile_image_url = full_user_dict['profile_image_url']
        offline_image_url = full_user_dict['offline_image_url']
        view_count = full_user_dict['view_count']
        id = full_user_dict['id']
        broadcaster_type = full_user_dict['broadcaster_type']
        created_at = full_user_dict['created_at']
        description = full_user_dict['description']
        login = full_user_dict['login']
        #type = full_user_dict['type']

        for variable in ["broadcaster_type", "description", "display_name", "id", "login", "offline_image_url", "profile_image_url", "view_count", "created_at"]:
            full_user_dict[variable] = eval(variable)
            
        enter_user_dict(full_user_dict)
        calculate_points(id, follow_age_dict, full_user_dict)
        
        
    elif check_exists:
        ## Breaking down the Database info into variables
        ### Preparing to Calculate new Results
        a_dict = {}
        id = check_exists[0]
        broadcaster_type = check_exists[1]   ## these things just dont matter for calculating points...
        display_name = full_user_dict['display_name']
        login = check_exists[3]
        description = full_user_dict['description']
        offline_image_url = full_user_dict['offline_image_url']
        profile_image_url = full_user_dict['profile_image_url']
        type = check_exists[7]
        view_count = full_user_dict['view_count']
        created_at = check_exists[9]
        #follow_months = check_exists[10]
        follow_months = new_follow_months
        total_messages = check_exists[11]
        months_subscribed = check_exists[12]   ### this is constantly updated from chat messages/badges
        total_bits = check_exists[13]
        level = check_exists[14]
        badges = check_exists[15]



        import twitch_api  
    ###  Importing Points config and Gifted Subs Dictionary  -  #gifted_sub_dict = plug_config.full_config.Gift_Subs
        import plug_config
        ### getting persons profile image and saving to local folder
        twitch_api.get_profile_image(profile_image_url)


     ###CALCULATING BITS PERSON HAS DONTED INTO SCORE WITH API CALL -  IF imported here, it gets around the circular dependency bs    
        new_total_bits = twitch_api.bits_person(1, id)
    #### Bits Badge if Bits
        bits_badge_path = None #setting path to None incase no bits    
        ## making sure its not None, if so, then make the score 0.
        if new_total_bits == None:
            bits_given_score = 0
            new_total_bits = 0
            #print(f"{display_name} has 0 bits")
        elif new_total_bits != 0:
            bits_given_score = float(new_total_bits) * Points_Per_Bit
           # print(f"{display_name} has {new_total_bits} bits")

        ### If User has bits, lets find proper png
            png_file = [1, 100, 1000, 5000, 10000, 25000, 50000, 75000, 100000]
            for item in png_file:
                if int(new_total_bits) >= int(item):
                    bits_badge_path = f"{item}_bits.png "


    ### Take Follow Age Dict Sent and Sort it - Delete entries if they are 0..
        the_list = ["diff_year", "diff_month", "diff_day", "diff_hour", "diff_min"]
        for k in list(follow_age_dict.keys()):
            if follow_age_dict[k] == 0:
                del follow_age_dict[k]
        
        #for everything left in dict, lets see if its greater than 1, if so pluralize it..       
        new_months_dict = {}   
        for item in follow_age_dict.keys():
            if item in the_list:
                if follow_age_dict[item] > 1:
                    split_i = item.split("_")
                    split_i = split_i[1]+"s"
                    new_months_dict[item] = str(follow_age_dict[item])+" "+split_i
                else:
                    split_i = item.split("_")
                    split_i = split_i[1]
                    new_months_dict[item] = str(follow_age_dict[item])+" "+split_i

    ## Looping thru newly created dict for items and creating final clean string           
        follow_status = ""
        final_string =""
        for item in new_months_dict:
            final_string = final_string + new_months_dict[item]+" "
    ## Figuring out if they are actually following based on follow months/days etc..
        if final_string == "":
            print("NOT FOLLOWING")
            follow_status = "False"
            final_string = "0"
        else:
            print(f"Following for {final_string}")
            follow_status = "True"

    ##        CALCULTING THE POINTS        ##

    ## Messages   
        if total_messages == None:
            chat_msg_score = 0
            total_messages=0
        else: 
            chat_msg_score = float(total_messages) * Chat_Msg_Points
            #print("\nTotal messages: ", total_messages, " Points: ", Chat_Msg_Points, "Total Score: ", chat_msg_score,"\n", )

    ## Follow Months
        if follow_months == None:
            follow_age_score = 0
            follow_months = 0               
        elif follow_months >= 0:
            follow_age_score = float(follow_months) * Follow_Age_Points

    ## Months Subscribed
        if months_subscribed == None:
            months_subbed_score = 0
            months_subscribed = 0
            ## Calculate Points for Total Months Subscribed           
        else:
            months_subbed_score = float(months_subscribed) * Sub_Months_Points

    ## Gifted Subs
        gifted_sub_status = False
        gifted_subs = None  # setting gifted_subs to none so if it doesnt get found in if check.. then we ok   
        if display_name in plug_config.full_config.Gift_Subs:
            gifted_subs = plug_config.full_config.Gift_Subs.get(display_name)
            gifted_sub_status = True

        if gifted_subs:
            gifted_sub_score = float(gifted_subs) * Points_Per_Gifted_Sub
            print(f"{display_name} has {gifted_subs} gifted subs - Score: {gifted_sub_score}")

        ## Figuring out what gifted sub badge to assign.
            png_file = [1, 5, 10, 25, 50, 100, 250, 50000, 500, 1000]
            for item in png_file:
                if int(gifted_subs) >= int(item):
                    #print(f"{display_name} | {gifted_subs} is equal or greater than {item}" )
                    gifted_subs_path = f"{item}_sub_gifts.png "
    #just making double sure its false if not in gifted subs
        elif not gifted_subs:
            gifted_sub_status = False
            gifted_subs = 0
            gifted_sub_score = 0


        ## Caclulate Total Score
        total_score = chat_msg_score + follow_age_score + months_subbed_score + bits_given_score + gifted_sub_score

        ## Calculate Level based on Points needed per level
        level = total_score / Points_Per_Level

        # Turning into a String so can split the decimal point
        strlevel = str(level)

        #Getting Percentages and Stuff for Level Card Data
        xptolevel = strlevel.split('.')[1]
        xptolevel = xptolevel[0:2]
        level_percentages = 100 - int(xptolevel)

        ## Turning it into a single digit to the 'level' bar graphic.. 1-10 determines where the level car png is at..
        str_level_percentages = str(level_percentages)
        single_digit = str_level_percentages[0]

        level_percentages = str(level_percentages)
        level = (round(level))

        if level == 0:
            level = 1
        ### Allows user to set max level in config
        if level >= maxlevel:
            level = f"MAX"
        
        rounded_score = round(total_score)

        vip_status = False
        subscriber_check = False
        mod_status = False
        
    ### We still have to get total months subscribed data from chat messages, no other way currently.
    ### in future can use event sub to constantly update when data comes in from a resub and other such things..
        if badges != None:
            print("[BADGES]", badges)
            if "subscriber" in badges:
                chunked = (badges.split(','))
                for item in chunked:
                    ### sorting thru badges and figuring out what subscriber month badge they have, using info below to assign an image
                    if "subscriber" in item:
                        split_sub = (item.split('/')[1])
                        subscriber_check = True

            if "vip" in badges:
                vip_status = True
            if "moderator" in badges:
                mod_status = True
            if "bits" in badges:
                pass  ## bits badge is made by calculating total bits above. line 260ish
    
        

        ### After we sorted the Badges, now we check if true/false..        
        if subscriber_check == True:
            save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras\images\badges\subscriber_badges\\')
            badge_image_path = save_path + split_sub+".png"
            TPClient.stateUpdate(PLUGIN_ID + ".state.levelcard.sub_badge", badge_image_path)
        elif subscriber_check == False:
            TPClient.stateUpdate(PLUGIN_ID + ".state.levelcard.sub_badge", "NONE")


        if gifted_sub_status == True:
            save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras\images\badges\sub_gifter_badges\\')
            badge_image_path = save_path + gifted_subs_path
            TPClient.stateUpdate(PLUGIN_ID + ".state.levelcard.sub_gifter_badge", badge_image_path)
        if gifted_sub_status == False:
            TPClient.stateUpdate(PLUGIN_ID + ".state.levelcard.sub_gifter_badge", "NONE")


        if bits_badge_path:
            save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras\images\badges\bit_badges\\')
            badge_image_path = save_path +bits_badge_path
            TPClient.stateUpdate(PLUGIN_ID + ".state.levelcard.user_bits_badge", badge_image_path)
        elif not bits_badge_path:
            TPClient.stateUpdate(PLUGIN_ID + ".state.levelcard.user_bits_badge", "NONE")

        
        ### VIPS that talk in chat which are not in the VIP list already will be added via chat_bot.py
        if display_name.lower() in vip_list: 
            vip_status = True
        elif not display_name.lower() in vip_list:
            vip_status = False

        if badges == None:
            badges = "No Badges For User."


        ## This is RE-ENTERING The Users info Back into the Database with updated info.
        for variable in ["broadcaster_type", "description", "display_name", "id", "login", "offline_image_url", "profile_image_url", 
                        "type", "view_count", "total_bits", "total_messages", "created_at", "months_subscribed", "level", "follow_months", "badges"]:
            a_dict[variable] = eval(variable)
            
        enter_user_dict(a_dict)

## XPTOLEVEL is actually HOW MUCH into level they are
## LEVEL PERCENTAGE IS HOW MUCH PERCENT TO LEVEL
        TPClient.stateUpdateMany([
    {
        "id": 'gitago.twitchextras.state.levelcard.name',
        "value": display_name
    },
    {
        "id": 'gitago.twitchextras.state.levelcard.level',
        "value": str(level)
    },
    {
        "id": 'gitago.twitchextras.state.levelcard.percentage',
        "value": str(xptolevel)
    },
    {
        "id": 'gitago.twitchextras.state.levelcard.percentage_to_level',
        "value": str(level_percentages)
    },
    {
        "id": 'gitago.twitchextras.state.levelcard.bar',
        "value": str(single_digit)
    },
    {
        "id": 'gitago.twitchextras.state.levelcard.vip_status',
        "value": str(vip_status)
    },
    {
        "id": 'gitago.twitchextras.state.levelcard.mod_status',
        "value": str(mod_status)
    },
    {
        "id": 'gitago.twitchextras.state.levelcard.follow_status',
        "value": str(follow_status)
    },
    {
        "id": 'gitago.twitchextras.state.levelcard.profilepic',
        "value": str(profile_image_url)
    },
    {
        "id": 'gitago.twitchextras.state.levelcard.bits_donated',
        "value": str(new_total_bits)
    },
    {
        "id": 'gitago.twitchextras.state.levelcard.follow_months',
        "value": str(follow_months)
    },
   {
       "id": 'gitago.twitchextras.state.levelcard.full_follow_age',
       "value": str(final_string)
   },
    {
        "id": 'gitago.twitchextras.state.levelcard.sub_months',
        "value": str(months_subscribed)
    },
    {
        "id": 'gitago.twitchextras.state.levelcard.gifted_subs',
        "value": str(gifted_subs)
    },
    {
        "id": 'gitago.twitchextras.state.levelcard.total_messages',
        "value": str(total_messages)
    },
    {
        "id": 'gitago.twitchextras.state.levelcard.total_score',
        "value": str(rounded_score)
    },
    ])


        print("Level:", level, "Score: ", total_score)
        print(display_name, "is currently Level", level, "with", xptolevel, "left to level" )

#calculate_points("479000324")



def sql_data_to_list_of_dicts(select_query):
      """Returns data from an SQL query as a list of dicts."""
      try:
          con = sqlite3.connect(the_database, check_same_thread=False)
          con.row_factory = sqlite3.Row
          things = con.execute(select_query).fetchall()
          unpacked = [{k: item[k] for k in item.keys()} for item in things]
          return unpacked
      except Exception as e:
          print(f"Failed to execute. Query: {select_query}\n with error:\n{e}")
          return []
      finally:
          con.close()



def get_top_5_leaders(returned_data):
    import operator
    ### Looping thru Dict, if its NONE then make 0.. do this for each..

### Top 5 Message Senders
    for dict in returned_data:
        if dict['total_messages'] == None:
            dict['total_messages'] = 0
    top_message_senders = sorted(returned_data, key=operator.itemgetter('total_messages'), reverse=True)
    top_5_message_senders = (top_message_senders[:5])
    count=1
    print("TOP 5 MESSAGE SENDERS")
    for person in top_5_message_senders:
         print(f"[#{count}] {person['display_name']} - {person['total_messages']} messages")
         count = count + 1
  
  
### Top 5 Levels
    for dict in returned_data:
        if dict['level'] == None:
            dict['level'] = 0
    top_levels = sorted(returned_data, key=operator.itemgetter('level'), reverse=True)
    top_5_levels = (top_levels[:5])
    count=1
    print("TOP 5  BY LEVEL")
    for person in top_5_levels:
        print(f"[#{count}] {person['display_name']} - Level:{person['level']}")
        count = count + 1
  
  
### Top 5 Total Bits Given  ### We can use leaderboard API for this?
    for dict in returned_data:
        if dict['total_bits'] == None:
            dict['total_bits'] = 0
    top_bit_senders = sorted(returned_data, key=lambda x: x['total_bits'], reverse=True)
    top_5_bit_senders = (top_bit_senders[:5])
    count = 1
    print("TOP 5 BIT SENDERS")
    for person in top_5_bit_senders:
        print(f"[#{count}] {person['display_name']} - {person['total_bits']}")
        count = count + 1

#### This is how we are getting a list of dictionaries from the database to use for sorting top 5..
#########        QUERY = "SELECT * FROM user_db"
##  returned_data = sql_data_to_list_of_dicts(QUERY)
##  get_top_5_leaders(returned_data)
#### https://note.nkmk.me/en/python-dict-list-sort/
### SQlite tutorial stuffs  https://pynative.com/python-sqlite-delete-from-table/








### Commit/Save Database   # this is not really needed but keeping for now incase something uses it.. lol.. 
def commit():
    conn.commit()
################################## END OF DATABASE MAIN #############################
################################## END OF DATABASE MAIN #############################


