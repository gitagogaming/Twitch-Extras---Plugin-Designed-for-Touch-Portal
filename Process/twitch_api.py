
############## TWITCH API IMPORTS  ###############
from logging import error, exception
from attr.converters import optional

from requests.models import Response    ## Dont Think I'm using this at all

from twitchAPI.oauth import UserAuthenticator
from twitchAPI.oauth import validate_token, refresh_access_token
from twitchAPI.twitch import Twitch
from twitchAPI.pubsub import PubSub
from twitchAPI.types import AuthScope, AutoModAction, MissingScopeException, UnauthorizedException, TwitchAPIException, PredictionStatus
from uuid import UUID

from tpclient import *

from dateutil.relativedelta import relativedelta
from datetime import datetime
import time

from pprint import pprint
from os import path
import json
import re
import requests


## get profile image function to download+ save file locally
from PIL import Image
from requests.models import HTTPError
import urllib.request 


##### Importing Other PY Files for Plugin #######
from user_database import enter_user_dict    ### This is conflicting with user_database.py having to import followage_months here... why circular dependcy if only improting the ONE command?



#### ------------ LOAD CONFIG FILE, CHECK IF 


IS VALID ------------------ #####
#### ------------ LOAD CONFIG FILE, CHECK IF TOKEN IS VALID ------------------ #####

try:
    save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras')
    a_file = open(save_path +"\main_config.json", "r")
    the_config = json.load(a_file)
    a_file.close()
    current_token = the_config.get('Current Token')
    a_refresh_token = the_config.get('Refresh Token')
    the_broadcaster_id = the_config.get('Broadcaster ID')
    broadcaster_username = the_config.get('Broadcaster Username')

except (FileNotFoundError, IOError):
    fullerror = "Load Config Auth: "+ str(IOError)
    print(fullerror)
    print("Wrong file or file path")

#### ------------------------ END LOAD CONFIG FILE ------------------------------ #####
#### ------------------------ END LOAD CONFIG FILE ------------------------------ #####

debug = True

### UNOFFICIAL KEYS
app_key = "ha89swtfythbsip"
app_secret = "4iy0"


twitch = Twitch(app_key, app_secret)

#### This is what sets the API connection for everything, so this would be the actual "broadcaster/streamer using the plugin"
#broadcaster_username = "TheEsportCompany" ### This should taken from settings file from Plugin.
#### Broadcaster_id is created via config file and loaded into variable upon every plugin boot..


######################################################################################################
################################      My Twitch API MESS      ########################################
######################################################################################################

### The Docs  https://pytwitchapi.readthedocs.io/en/latest/modules/twitchAPI.oauth.html   
###           https://dev.twitch.tv/docs/api/reference#get-bits-leaderboard



def saveconfig(the_config):
    ### saving the main twitch API config stuff to json file...
    save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras')
    a_file = open(save_path +"\main_config.json", "w")
    text = json.dumps(the_config, sort_keys=False, indent=4)
    a_file.write(text)
    a_file.close()
    print('SAVED CONFIG: ', the_config)



##### WORKS, BUT SHOULD BE USING TRY AND EXCEPT KEYERR INSTEAD
def check_auth(current_token, a_refresh_token):
    check_token = validate_token(current_token)  ##using the current_token from config.txt
    message = check_token.get('message')
    expires_in = check_token.get('expires_in')
    #print(" CHECK TOKEN STUFF      ", check_token)
    #pprint(check_token)

    target_scope = [AuthScope.BITS_READ, AuthScope.WHISPERS_READ, AuthScope.CHANNEL_MANAGE_PREDICTIONS, AuthScope.CHANNEL_READ_POLLS, AuthScope.CHANNEL_MANAGE_POLLS, AuthScope.MODERATOR_MANAGE_AUTOMOD,
                AuthScope.CHANNEL_READ_PREDICTIONS, AuthScope.CHANNEL_MODERATE, AuthScope.MODERATION_READ, AuthScope.CHANNEL_MANAGE_REDEMPTIONS, AuthScope.CHANNEL_READ_REDEMPTIONS, AuthScope.CHANNEL_READ_SUBSCRIPTIONS]
    auth = UserAuthenticator(twitch, target_scope, force_verify=False)

    print('Token expires in: ', expires_in)
    if expires_in:
        if expires_in > 13700:
            pass
        if expires_in < 3600:  ## 1 Hour
            #twitch.refresh_used_token()
            print("Token less than 3600 seconds.. We are refreshing now just because")

    if not message:
        print("WE ARE AUTHORIZED")
        try:
            twitch.set_user_authentication(current_token, target_scope, a_refresh_token)
        except MissingScopeException as err:
            debug_log(f"[ERROR - check_auth] - {err}")
            print(err, " Should probably fix this...")  

    if message:
        ## 'message' existed, so appears we have an error.. re-auth now
        print("ERROR: ", message)
        print('MISSING TOKEN: ', check_token, "\nbroadcaster user: ", broadcaster_username)
  

        if message == "invalid access token":
            print("lets refresh ok")
            try:
                ## must use these together to properly refresh token.
                current_token, refresh_token=  refresh_access_token(a_refresh_token, app_key, app_secret )
                twitch.refresh_used_token()
                print("Tokens Refreshed\nNew Token: ", current_token)
                print("New Refresh Token: ", refresh_token)

                the_broadcaster_id = twitch.get_users(logins=[broadcaster_username])['data'][0]['id']

                ### Save Current + Refresh Token to a txt file 
                the_config = {
                        'Current Token': current_token,
                        'Refresh Token': refresh_token, 
                        'Broadcaster ID': the_broadcaster_id,
                        'Broadcaster Username': broadcaster_username
                        }
                print("")
                print('The NEW RE-AUTHd Tokens: ', the_config)
                print("")
                saveconfig(the_config)
            except TwitchAPIException as err:
                current_token, refresh_token = auth.authenticate()
                print("This is the error ", err)
                debug_log(f"[ERROR - check_auth] - {err}")
            except UnauthorizedException as err:
                current_token, refresh_token = auth.authenticate()
                print("Unauth Error, Twitch_API.py :", err )
                debug_log(f"[ERROR - check_auth] - {err}")
            except MissingScopeException as err:
                print("missing scopes stuff", err)
                debug_log(f"[ERROR - check_auth] - {err}")
    if message == "missing authorization token":
        try:
            #must be first time setup
            the_broadcaster_id = twitch.get_users(logins=[broadcaster_username])['data'][0]['id']
            auth = UserAuthenticator(twitch, target_scope, force_verify=False)

            # this will open your default browser and prompt you with the twitch verification website
            token, refresh_token = auth.authenticate()
            twitch.set_user_authentication(token, target_scope, refresh_token)

            the_config = {
            'Current Token': token,
            'Refresh Token': refresh_token, 
            'Broadcaster ID': the_broadcaster_id, 
            'Broadcaster Username': broadcaster_username
            }
            print("")
            print('The NEW RE-AUTHd Tokens: ', the_config)
            print("")
            saveconfig(the_config)
        except TwitchAPIException:
            print("maybe next time?")
            pass


check_auth(current_token, a_refresh_token)

def debug_log(fullerror):
    ts = time.time()
    st = datetime.fromtimestamp(ts).strftime('[%Y-%m-%d - %I:%M:%S]')
    ## if error style things, use this to save to log file
    save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras')
    a_file = open(save_path +"\debug_log.txt", "a")
    a_file.write(st+ " " +str(fullerror)+ "\n")
    a_file.close()




################# THINK WE CAN DELETE THIS? #####################

#### ------------ LOAD CONFIG FILE, CHECK IF TOKEN IS VALID ------------------ #####
####  try:
####      save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras')
####      a_file = open(save_path +"\main_config.json", "r")
####      the_config = json.load(a_file)
####      a_file.close()
####      current_token = the_config.get('Current Token')
####      a_refresh_token = the_config.get('Refresh Token')
####      the_broadcaster_id = the_config.get('Broadcaster ID')
####      broadcaster_username = the_config.get('Broadcaster Username')
####      #check_auth(current_token, a_refresh_token)
####  except (FileNotFoundError, IOError):
####      if debug:
####          fullerror = "Load Config Auth: "+ str(IOError)
####      debug_log(fullerror)
####      print("Wrong file or file path")
####  #### ------------ END LOAD CONFIG FILE ------------------ #####



###    the_broadcaster_id = twitch.get_users(logins=[broadcaster_username])['data'][0]['id']
###    
###    target_scope = [AuthScope.BITS_READ, AuthScope.WHISPERS_READ, AuthScope.CHANNEL_MANAGE_PREDICTIONS, AuthScope.CHANNEL_READ_POLLS, AuthScope.CHANNEL_MANAGE_POLLS, AuthScope.MODERATOR_MANAGE_AUTOMOD,
###                AuthScope.CHANNEL_READ_PREDICTIONS, AuthScope.CHANNEL_MODERATE, AuthScope.MODERATION_READ, AuthScope.CHANNEL_MANAGE_REDEMPTIONS, AuthScope.CHANNEL_READ_REDEMPTIONS]
###    auth = UserAuthenticator(twitch, target_scope, force_verify=False)
###    token, refresh_token = auth.authenticate()
###    
###    print("the current token", current_token)
###    print("refresh token", refresh_token)
###    ### Save Current + Refresh Token to a txt file 
###    the_config = {
###            'Current Token': current_token,
###            'Refresh Token': refresh_token, 
###            'Broadcaster ID': the_broadcaster_id
###            }
###    saveconfig(the_config)





######################     TWITCH API FUNCTIONS BELOW      ######################


def get_global_badges():
  ### Making the Save Path ###
  local_path = path.expandvars('%APPDATA%')
  sub_gifter_folder = r"\TouchPortal\plugins\TwitchExtras\images\badges\sub_gifter_badges\\"
  bits_badge_folder = r"\TouchPortal\plugins\TwitchExtras\images\badges\bit_badges\\"
  subscriber_save_path = local_path+ sub_gifter_folder
  bits_save_path = local_path +bits_badge_folder

  ## making the request
  r = requests.get("https://badges.twitch.tv/v1/badges/global/display?language=en")
  r = json.loads(r.text)

  ## Sorting Thru Dict for what we want/need
  for adict in (r['badge_sets']):
      if adict == "sub-gifter":
        inside_sub_gifter = (r['badge_sets'][adict]['versions'])

      if adict == "sub-gift-leader":
        inside_sub_gift_leader = (r['badge_sets'][adict]['versions'])

      if adict == "bits":
        inside_bits_default = (r['badge_sets'][adict]['versions'])

      if adict == "bits-leader":
        inside_bits_leader = (r['badge_sets'][adict]['versions'])


    ## saving each image to folder with biggest size
  for item in inside_sub_gifter:
    image_name = subscriber_save_path+item + "_sub_gifts" + ".png"
    imgURL = inside_sub_gifter[item]['image_url_4x']
    urllib.request.urlretrieve(imgURL, image_name)

    ## saving each image to folder with biggest size  - not using leader yet but its there...
  for item in inside_sub_gift_leader:
    image_name = subscriber_save_path+item + "_sub_gift_leader" + ".png"
    imgURL = inside_sub_gift_leader[item]['image_url_4x']
    urllib.request.urlretrieve(imgURL, image_name)


  for item in inside_bits_default:
    image_name = bits_save_path+item + "_bits" + ".png"
    imgURL = inside_bits_default[item]['image_url_4x']
    urllib.request.urlretrieve(imgURL, image_name)

  for item in inside_bits_leader:
    image_name = bits_save_path+item + "_bits_leader" + ".png"
    imgURL = inside_bits_leader[item]['image_url_4x']
    urllib.request.urlretrieve(imgURL, image_name)




### Loading and Saving Badges to TwitchExtras folder to utilize for 'calculate_points' 
def get_badges():
    import urllib.request
    local_path = path.expandvars('%APPDATA%')
    subscriber_folder = r"\TouchPortal\plugins\TwitchExtras\images\badges\subscriber_badges\\"
    bits_folder = r"\TouchPortal\plugins\TwitchExtras\images\badges\bit_badges\\"
    subscriber_save_path = local_path+ subscriber_folder
    bits_save_path = local_path+ bits_folder
    #save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras\images\badges\\')

    badges = twitch.get_chat_badges(broadcaster_id=the_broadcaster_id)

    #########################
    ### making sure we are saving the right data as the right badges...
    bits_badge_dict = {}
    subscriber_badge_dict= {}
    debug_log(badges)
    pprint(badges)
    for key in badges['data']:
        if key['set_id'] == "bits":
            print("here is the bits")
            bits_badge_dict = key['versions']
            print(key['set_id'])
            pprint(bits_badge_dict)

        if key['set_id'] == "subscriber":
            print("\n\n-------------------------")
            print("here is the subscriber")
            print(key['set_id'])
            subscriber_badge_dict = key['versions']
            pprint(subscriber_badge_dict)

    for item in subscriber_badge_dict:
        image_name = subscriber_save_path+item['id'] +".png"
        print(image_name)
        imgURL = item['image_url_4x']
        urllib.request.urlretrieve(imgURL, image_name)

    for item in bits_badge_dict:
        image_name = bits_save_path+item['id'] +".png"
        imgURL = item['image_url_4x']
        urllib.request.urlretrieve(imgURL, image_name)
    print("Subscriber Badges images saved to file")
    #triggering global badges download...
    get_global_badges()

#get_badges()


#### This is used for Level Card currently.. it triggers this.. and this saves the image to folder as needed.. if 403 error then it saves a default image instead
def get_profile_image(imgURL):
    #profile_image_save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras\images\\')
    
    local_path = path.expandvars('%APPDATA%')
    tp_path = r"\TouchPortal\plugins\TwitchExtras\images\\"
    profile_image_save_path = local_path+ tp_path
    image_name = profile_image_save_path+"level_card_profile_picture.png"
    #print(image_name)

    try:
        urllib.request.urlretrieve(imgURL, image_name)
        #print("badge images saved to file")
    except urllib.error.HTTPError as err:
       # from PIL import Image 
        print("[GET PROFILE IMAGE] - we are in error..")
        local_path = path.expandvars('%APPDATA%')
        tp_path = "\TouchPortal\plugins\TwitchExtras\images\\"
        full_path = local_path+ tp_path
        im1 = Image.open(f"{full_path}\default_profile_image.png") 
        im1 = im1.save(f"{full_path}\level_card_profile_picture.png")
        print("Use a default image here instead since we got an error..")
        print(err)


### this is currently holding gifted subs for other commands to utilize..
from plug_config import *
### this is just temp to reset the sub dict every time.. in future we will store this in file to save and reuse..
#  once we can update that data...
def get_gifters_fresh():
    full_config.Gift_Subs = {}
    get_gifters()

def get_gifters(cursor=False):
    #dictionary_tracker.get_gifters_loop_count = dictionary_tracker.get_gifters_loop_count + 1
    #print(f"[GET_GIFTERS LOOP COUNT] {dictionary_tracker.get_gifters_loop_count}")
    sub_dict = {}
    try:
        if not cursor:
            sub_dict = twitch.get_broadcaster_subscriptions(broadcaster_id=the_broadcaster_id, first=99)
        if cursor:
            sub_dict = twitch.get_broadcaster_subscriptions(broadcaster_id=the_broadcaster_id,after=cursor, first=99)
            if len(sub_dict['data']) >0:
                print("\n------------ NEXT PAGE -------------  ")
            else:
                print("\nEND OF GET SUBSCRIPTIONS")
            ### setting the gift_subs dict to empty.. so it doesnt keep adding to ?
    except TwitchAPIException as err:
        fullerror = f"[ERROR - get_gifters] -> {err} Are you an Affiliate or Partner? - subdict = {sub_dict}"
        debug_log(fullerror)
        
    if sub_dict:
        if len(sub_dict['data']) >0:
            next_page_cursor = sub_dict.get('pagination', {}).get('cursor', None)

            gifters_dict = full_config.Gift_Subs
            all_subscribers = full_config.all_subscribers

            sub_dict_data = sub_dict['data']
           # pprint(sub_dict_data)
            for adict in sub_dict_data:
               gifted = adict['is_gift']
               subscriber_name = adict['user_name']
               subscriber_id = adict['user_id']
               subscriber_tier = adict['tier']
               ### adding name to all subscribers
               all_subscribers[subscriber_name] = subscriber_tier[:1]

               if gifted:
                   gifter_name = adict['gifter_name']
                   gifter_id = adict['gifter_id']
                   gifted_tier = adict['tier'][:1]
                   person_gifted = adict['user_name']
                   #print(f"[GIFTED] {person_gifted} -> Tier {gifted_tier} gifted by {gifter_name} ")
                   if gifter_name in gifters_dict:
                       gifter_count = gifters_dict[gifter_name]
                       gifter_count = gifter_count + 1
                       gifters_dict[gifter_name] = gifter_count
                   elif not gifter_name in gifters_dict:
                       gifters_dict[gifter_name] = 1
                   print(f"[GIFTED] {person_gifted} -> Tier {gifted_tier} gifted by {gifter_name} with a total gifted count of {gifters_dict}")
               else:
                   subscriber = adict['user_name']
                   subscriber_id = adict['user_id']
                   sub_tier = adict['tier'][:1]
                   print(f"[SUB] - {subscriber} | Tier {sub_tier}")

            if next_page_cursor:
                ## only if theres soemthing in data..
                if len(sub_dict['data']) >0:
                    print("[THE GIFTERS + AMOUNT] - ", full_config.Gift_Subs)
                    print("[ALL SUBSCRIBERS + TIER] - ", full_config.all_subscribers)
                    get_gifters(next_page_cursor)

                


            #print("The Gifters:",gifters_dict)
            ### saving
           # print("saving Gifters Dict to Full_Config") 
            #full_config.Gift_Subs = gifters_dict


  # save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras\lists')
  # a_file = open(save_path +"\sub_gifters.txt", "w")
  # text = json.dumps(gifters_dict, sort_keys=False, indent=4)
  # a_file.write(text)
  # a_file.close()

#get_gifters()


def delete_users():
    print(twitch.block_user(target_user_id="436373430"))
    print("success?")

def check_clip_info():
    dict = twitch.get_clips(clip_id="ObedientElegantPepperStrawBeary-sYxFt2wpXywVTu_K")
    pprint (dict)
    
check_clip_info()

#### This is bringing back top 3 clips, not most recent...
def get_clips(username, amount):
    amount = int(amount)
    dict = twitch.get_users(logins=[username])['data'][0]
    user_id = dict['id']
    clips = twitch.get_clips(broadcaster_id=user_id, first=amount)

    pprint(clips)

    if amount >= 1:
        clip_0_url = (clips['data'][0]['url'])
        clip_0_title = (clips['data'][0]['title'])
        clip_0_duration = (clips['data'][0]['duration'])
        clip_0_views = (clips['data'][0]['view_count'])
        clip_0_creator_name = (clips['data'][0]['creator_name'])
        clip_0_thumbnailurl = (clips['data'][0]['thumbnail_url'])
        print(clip_0_creator_name, ": ", clip_0_url, "\n","Title: ", clip_0_title, ": ", clip_0_views, "total views")
        
        TPClient.stateUpdateMany([
        {
            "id": 'gitago.twitchextras.state.getuserclips.clip1.creatorname',
            "value": clip_0_creator_name
        },
        {
            "id": 'gitago.twitchextras.state.getuserclips.clip1.title',
            "value": str(clip_0_title)
        },
        {
            "id": 'gitago.twitchextras.state.getuserclips.clip1.url',
            "value": str(clip_0_url)
        },
        {
            "id": 'gitago.twitchextras.state.getuserclips.clip1.thumburl',
            "value": str(clip_0_thumbnailurl)
        },
        {
            "id": 'gitago.twitchextras.state.getuserclips.clip1.duration',
            "value": str(clip_0_duration)
        },
        {
            "id": 'gitago.twitchextras.state.getuserclips.clip1.views',
            "value": str(clip_0_views)
            },
            ])

    if amount >= 2:
        clip_1_url = (clips['data'][1]['url'])
        clip_1_title = (clips['data'][1]['title'])
        clip_1_duration = (clips['data'][1]['duration'])
        clip_1_views = (clips['data'][1]['view_count'])
        clip_1_creator_name = (clips['data'][1]['creator_name'])
        clip_1_thumbnailurl = (clips['data'][1]['thumbnail_url'])
        #print(clip_1_creator_name, ": ", clip_1_url, "\n","Title: ", clip_1_title, ": ", clip_1_views, "total views")
        TPClient.stateUpdateMany([
        {
            "id": 'gitago.twitchextras.state.getuserclips.clip2.creatorname',
            "value": clip_1_creator_name
        },
        {
            "id": 'gitago.twitchextras.state.getuserclips.clip2.title',
            "value": str(clip_1_title)
        },
        {
            "id": 'gitago.twitchextras.state.getuserclips.clip2.url',
            "value": str(clip_1_url)
        },
        {
            "id": 'gitago.twitchextras.state.getuserclips.clip2.thumburl',
            "value": str(clip_1_thumbnailurl)
        },
        {
            "id": 'gitago.twitchextras.state.getuserclips.clip2.duration',
            "value": str(clip_1_duration)
        },
        {
            "id": 'gitago.twitchextras.state.getuserclips.clip2.views',
            "value": str(clip_1_views)
            },
            ])
    
    if amount >= 3:
        print("yay 3")
        print(clips)
        clip_2_url = (clips['data'][2]['url'])
        clip_2_title = (clips['data'][2]['title'])
        clip_2_duration = (clips['data'][2]['duration'])
        clip_2_views = (clips['data'][2]['view_count'])
        clip_2_creator_name = (clips['data'][2]['creator_name'])
        clip_2_thumbnailurl = (clips['data'][2]['thumbnail_url'])
        #print(clip_2_creator_name, ": ", clip_2_url, "\n","Title: ", clip_2_title, ": ", clip_2_views, "total views")
        TPClient.stateUpdateMany([
        {
            "id": 'gitago.twitchextras.state.getuserclips.clip3.creatorname',
            "value": clip_2_creator_name
        },
        {
            "id": 'gitago.twitchextras.state.getuserclips.clip3.title',
            "value": str(clip_2_title)
        },
        {
            "id": 'gitago.twitchextras.state.getuserclips.clip3.url',
            "value": str(clip_2_url)
        },
        {
            "id": 'gitago.twitchextras.state.getuserclips.clip3.thumburl',
            "value": str(clip_2_thumbnailurl)
        },
        {
            "id": 'gitago.twitchextras.state.getuserclips.clip3.duration',
            "value": str(clip_2_duration)
        },
        {
            "id": 'gitago.twitchextras.state.getuserclips.clip3.views',
            "value": str(clip_2_views)
            },
            ])

    if amount >= 4:
        pass
        clip_3_url = (clips['data'][3]['url'])
        clip_3_title = (clips['data'][3]['title'])
        clip_3_duration = (clips['data'][3]['duration'])
        clip_3_views = (clips['data'][3]['view_count'])
        clip_3_creator_name = (clips['data'][3]['creator_name'])
        clip_3_thumbnailurl = (clips['data'][3]['thumbnail_url'])
        print(clip_3_creator_name, ": ", clip_3_url, "\n","Title: ", clip_3_title, ": ", clip_3_views, "total views")
    if amount >= 4:
        pass
        clip_4_url = (clips['data'][4]['url'])
        clip_4_title = (clips['data'][4]['title'])
        clip_4_duration = (clips['data'][4]['duration'])
        clip_4_views = (clips['data'][4]['view_count'])
        clip_4_creator_name = (clips['data'][4]['creator_name'])
        clip_4_thumbnailurl = (clips['data'][4]['thumbnail_url'])
        print(clip_4_creator_name, ": ", clip_4_url, "\n","Title: ", clip_4_title, ": ", clip_4_views, "total views")                    
#get_clips("GitagoGaming", 2)   #testing get_clips   



### take top 100 bits? and make a leaderboard csv or database? or just grab person by person as needed...
#amount = how many results, 1-100.. defaults to 10  - #period = day, week, month, year, all (is default)     
def bits_person(amount, a_user_id):
    try:
        bits_data = twitch.get_bits_leaderboard(count=amount, user_id=a_user_id)
        total_data = bits_data['total']
        if total_data > 0:
            bits_data = bits_data['data'][0]
            #this means it found 'someone'
            persons_bits = str(bits_data['score'])
            #print("Bits for ", username, ": ",persons_bits)
            print("[BITS PERSON] ", persons_bits)
            return persons_bits

        elif bits_data['total']== 0:
            person_bits = 0
            print("[BITS PERSON] No Bits Recorded")
    except UnauthorizedException as err:
        debug_log(f'[BITS-PERSON ERROR] - {err}')
        try:
            check_auth()
            bits_person()
        except:
            pass

#bits_leaderboard(1)


def get_cheer_motes():
    print(twitch.get_cheermotes(the_broadcaster_id))



def get_followers(username):
    a_user_id = twitch.get_users(logins=[username])['data'][0]['id']
    dict = twitch.get_users_follows(to_id=a_user_id, first=5)
    Total_Followers = dict['total']
    print("Total Followers: ", Total_Followers)
    pprint(dict)

#get_followers("theesportcompany")


#### followage_months i think is useless... but keeping for now
def followage_months(user_id):
    my_date = datetime.utcnow()   #using UTC time to match twitch ?  Apparently Z on end of it means
    current_stamp = (my_date.strftime('%Y-%m-%d %H:%M:%S'))  # sets same time stamp format as Twitch.
    follow_info = twitch.get_users_follows(from_id=user_id, to_id=the_broadcaster_id)  ## FROM ID = WHO WAS BEING FOLLOWED, TO_ID = WHO DID THE FOLLOWING, AND WHEN
    #print(follow_info)
    ### Checking if follow data is even valid.
    checkit = (follow_info.get('data')) 
    if not checkit:
        print(f"\nThis user is not following {broadcaster_username}\n") 
        months_dict = {}
        return months_dict

    #### ALL THIS IS CHECKING FOLLOWED AT TIME AND THEN FORMATTING  ####
    elif checkit:
        followed_at = (follow_info['data'][0]['followed_at']) #shows the follow timestamp for that follower
        followed_date = (followed_at.split('T')[0])   # this is splitting from T and returning the Date
        match = re.search('T(.*)Z',followed_at) # this is searching for whats between between T and Z 
        followed_time = (match.group(1)) # This is displaying the match found between T and Z
        followed_at_formatted = followed_date + " " +followed_time  ## this is the formatted time needed to make the following command work.
        
        ##### Finding The Difference Between the Two Dates #################
        start = datetime.strptime(current_stamp, '%Y-%m-%d %H:%M:%S')
        ends = datetime.strptime(followed_at_formatted, '%Y-%m-%d %H:%M:%S')
        diff = relativedelta(start, ends)
        years_to_months = 12*int(diff.years)
        #print("years t omonths", years_to_months)
        totalmonths = years_to_months + diff.months
        #print("Total Months", totalmonths)
        
        ### around line 220 on user_database.py can "maybe" pull those lines here to make this command send full dict pre formatted.  
        months_dict = {
        "Total Months": totalmonths,
        "diff_year": diff.years,
        "diff_month": diff.months,
        "diff_day": diff.days,
        "diff_hour": diff.hours,
        "diff_min": diff.minutes
        }
        return months_dict



def followage(username, choice):
    my_date = datetime.utcnow()   #using UTC time to match twitch ?  Apparently Z on end of it means
    print(my_date)
    current_stamp = (my_date.strftime('%Y-%m-%d %H:%M:%S'))  # sets same time stamp format as Twitch.
    a_user_id = twitch.get_users(logins=[username])['data'][0]['id']   # sets user ID
    follow_info = twitch.get_users_follows(from_id=a_user_id, to_id=the_broadcaster_id)  ## FROM ID = WHO WAS BEING FOLLOWED, TO_ID = WHO DID THE FOLLOWING, AND WHEN
    checkit = (follow_info.get('data'))  ### Checking if follow data is even valid.
    if not checkit:
        print("not following, or broken stuff")

    elif checkit:
        #### ALL THIS IS CHECKING FOLLOWED AT TIME AND THEN FORMATTING  ####
        followed_at = (follow_info['data'][0]['followed_at']) #shows the follow timestamp for that follower
        followed_date = (followed_at.split('T')[0])   # this is splitting from T and returning the Date
        match = re.search('T(.*)Z',followed_at) # this is searching for whats between between T and Z 
        followed_time = (match.group(1)) # This is displaying the match found between T and Z
        followed_at_formatted = followed_date + " " +followed_time  ## this is the formatted time needed to make the following command work.
        
        ##### Finding The Difference Between the Two Dates #################
        start = datetime.strptime(current_stamp, '%Y-%m-%d %H:%M:%S')
        ends = datetime.strptime(followed_at_formatted, '%Y-%m-%d %H:%M:%S')
        diff = relativedelta(start, ends)
        calculated_followage = ("%s has been following for %d year %d month %d days %d hours %d minutes" % (username, diff.years, diff.months, diff.days, diff.hours, diff.minutes))
        years_to_months = 12*int(diff.years)
        totalmonths = years_to_months + diff.months

        if choice == "months":
            print('total months', totalmonths)
            TPClient.stateUpdate("gitago.twitchextras.state.user.followagemonths",  totalmonths)
            return totalmonths
            pass

        if choice == "full":
            fullist = [diff.years, diff.months, diff.days]
            print(fullist)
                
            if diff.years == 0:
                calculated_followage = ("%s has been following for %d month %d days %d hours %d minutes" % (username, diff.months, diff.days, diff.hours, diff.minutes))
                ## if 0 years, then lets not bother showing
                if diff.months == 0:
                    calculated_followage = ("%s has been following for %d days %d hours %d minutes" % (username, diff.days, diff.hours, diff.minutes))
                    if diff.days == 0:
                        calculated_followage = ("%s has been following for %d hours %d minutes" % (username, diff.hours, diff.minutes))
                        return calculated_followage
        
            print (calculated_followage)
            TPClient.stateUpdate("gitago.twitchextras.state.user.followage",  calculated_followage)
            TPClient.stateUpdate("gitago.twitchextras.state.user.followagemonths",  str(totalmonths))

            #return calculated_followage

#followage("GitagoGaming", "full")



def get_user_info(username, choice):
    if choice == "username":
        ### EVERY TIME USER_INFO called it does API call.. This could be 6 api calls for a single person.. 
        ### Instead lets put full user info into CSV/DB and then check that.. if NOT in list, then do an api call.. if in list then use that info
        
        dict = twitch.get_users(logins=[username])['data'][0]
        
        ##how to turn this image url into an actual 256 image in TP folder...
        profile_image_url = dict['profile_image_url']
        view_count = dict['view_count']
        user_id = dict['id']
        broadcaster_type = dict['broadcaster_type']


        #### Adding in DICT2 here then 'updating' with some base info so it doesnt enter in NULL for these items.
         ### Total Months Subscribed will come every time on each chat message and be updated inside of Chatbot.py
        dict2 = {
        'level': 1,
        'total_messages': 1,
        'total_bits': 0,
        'months_subscribed': 0,
        'follow_months': 0,
        #'gifted_subs': 0,
        'badges': "{}"
        }

        for item in dict:
            dict[item] = dict[item]
        dict2.update(dict)
        enter_user_dict(dict2)
        print("user was not in database, so we are getting their info")
        return dict2

    if choice == "user-id":
        dict = twitch.get_users(user_ids=[username])['data'][0]

        #pprint(dict, sort_dicts=False)
        #### Adding in DICT2 here then 'updating' with some base info so it doesnt enter in NULL for these items.
        ### Total Months Subscribed will come every time on each chat message and be updated inside of Chatbot.py
        dict2 = {
        'level': 1,
        'total_messages': 1,
        'total_bits': 0,
        'months_subscribed': 0,
        'follow_months': 0,
        'badges': "{}"
        }

        for item in dict:
            #print("Key", item, "Value", dict[item])
            dict[item] = dict[item]
        ##Updating dict
        dict2.update(dict)

        enter_user_dict(dict2)  ## this was 'dict' but now we update with dict data
        return dict2


    if choice == "request":
        dict = twitch.get_users(logins=[username])['data'][0]
        user_id = dict['id']
        #pprint (dict)  
        followage_dict = followage_months(user_id)
        #pprint(followage_dict)
    
        ##how to turn this image url into an actual 256px image in TP folder...
        display_name = dict['display_name']
        profile_image_url = dict['profile_image_url']
        total_view_count = dict['view_count']
        user_id = dict['id']
        broadcaster_type = dict['broadcaster_type']
        created_at = dict['created_at']

        
        r = requests.get(f"https://decapi.me/twitch/followcount/{username}")
        INT_Total_Followers = int(r.text)
        Total_Followers = "{:,}".format(INT_Total_Followers)     ### Adding Commas to View Count and Followers
        total_view_count = "{:,}".format(total_view_count)

        ### didnt do commas for viewer count yet since if no viewers it comes back as 'offline' which causes error.. 
        ## Easy fix..
        viewercount = requests.get(f'https://decapi.me/twitch/viewercount/{username}')

        game_category = requests.get(f'https://decapi.me/twitch/game/{username}')

        stream_title = requests.get(f'https://decapi.me/twitch/status/{username}')

        uptime =  requests.get(f'https://decapi.me/twitch/uptime/{username}')

        #followage = requests.get(f'https://decapi.me/twitch/followage/{the_broadcaster_id}/{username}?precision=2')


        TPClient.stateUpdateMany([
        {
            "id": 'gitago.twitchextras.state.user.displayname',
            "value": str(display_name)
        },
        {
            "id": 'gitago.twitchextras.state.user.imageurl',
            "value": str(profile_image_url)
        },
        {
            "id": 'gitago.twitchextras.state.user.viewcount',
            "value": str(total_view_count)
        },
        {
            "id": 'gitago.twitchextras.state.user.currentviewcount',
            "value": str(viewercount)
        },
        {
            "id": 'gitago.twitchextras.state.user.gamecategory',
            "value": str(game_category)
        },
        {
            "id": 'gitago.twitchextras.state.user.streamtitle',
            "value": str(stream_title)
        },
        {
            "id": 'gitago.twitchextras.state.user.uptime',
            "value": str(uptime)
        },
        {
            "id": 'gitago.twitchextras.state.user.broadcastertype',
            "value": str(broadcaster_type)
        },
        {
            "id": 'gitago.twitchextras.state.user.followcount',
            "value": str(Total_Followers)
        },
        {
            "id": 'gitago.twitchextras.state.user.createdat',
            "value": str(created_at)
        },
        {
            "id": 'gitago.twitchextras.state.user.userid',
            "value": str(user_id)
        },
        {
            "id": 'gitago.twitchextras.state.user.follow_age',
            "value": str(followage)
        }
        ])



### WE DO NOT CREATE STATES HERE, JUST GHOST UPDATE THEM FOR PEOPLE WHO WANT TO USE
### Get Mods, and VIPS
def get_moderators():
    dictionary_tracker.mod_loop_count = dictionary_tracker.mod_loop_count + 1
    #print(f"[GET_MODERATORS LOOP COUNT] {dictionary_tracker.mod_loop_count}")
    link = f"http://tmi.twitch.tv/group/user/{the_broadcaster_id}/chatters"
    ugh = requests.get(link).json()
    x = 0
    ## we should count the amount of moderators in chat, and then loop over that instead
    
    #print(ugh)
    for thing in range(15):
        x = x +1
        try:
            TPClient.stateUpdate("gitago.twitchextras.state.active_mods.name" +str(x), "")
            TPClient.stateUpdate("gitago.twitchextras.state.active_vips.name" +str(x), "")
        except Exception as err:
            debug_log(f"[ERROR - get_moderators/vips] -> {err}")

    x=0
    for item in ugh:
        if item =="chatters":
            the_mods = ugh['chatters']['moderators']
            the_vips = ugh['chatters']['vips']
            chatter_count = (ugh['chatter_count'])

            if the_mods:
                print(the_mods)
                for person in the_mods:
                    x = x +1
                    TPClient.stateUpdate("gitago.twitchextras.state.active_mods.name" +str(x), str(person))

            if the_vips:
                for person in the_vips:
                    TPClient.stateUpdate("gitago.twitchextras.state.active_vips.name" +str(x), str(person))
                   # print(f"[ACTIVE VIP] {person}")

#get_moderators()




global reward_dict_list
reward_dict_list = []
def get_rewards():
    try:
        global reward_dict_list
        reward_dict = twitch.get_custom_reward(broadcaster_id=the_broadcaster_id)

        reward_dict = reward_dict.get('data')
        if reward_dict == None:
            fullerror ="[ERROR - get_rewards] -> Rewards are EMPTY, Are you an Affiliate/Partner?" 
            debug_log(fullerror)

        if reward_dict:

              #### CLEAR ALL STATES BEFORE UPDATING...
              # 
          TPClient.createStateMany([
          {
              "id": 'gitago.twitchextras.state.twitchreward1.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward1.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward1.cost',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward2.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward2.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward2.cost',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward3.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward3.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward3.cost',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward4.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward4.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward4.cost',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward5.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward5.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward5.cost',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward6.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward6.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward6.cost',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward7.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward7.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward7.cost',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward8.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward8.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward8.cost',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward9.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward9.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward9.cost',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward10.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward10.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward10.cost',
              "value": ""
          },

          ]) 


          TPClient.stateUpdateMany([
          {
              "id": 'gitago.twitchextras.state.twitchreward1.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward1.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward1.cost',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward2.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward2.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward2.cost',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward3.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward3.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward3.cost',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward4.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward4.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward4.cost',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward5.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward5.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward5.cost',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward6.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward6.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward6.cost',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward7.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward7.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward7.cost',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward8.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward8.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward8.cost',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward9.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward9.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward9.cost',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward10.name',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward10.id',
              "value": ""
          },
          {
              "id": 'gitago.twitchextras.state.twitchreward10.cost',
              "value": ""
          },

          ])


          x = 0
          for key in reward_dict:
              print("reward states should be created...")
              x = x +1
              reward_cost = (key['cost'])
              reward_id = (key['id'])
              reward_title = (key['title'])
              print("Title: ", reward_title, " Cost: ", reward_cost, "ID: ", reward_id, " ", x)

              TPClient.createState("gitago.twitchextras.state.twitchreward" +str(x) +".name", "TE | Channel Reward " +str(x) + " Title  ||  " + str(key['title']), "")    
              TPClient.stateUpdate("gitago.twitchextras.state.twitchreward" +str(x) +".name", (key['title']))

              TPClient.createState("gitago.twitchextras.state.twitchreward" +str(x) +".cost", "TE | Channel Reward " +str(x) +": Cost", "")    
              TPClient.stateUpdate("gitago.twitchextras.state.twitchreward" +str(x) +".cost", str((key['cost'])))

              TPClient.createState("gitago.twitchextras.state.twitchreward" +str(x) +".id", "TE | Channel Reward "  +str(x) +": ID", "")    
              TPClient.stateUpdate("gitago.twitchextras.state.twitchreward" +str(x) +".id", str((key['id'])))
              insert_dict = {
              'Reward Title': reward_title,
              'Reward ID': reward_id,
              'Reward Cost': reward_cost,
              'State': "gitago.twitchextras.state.twitchreward" +str(x)
              }
              reward_dict_list.append(insert_dict)
    except UnauthorizedException as err:
        fullerror ="ERROR, MUST BE TWITCH AFFILIATE TO USE THIS - Check you are using the correct account" 
        debug_log(fullerror)
        TPClient.createState("gitago.twitchextras.state.twitchreward1.name", "TE | Channel Reward ERROR", "Must Be Twitch Affiliate." )

    #pprint(reward_dict_list)

#get_rewards()






def create_rewards(r_title, r_cost, r_color, r_maxperstream, r_maxperuser, r_globalcd, skip_queue, user_input_req):
    r_color = r_color[0:7]

    if int(r_maxperuser) > 0:
        maxperuser_enabled = True        
    elif int(r_maxperuser) == 0:
        maxperuser_enabled = False


    if int(r_maxperstream) > 0:
        maxperstream_enabled = True        
    elif int(r_maxperstream) == 0:
        maxperstream_enabled = False

    if user_input_req == "False":
        user_input_req = False
    elif user_input_req == "True":
        user_input_req = True

    try:
        reward_dict = twitch.create_custom_reward(broadcaster_id=str(the_broadcaster_id), title=str(r_title), cost=int(r_cost), is_user_input_required=user_input_req,
                                max_per_stream=int(r_maxperstream), is_max_per_stream_enabled=maxperstream_enabled, max_per_user_per_stream=int(r_maxperuser), is_max_per_user_per_stream_enabled=maxperuser_enabled,
                                global_cooldown_seconds=int(r_globalcd), should_redemptions_skip_request_queue=skip_queue, background_color=r_color   )

        reward_id = reward_dict['data'][0]['id']
        reward_title = reward_dict['data'][0]['title']
    except TwitchAPIException as err:
        fullerror =f"[ERROR - Create Rewards] -> {err}" 
        debug_log(fullerror)
    pass




def delete_reward(r_id):
    print(" we here")
    ### Lets check for reward in reward list dict we created when getting rewards.. 
    for dict in reward_dict_list:
        dicts_id = (dict['Reward ID'])
        dicts_state_id = (dict['State'])
        if r_id == dicts_id:
            print("This is a match", r_id)
            ## we the ID matches, set all the states for this particular ID to EMPTY
            TPClient.stateUpdate(dicts_state_id + ".name", "")
            TPClient.stateUpdate(dicts_state_id + ".cost", "")
            TPClient.stateUpdate(dicts_state_id + ".id", "")
            print(the_broadcaster_id)
            twitch.delete_custom_reward(broadcaster_id=the_broadcaster_id, reward_id=str(r_id))

    #get_rewards()  
    





######################## AUTOMOD FUNCTIONS ##################
######################## AUTOMOD FUNCTIONS ##################

global automod_case_list
approved_denied_cases = {"Approved Cases":0, "Denied Cases": 0, "Total Cases":0}
automod_case_list = []
current_case_num = 0
def get_new_case(automod_case_list):
    automod_query_length = len(automod_case_list)
    global approved_denied_cases
    approved_denied_cases['Total Cases'] = automod_query_length
    print(approved_denied_cases)
    TPClient.stateUpdate("gitago.twitchextras.state.automod.case_count", str(automod_query_length))
    countbad = 0
    countgood = 0
    pprint(automod_case_list)

    ### setting everything up from the dict
    global current_case_id
    current_case_id = (automod_case_list[current_case_num]['message']['id'])
    case_level = (automod_case_list[current_case_num]['content_classification']['level'])
    case_category = (automod_case_list[current_case_num]['content_classification']['category'])
    current_case_offender =(automod_case_list[current_case_num]['message']['sender']['display_name'])
    
    current_case_words = (automod_case_list[current_case_num]['message']['content']['fragments'])
    current_case_full_message = (automod_case_list[current_case_num]['message']['content']['text'])

    if len(automod_case_list) > 0:
        for word in current_case_words:
            #print(word)
            if "automod" in word:
                #countbad = countbad + 1
                #print(f"AUTOMOD WORD: {word['text']}")
                automod_word = word['text']
            else:
                #countgood = countgood + 1
                good_words = (f"Word #{countgood}, {word['text']}")
                #print(good_words)
                pass
    print(f"Case ID: {current_case_id} \nOffender: {current_case_offender}\nOffending Word/Words: {automod_word}")

    TPClient.stateUpdateMany([
    {
        "id": 'gitago.twitchextras.state.automod.case_offender',
        "value": str(current_case_offender)
    },
    {
        "id": 'gitago.twitchextras.state.automod.case_id',
        "value": str(current_case_id)
    },
    {
        "id": 'gitago.twitchextras.state.automod.case_word',
        "value": str(automod_word)
    },
    {
        "id": 'gitago.twitchextras.state.automod.case_fullmessage',
        "value": str(current_case_full_message)
    },
    {
        "id": 'gitago.twitchextras.state.automod.case_count',
        "value": str(len(automod_case_list))
    },
    ])



#### got to count total cases + total approved/denied...

def confirm_case(decision):
    global approved_denied_cases
    if len(automod_case_list) >0:
        try:
            if decision == "Approve":
                print(twitch.manage_held_automod_message(the_broadcaster_id, current_case_id, action=AutoModAction.ALLOW))
                approved_denied_cases['Approved Cases'] = approved_denied_cases['Approved Cases'] +1 
                print(approved_denied_cases)
            elif decision == "Deny":
                print(twitch.manage_held_automod_message(the_broadcaster_id, current_case_id, action=AutoModAction.DENY))
                approved_denied_cases['Denied Cases'] = approved_denied_cases['Denied Cases'] +1 
                print(approved_denied_cases)

            total_approved_denied = approved_denied_cases['Denied Cases'] + approved_denied_cases['Approved Cases']
            total_cases_left = len(automod_case_list) - total_approved_denied
        
            for i in range(len(automod_case_list)):
             # if total_approved_denied == approved_denied_cases['Total Cases']:
             #     TPClient.stateUpdateMany([
             # {
             #     "id": 'gitago.twitchextras.state.automod.case_offender',
             #     "value": "No Active Cases"
             # },
             # {
             #     "id": 'gitago.twitchextras.state.automod.case_id',
             #     "value": ""
             # },
             # {
             #     "id": 'gitago.twitchextras.state.automod.case_word',
             #     "value": ""
             # },
             # {
             #     "id": 'gitago.twitchextras.state.automod.case_fullmessage',
             #     "value": ""
             # },
             # {
             #     "id": 'gitago.twitchextras.state.automod.case_count',
             #     "value": "0"
             # },
             # ])
             #     break
                if automod_case_list[i]['message']['id'] == current_case_id:
                    print("This is i   ", automod_case_list[i])
                    del automod_case_list[i]
                    print("Removed Case from List")
                    break
            ## lets get a new case
            if total_cases_left > 0:
                get_new_case(automod_case_list)
            elif total_cases_left == 0:
                print("------------queue is empty-------------------")
            # TPClient.stateUpdateMany([
            # {
            #     "id": 'gitago.twitchextras.state.automod.case_offender',
            #     "value": "No Active Cases"
            # },
            # {
            #     "id": 'gitago.twitchextras.state.automod.case_id',
            #     "value": ""
            # },
            # {
            #     "id": 'gitago.twitchextras.state.automod.case_word',
            #     "value": ""
            # },
            # {
            #     "id": 'gitago.twitchextras.state.automod.case_fullmessage',
            #     "value": ""
            # },
            # {
            #     "id": 'gitago.twitchextras.state.automod.case_count',
            #     "value": "0"
            # },
            # ])
        except TwitchAPIException as err:
            debug_log(f"[ERROR - Confirm AutoMod Case] -> {err} - Queue Empty ?  - {approved_denied_cases}")

import threading
import schedule

def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


schedule.every(1).minutes.do(get_moderators)
### for now running get_gifters every 15 minutes as it can sometimes return a very large dictionary..
### when it runs, it stores gifter data in py file for use in calculating points etc..
#schedule.every(15).seconds.do(get_gifters)


# Start the background thread
stop_run_continuously = run_continuously()

# Do some other things...
#time.sleep(1)

# Stop the background thread
#stop_run_continuously.set()








### Whispers works on same account as broadcaster_id/username in config file
#############################################################################################
pubsub = PubSub(twitch)  # PUB SUB BELOW  ###################################################
#############################################################################################

#### Whispers are working
def callback_whisper(uuid: UUID, data: dict) -> None:
    print('got callback for UUID ' + str(uuid))
    check = data.get('data')
    ### we do if last_read not in, so it doesnt bother us with the extra callback, which we can worry about later which is some sort of spam filtr thing
    
    if "last_read" not in check:
        #pprint(data)

        data = data.get("data_object")
        message_id = data.get("id")
        from_id = data.get('from_id')
        message_body = data.get('body')

        from_username = data.get('tags')
        from_username = from_username['display_name']

        sent_time_unix = data.get('sent_ts')

        if sent_time_unix:
            timestamp = time.strftime("%D %#I:%M %p", time.localtime(int(sent_time_unix)))
            #print(timestamp)

        TPClient.stateUpdateMany([
        {
            "id": 'gitago.twitchextras.state.whisper1.timestamp',
            "value": str(timestamp)
        },
        {
            "id": 'gitago.twitchextras.state.whisper1.usernam',
            "value": str(from_username)
        },
        {
            "id": 'gitago.twitchextras.state.whisper1.message',
            "value": str(message_body)
        },
        ])

        print(timestamp, "  ", from_username, ": ", message_body)       
    elif "last_read" in check:
        #print(data['data_object'])
        #print(data)
        data = data.get("data_object")

        last_read = data['last_read']
        archived = data['archived']  #should return true or false.
        spam_info = data['spam_info']['likelihood']
        #print(spam_info)
        print("Archived: ", archived, " | ", "\nSpam Likelihood: ", spam_info, "\nTotal Whispers from person ",  last_read)




def callback_listen_channel_subcriptions(uuid: UUID, data: dict) -> None:
    print('Channel Subs - got callback for UUID ' + str(uuid))
    adict = data.get('data')
    debug_log("----------CHANNEL SUB HAPPENED----------")
    debug_log(adict)
    debug_log("----------DATA BACKUP---------")
    debug_log(data)
    pprint(adict)


###########################   Start CALLBACK Listen Chat Moderator    ################################# 
###########################   Start CALLBACK Listen Chat Moderator    ################################# 

def callback_listen_chat_moderator_actions(uuid: UUID, data: dict) -> None:
    print('chat mod actions listen - got callback for UUID ' + str(uuid))
    adict = data.get('data')
    pprint(adict) 
    
    ### listens for bans, unbans, timeouts, deleting messages, changing caht modes, adding moderators..
    mod_type = (adict['type'])

    if mod_type == "chat_channel_moderation":
        mod_action = (adict['moderation_action'])
        mod_username = (adict['created_by'])
        target_user = (adict['target_user_id'])
        auto_mod = (adict['from_automod'])  #returns True or Fasle
        print(mod_username, ": ",mod_action, "targeted user:", target_user, "Automod: ", auto_mod )


################## Followers Only
        if mod_action =="followers":
            print("followers mode only event to TP")
            follower_time_length = adict['args'][0]
            TPClient.stateUpdate(stateId="gitago.twitchextras.state.followers_only", stateValue="On")
            TPClient.stateUpdate(stateId="gitago.twitchextras.state.followers_only_length", stateValue=str(follower_time_length + " minutes"))
        elif mod_action == "followersoff":
            print("followers mode off event ")
            TPClient.stateUpdate(stateId="gitago.twitchextras.state.followers_only", stateValue="Off")
            TPClient.stateUpdate(stateId="gitago.twitchextras.state.followers_only_length", stateValue="0")


################## Emotes Only
        if mod_action == "emoteonly":
            print("emotes only event trigger")
            TPClient.stateUpdate(stateId="gitago.twitchextras.state.emotes_only", stateValue="On")
        elif mod_action == "emoteonlyoff":
            TPClient.stateUpdate(stateId="gitago.twitchextras.state.emotes_only", stateValue="Off")
            print("emotes only is off")


############## Subscribers Only
        if mod_action == "subscribers":
            print("Subscribers onlys only event trigger")
            TPClient.stateUpdate(stateId="gitago.twitchextras.state.subscribers_only", stateValue="On")
        elif mod_action == "subscribersoff":
            print("Subscribers only is off")
            TPClient.stateUpdate(stateId="gitago.twitchextras.state.subscribers_only", stateValue="Off")


##############  Slow Mode
        if mod_action == "slow":
            TPClient.stateUpdate(stateId="gitago.twitchextras.state.slow_mode", stateValue="On")
            print("Slow mode ON event")
            slow_time = (adict['args'][0])
            print(slow_time)
        elif mod_action == "slowoff":
            TPClient.stateUpdate(stateId="gitago.twitchextras.state.slow_mode", stateValue="Off")
            print("Slow Mode is off")


############## Chat Moderation
    if mod_type == "chat_login_moderation":
        mod_action = (adict['moderation_action'])
        if mod_action =="timeout":
            ### Make a WHEN USER TIMEDOUT Event...
            user_timedout= (adict['args'][0])
            user_timeount_int= (adict['args'][1])
            print(user_timedout, " was timedout for ", user_timeount_int)



#############  Deleted Blocked Terms
    if mod_type == "deleted_blocked_term":
        deleted_term = (adict['text'])
        requester = (adict['requester_login'])
        print(requester, " removed ", deleted_term, " from the blocked terms list")


#################   END CALLBACK LISTEN CHAT MODERATOR ACTIONS  ########################    
#################   END CALLBACK LISTEN CHAT MODERATOR ACTIONS  ########################





##### "Undocumented Topic" On Follow

def callback_listen_undocumented_topic_following(uuid: UUID, data: dict) -> None:
    adict = data.get('data')
    print('undocumented - got callback for UUID ' + str(uuid))
    print(adict)
    follow_name = (data['display_name'])
    follow_id = (data['user_id'])
    ## have this check database to see if person is already in there, if so then dont trigger a state update??  this would stop follow/refollows...
    TPClient.stateUpdate(stateId="gitago.twitchextras.state.on_follow", stateValue="True")
    TPClient.stateUpdate(stateId="gitago.twitchextras.state.on_follow", stateValue=follow_name)
    #print(f'{follow_name} has started following you!')



def callback_listen_undocumented_topic_polls(uuid: UUID, data: dict) -> None:
    adict = data.get('data')
    #print('undocumented - got callback for UUID ' + str(uuid))
    #pprint(adict)
    ### percentage dict is going to be used to deliver values to TP to show the percentage relationship of one to the other for visuals inside of OBS.

    poll_status = adict['poll']['status']
    poll_title = adict['poll']['title']
    poll_id = adict['poll']['poll_id']
    poll_created_by = adict['poll']['created_by']
    poll_ended_by = adict['poll']['ended_by']
    remaining_duration_milliseconds = adict['poll']['remaining_duration_milliseconds']

    TPClient.stateUpdateMany([
    {
        "id": 'gitago.twitchextras.state.poll.id',
        "value": str(poll_id)
    },
    {
        "id": 'gitago.twitchextras.state.poll.createdby',
        "value": str(poll_created_by)
    },
    {
        "id": 'gitago.twitchextras.state.poll.remaining_ms',
        "value": str(remaining_duration_milliseconds)
    },
    {
        "id": 'gitago.twitchextras.state.poll.title',
        "value": str(poll_title)
    },
    {
        "id": 'gitago.twitchextras.state.poll.status',
        "value": str(poll_status)
    },
    ])

    percentage_dict = {}
     ### loops thru choices dict and makes variables and updates states...
    choices_dict = adict['poll']['choices']
    ## use X in the variable name when sending to TP states, just like done previously with 'get_poll'
    x = 0
    for item in choices_dict:
        x = x + 1
        print(f"-- Choice {x} --")
        choice_id = (item['choice_id'])
        choice_title = (item['title'])
        bit_votes = (item['tokens']['bits'])
        channel_point_votes = (item['tokens']['channel_points'])
        total_people_voting = (item['total_voters'])
        combined_votes = (item['votes'])

        ##adding each choice to a new dict for us to calculate percentages.
        percentage_dict[f"Choice {x}"] = combined_votes['total']
        ### then later we will loop thru it and calculate and 'fix' it..   line 1361

        print(f"Title:{choice_title} - Bits Voted:{bit_votes} - Channel Points Voted: {channel_point_votes} - Total Voters: {total_people_voting}")
        print("")
       
        TPClient.stateUpdateMany([
        {
            "id": 'gitago.twitchextras.state.poll.choice_id_' +str(x),
            "value": choice_id
        },
        {
            "id": 'gitago.twitchextras.state.poll.title_' +str(x),
            "value": str(choice_title)
        },
        {
            "id": 'gitago.twitchextras.state.poll.bitvotes_' +str(x),
            "value": str(bit_votes)
        },
        {
            "id": 'gitago.twitchextras.state.poll.cpvotes_' +str(x),
            "value": str(channel_point_votes)
        },
        {
            "id": 'gitago.twitchextras.state.poll.totalvoters_' +str(x),
            "value": str(total_people_voting)
        },
        {
            "id": 'gitago.twitchextras.state.poll.votes_' +str(x),
            "value": str(combined_votes['total'])
        },
        ])

    ### CALCULATE PERCENTAGES BASED ON DICT     
    ### now lets loop thru the percentage dict and create actual percentages for visuals...
    #max_val = max(percentage_dict.values())
    total_val = sum(percentage_dict.values())
    if total_val:
        new = {k: v * 100 / total_val for k,v in percentage_dict.items()}
        for item in new.items():
            ## rebuilding  a new dict, but technically we dont need to do that. jsut updating TP values instead...
            #percentage_dict[item[0]] = int(item[1])  
            choice_loop = item[0].replace(" ", "")

            ### this is removing any decimals below - could convert to string instead and limit to 4 characters so it shows 27.1 for example  but then movement stuff would not work
            votes_loop = int(item[1])
            TPClient.stateUpdate('gitago.twitchextras.state.poll.percent_'+str(choice_loop), str(votes_loop))
        print("The Percentage Dict", percentage_dict)


############################
    #### basic data is being sent to states..
    ## data below is all TOTALS combined for each detail..
    top_bits_contrib = adict['poll']['top_bits_contributor']
    top_cp_contrib = adict['poll']['top_channel_points_contributor']
    top_contrib = adict['poll']['top_contributor']
    ## ALL THE VOTES FOR EVERY CHOICE
    total_base_votes = (combined_votes['base'])
    total_cp_votes = (combined_votes['channel_points'])
    total_bits_votes = (combined_votes['bits'])
    total_votes_all = adict['poll']['total_voters']
    total_bits_spent = adict['poll']['tokens']['bits']
    total_cp_spent = adict['poll']['tokens']['channel_points']

    ## the Poll settings, channel point cost, multi choice, subscriber multi, subscriber only, etc..
    poll_settings = adict['poll']['settings']

    TPClient.stateUpdateMany([
    {
        "id": 'gitago.twitchextras.state.poll.total_voters_all',
        "value": str(total_base_votes)
    },
    {
        "id": 'gitago.twitchextras.state.poll.total_cp_votes',
        "value": str(total_cp_votes)
    },
    {
        "id": 'gitago.twitchextras.state.poll.total_bit_votes',
        "value": str(total_bits_votes)
    },
    {
        "id": 'gitago.twitchextras.state.poll.total_voters_all',
        "value": str(total_votes_all)
    },
    {
        "id": 'gitago.twitchextras.state.poll.total_bit_spent',
        "value": str(total_bits_spent)
    },
    {
        "id": 'gitago.twitchextras.state.poll.total_cp_spent',
        "value": str(total_cp_spent)
    },
    {
        "id": 'gitago.twitchextras.state.poll.top_bits_contributor',
        "value": str(top_bits_contrib)
    },
    {
        "id": 'gitago.twitchextras.state.poll.top_cp_contributor',
        "value": str(top_cp_contrib)
    },
    {
        "id": 'gitago.twitchextras.state.poll.top_contributor',
        "value": str(top_contrib)
    },
    {
        "id": 'gitago.twitchextras.state.poll.status',
        "value": "UPDATED"
    },
    ])







######### START LISTEN AUTO MOD QUEUE -  needs completed
#### I need help on getting this to be first in, first out for the entire list.. 
## so only one state to approve/deny.. and then this will cycle thru them as needeed..

alist = []
def callback_listen_automod_queue(uuid: UUID, data: dict) -> None:
    print('automod queue - got callback for UUID ' + str(uuid))
    global automod_case_list
    ## This is how it was prior then it decided to break and not let me append the dict to the list...
    #print(adict)
    adict = data.get('data')

    adict_copy = adict.copy()
    automod_case_list.append(adict_copy)

    get_new_case(automod_case_list)


    ###   adict = data.get('data')
    ###   alist = []
###   
    ###   current_case_id = (adict['message']['id'])
###   
    ###   case_level = (adict['content_classification']['level'])
    ###   case_category = (adict['content_classification']['category'])
###   
    ###   current_case_offender =(adict['message']['sender']['display_name'])
    ###   current_case_words = (adict['message']['content']['fragments'])
    ###   current_case_full_message = (adict['message']['content']['text'])
    ###   #print(adict)
###   
    ###   newdict = {
    ###       'current_case_id': adict['message']['id'],
    ###       'case_level': case_level,
    ###       'case_category': case_category,
    ###       'case_offender': current_case_offender,
    ###       'offending_words': current_case_words,
    ###       'full_message': current_case_full_message
    ###   }

    #pprint(newdict)



def callback_listen_undocumented_topic_predictions(uuid: UUID, data: dict) -> None:
    adict = data.get('data')
    print('undocumented - got callback for UUID ' + str(uuid))
    pprint(adict)
    checked_winning_name = ""  ## used for final states when winner is selected

    the_dict = adict['event']

    status = the_dict['status']
    ptitle = the_dict['title']
    ended_at = the_dict['ended_at']
    locked = the_dict['locked_at']
    prediction_id = the_dict['id']
    outcomes = (the_dict['outcomes'])
    prediction_1_dict = (the_dict['outcomes'][0])
    prediction_1_id = prediction_1_dict['id']
    prediction_1_votes = prediction_1_dict['total_users']
    prediction_1_cpoints = prediction_1_dict['total_points']
    prediction_1_title = prediction_1_dict['title'] 

    prediction_2_dict = (the_dict['outcomes'][1])
    prediction_2_id = prediction_2_dict['id']
    prediction_2_votes = prediction_2_dict['total_users']
    prediction_2_cpoints = prediction_2_dict['total_points']
    prediction_2_title = prediction_2_dict['title']  


    #### This could be made dyanmic since not everyone will get use out of them.. 


    if not ended_at:
        #print("its not ended yet, pick a winner...")
        ### if ended_at == NONE then it still needs icked...
        pass   
    if status == "LOCKED":
        print("Locked at: ", locked)
        #### LOCKED MEANS IT FINISHED LEGITIMATELY...

        TPClient.stateUpdateMany([
        {
            "id": 'gitago.twitchextras.state.prediction.title',
            "value": str(ptitle)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.status',
            "value": "LOCKED"
        },
        {
            "id": 'gitago.twitchextras.state.prediction.choice1',
            "value": str(prediction_1_title)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.choice2',
            "value": str(prediction_2_title)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.1points',
            "value": str(prediction_1_cpoints)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.2points',
            "value": str(prediction_2_cpoints)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.1votes',
            "value": str(prediction_2_votes)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.2votes',
            "value": str(prediction_2_votes)
        },
        ])       
         
        print("Prediction has ended, still have to pick a winner")

        ### TOP PREDICTORS NOT BEING USED YET...  SAVING TO TEXT FILE TO GET FULL DATA FROM WHEN MORE THAN ONE USER 
        blue_top_predictors = (adict['event']['outcomes'][0]['top_predictors'])
        pink_top_predictors = (adict['event']['outcomes'][1]['top_predictors'])

        save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras')
        with open(save_path + "\\top_predictors.txt", "a") as f:  ## Open and Append
            f.write("BLUE PREDICTORS \n")    
            f.write(json.dumps(blue_top_predictors,sort_keys=False, indent=4))
            f.write("\n\n\n" + "PINK PREDICTORS\n")
            f.write(json.dumps(pink_top_predictors,sort_keys=False, indent=4))
            f.write("\n\n\n")
        f.close()


    elif status == "CANCELED":
        print("lets clear all results")
        TPClient.stateUpdateMany([
        {
            "id": 'gitago.twitchextras.state.prediction.title',
            "value": ""
        },
        {
            "id": 'gitago.twitchextras.state.prediction.status',
            "value": "CANCELED"
        },
        {
            "id": 'gitago.twitchextras.state.prediction.choice1',
            "value": ""
        },
        {
            "id": 'gitago.twitchextras.state.prediction.choice2',
            "value": ""
        },
        {
            "id": 'gitago.twitchextras.state.prediction.1points',
            "value": ""
        },
        {
            "id": 'gitago.twitchextras.state.prediction.2points',
            "value": ""
        },
        {
            "id": 'gitago.twitchextras.state.prediction.1votes',
            "value": ""
        },
        {
            "id": 'gitago.twitchextras.state.prediction.2votes',
            "value": ""
        },
        ])


    elif status == "ACTIVE":
       # TPClient.stateUpdate("gitago.twitchextras.state.prediction.status", "ACTIVE") 
        print("It is now Active...")
        TPClient.stateUpdateMany([
        {
            "id": 'gitago.twitchextras.state.prediction.title',
            "value": str(ptitle)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.status',
            "value": "ACTIVE"
        },
        {
            "id": 'gitago.twitchextras.state.prediction.choice1',
            "value": str(prediction_1_title)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.choice2',
            "value": str(prediction_2_title)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.1points',
            "value": str(prediction_1_cpoints)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.2points',
            "value": str(prediction_2_cpoints)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.1votes',
            "value": str(prediction_2_votes)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.2votes',
            "value": str(prediction_2_votes)
        },
        ])



    elif status == "RESOLVED":
        #outcomes = (adict['event']['outcomes'])
        winning_id = adict['event']['winning_outcome_id']
        for a_dict in outcomes:
            for key in a_dict:
                if a_dict[key]=="BLUE":
                    color = "BLUE"
                    blue_id = a_dict['id']
                    blue_title = a_dict['title']
                    if blue_id == winning_id:
                        print(blue_title, " WINS!")
                        checked_winning_name = blue_title
                    
                if a_dict[key]=="PINK":
                    color = "PINK"
                    pink_id = a_dict['id']
                    pink_title = a_dict['title']
                    if pink_id == winning_id:
                        print(pink_title, " WINS!")
                        checked_winning_name = pink_title
                        
        TPClient.stateUpdateMany([
        {
            "id": 'gitago.twitchextras.state.prediction.title',
            "value": str(ptitle)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.status',
            "value": "RESOLVED"
        },
        {
            "id": 'gitago.twitchextras.state.prediction.choice1',
            "value": str(prediction_1_title)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.choice2',
            "value": str(prediction_2_title)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.1points',
            "value": str(prediction_1_cpoints)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.2points',
            "value": str(predictiontop_predict_2_cpoints)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.1votes',
            "value": str(prediction_2_votes)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.2votes',
            "value": str(prediction_2_votes)
        },
        {
            "id": 'gitago.twitchextras.state.prediction.winner_name',
            "value": str(checked_winning_name)
        },
        ])

        print("Prediction 2: ", prediction_2_title, "Votes:",  prediction_2_votes, "  |  Total Points Bet:", prediction_2_cpoints)
        #print(the_dict)

##########################################################################    
#########################################################################


try:
    ### Undocumented Listen Topics
    pubsub.listen_undocumented_topic(topic="following."+the_broadcaster_id, callback_func=callback_listen_undocumented_topic_following)
    pubsub.listen_undocumented_topic(topic="polls."+the_broadcaster_id, callback_func=callback_listen_undocumented_topic_polls)
    pubsub.listen_undocumented_topic(topic="predictions-channel-v1."+the_broadcaster_id, callback_func=callback_listen_undocumented_topic_predictions)   

    ### PUB SUB DOCUMENTED TOPICS
    pubsub.listen_automod_queue(the_broadcaster_id, the_broadcaster_id, callback_listen_automod_queue)
    pubsub.listen_whispers(the_broadcaster_id, callback_whisper)
    pubsub.listen_chat_moderator_actions(the_broadcaster_id, the_broadcaster_id, callback_listen_chat_moderator_actions)
    pubsub.listen_channel_subscriptions(the_broadcaster_id, callback_listen_channel_subcriptions)

    pubsub.start()
except TwitchAPIException as err:
    debug_log(f"[ERROR - PUBSUB] -> {err} - Trying to start PUBSUB after re-authing...")

    print("Trying to start PUBSUB after re-authing...",err)


print("Twitch_API.py loaded")


### running get_gifters..
#get_gifters()
#get_moderators()
