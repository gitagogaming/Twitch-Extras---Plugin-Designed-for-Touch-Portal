"""
Gitago's Twitch Extras Plugin
"""
from CHATBOT_20 import *



from twitch_api import * 
from t_imports import *
from user_database import *

#### TWITCH API AND PREDICTIONS AND OTHER THINGS IMPORTED AT LINE 830 ish


# Crate the (optional) global logger
g_log = getLogger()


def handleSettings(settings, on_connect=False):
    settings = { list(settings[i])[0] : list(settings[i].values())[0] for i in range(len(settings)) }
    broadcaster_username_TP = settings['Twitch Username']
    oath_token_unformatted = settings['Chatbot OAUTH Token']
    chatbot_name_TP = settings['Chatbot Username']

    chatbot_channel_name = broadcaster_username_TP #setting chatbot channel same as broadcaster
    
    splittoken = oath_token_unformatted.split(':') ## Incase someone tosses in the oath: portion of the token lets remove it...
    chatbot_oauth_TP = (splittoken[-1])

    ###loading json file and writing username to it for twitchapi.py to utilize..
    try:
        ### Reading Config
        save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras')
        a_file = open(save_path +"\main_config.json", "r")
        the_config = json.load(a_file)
        #print(the_config)
        a_file.close()

        ### Editing Config
        the_config['Broadcaster Username'] = broadcaster_username_TP

        ### Resaving Config
        save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras')
        a_file = open(save_path +"\main_config.json", "w")
        text = json.dumps(the_config, sort_keys=False, indent=4)
        a_file.write(text)
        a_file.close()
        print("Updated Config File: ", the_config)
    except (FileNotFoundError, IOError):
        if debug:
            fullerror = "Load Config Auth: "+ str(IOError)
            debug_log(fullerror)
            print("Wrong file or file path")
    


    ### now lets load the chatbot config..
    try:
        #save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras')
        chat_config = open(save_path +"\chat_config.json", "r")  ## Open and Read
        the_chatconfig_dict = json.load(chat_config)
        chat_config.close()

        the_chatconfig_dict[1]['Chatbot Token'] = chatbot_oauth_TP
        the_chatconfig_dict[1]['Chatbot Name'] = chatbot_name_TP
        the_chatconfig_dict[1]['Chatbot Channel'] = chatbot_channel_name.lower()


        ## and now lets save it with updated info from TP settings..

        a_file = open(save_path +"\chat_config.json", "w")  ## Open and Write
        text = json.dumps(the_chatconfig_dict, sort_keys=False, indent=4)
        a_file.write(text)
        a_file.close()

    except (FileNotFoundError, IOError):
        if debug:
            fullerror = "Load Config Auth: "+ str(IOError)
            debug_log(fullerror)
            print("Wrong file or file path")



"""
#------------------------------------------#
#- TOUCHPORTAL EVENT HANDLER / CALL BACKS -#
#------------------------------------------#
"""
@TPClient.on(TP.TYPES.onConnect)
def onConnect(data):
    g_log.info(f"Connected to TP v{data.get('tpVersionString', '?')}, plugin v{data.get('pluginVersion', '?')}.")
    g_log.debug(f"Connection: {data}")
    if settings := data.get('settings'):
        handleSettings(settings, True)

    #import create_preditions

    ## Creating this state on connect so its fresh in list and not in a category.
    TPClient.createState("gitago.twitchextras.state.on_follow", "TE | New Follower Name", "")

    TPClient.stateUpdate("gitago.twitchextras.state.automod.case_offender", "NO CASES")
    TPClient.stateUpdate("gitago.twitchextras.state.automod.case_id", "")
    TPClient.stateUpdate("gitago.twitchextras.state.automod.case_word", "")
    TPClient.stateUpdate("gitago.twitchextras.state.automod.case_count", "")
    TPClient.stateUpdate("gitago.twitchextras.state.automod.case_fullmessage", "")
    ###import here temporarily for testing
    
    TPClient.stateUpdate(stateId="gitago.twitchextras.state.emotes_only", stateValue="")
    TPClient.stateUpdate(stateId="gitago.twitchextras.state.followers_only", stateValue="")
    TPClient.stateUpdate(stateId="gitago.twitchextras.state.subscribers_only", stateValue="")
    TPClient.stateUpdate(stateId="gitago.twitchextras.state.slow_mode", stateValue="")

    
    TPClient.stateUpdate(stateId="gitago.twitchextras.state.on_follow", stateValue="")

    #choices = {'id': '76dbd1cd-da1b-460b-b38c-01db32647b11', 'title': 'choice 1', 'votes': 0, 'channel_points_votes': 0, 'bits_votes': 0}, {'id': '24e95a23-9f3f-49a2-8bd5-4abe2bc0cdfa', 'title': 'choice 2', 'votes': 0, 'channel_points_votes': 0, 'bits_votes': 0}, {'id': '3374c595-ffa0-49aa-b845-29e95728bc36', 'title': 'choice 3', 'votes': 0, 'channel_points_votes': 0, 'bits_votes': 0}



# Settings handler
@TPClient.on(TP.TYPES.onSettingUpdate)
def onSettingUpdate(data):
    g_log.debug(f"Settings: {data}")
    if (settings := data.get('values')):
        handleSettings(settings, False)




"""
#------------------------------------------#
#--------------- IMPORTS   ----------------#
#------------------------------------------#
"""
##### TWITCH_API.PY AND CREATE PREDICTIONS IMPORTED HERE
##### TWITCH_API.PY AND CREATE PREDICTIONS IMPORTED HERE
##  Disabled and moved to t_imports.py    from websockets.legacy.client import *
##  Disabled and moved to t_imports.py    from websockets.extensions import *
##  Disabled and moved to t_imports.py    from websockets.legacy import *
#from chat_bot import * 
#from CHATBOT_20 import *
#from twitch_api import *    ### this imports twitch_api.py so it can communicate
#import create_preditions
##### TWITCH_API.PY AND CREATE PREDICTIONS IMPORTED HERE
##### TWITCH_API.PY AND CREATE PREDICTIONS IMPORTED HERE


#from t_imports import *

# Action handler
@TPClient.on(TP.TYPES.onAction)
def onAction(data):
    pprint(data)

    ## Prediction Start
    if data['actionId'] == "gitago.twitchextras.act.prediction":
        predictiontitle = TPClient.getActionDataValue(data.get("data"), "gitago.twitchextras.act.prediction.ptitle")
        predictiontime = TPClient.getActionDataValue(data.get("data"), "gitago.twitchextras.act.prediction.ptime")
        prediction1choice = TPClient.getActionDataValue(data.get("data"), "gitago.twitchextras.act.prediction.p1choice")
        prediction2choice = TPClient.getActionDataValue(data.get("data"), "gitago.twitchextras.act.prediction.p2choice")
        create_preditions.create_prediction(prediction1choice, prediction2choice, predictiontitle, int(predictiontime))

    if data['actionId'] == "gitago.twitchextras.act.prediction.cancelprediction":
        create_preditions.end_the_prediction("CANCELTHIS")  

    ###Prediction Pick Winner
    if data['actionId'] == "gitago.twitchextras.act.prediction.pickwinner":
        predictionwinner = TPClient.getActionDataValue(data.get("data"), "gitago.twitchextras.act.prediction.choice")
        if predictionwinner =="Choice 1":
            create_preditions.end_the_prediction("choice1")
        elif predictionwinner =="Choice2":
            create_preditions.end_the_prediction("choice2")

    ### Get User Info (display name, id, profile image, view count, created at, follows)
    if data['actionId'] == "gitago.twitchextras.act.getuserinfo":
        retrieve_info_user_name = TPClient.getActionDataValue(data.get("data"), "gitago.twitchextras.act.getuserinfo.name")
        get_user_info(retrieve_info_user_name, "request")  #located in twitch_api
        pass

    if data['actionId'] == "gitago.twitchextras.act.getuserclips":
        amount_clips = TPClient.getActionDataValue(data.get("data"), "gitago.twitchextras.act.getuserclips.amount")
        retrieve_clips_user_name = TPClient.getActionDataValue(data.get("data"), "gitago.twitchextras.act.getuserclips.name")
        get_clips(retrieve_clips_user_name, amount_clips)

    if data['actionId'] == "gitago.twitchextras.act.getuserfolloage":
         follow_age_name = TPClient.getActionDataValue(data.get("data"), "gitago.twitchextras.act.getuserfolloage.name")
         #followage(follow_age_name, "months")
         followage(follow_age_name, "full")

    if data['actionId'] == "gitago.twitchextras.act.createreward":
        r_title = TPClient.getActionDataValue(data.get("data"),"gitago.twitchextras.act.createreward.title")
        r_cost = TPClient.getActionDataValue(data.get("data"),"gitago.twitchextras.act.createreward.cost")
        r_color = TPClient.getActionDataValue(data.get("data"),"gitago.twitchextras.act.createreward.color")
        user_input_req = TPClient.getActionDataValue(data.get("data"),"gitago.twitchextras.act.createreward.inputreq")
        r_maxperstream = TPClient.getActionDataValue(data.get("data"),"gitago.twitchextras.act.createreward.maxperstream")
        r_maxperuser = TPClient.getActionDataValue(data.get("data"),"gitago.twitchextras.act.createreward.maxperuser")
        r_globalcd = TPClient.getActionDataValue(data.get("data"),"gitago.twitchextras.act.createreward.globalcooldown")
        skip_queue = TPClient.getActionDataValue(data.get("data"),"gitago.twitchextras.act.createreward.skipqueue")

        create_rewards(r_title, r_cost, r_color, r_maxperstream, r_maxperuser, r_globalcd, skip_queue, user_input_req) #located in twitch_api
        time.sleep(5)
  
         

    if data['actionId'] == "gitago.twitchextras.act.retrievechannelrewards":
        get_rewards() #located in twitch_api
    
    if data['actionId'] == "gitago.twitchextras.act.deletereward":
        delete_id = TPClient.getActionDataValue(data.get("data"),"gitago.twitchextras.act.deletereward.id")
        delete_reward(delete_id)  #located in twitch_api


    if data['actionId'] == "gitago.twitchextras.act.calculate_level":
        username = TPClient.getActionDataValue(data.get("data"),"gitago.twitchextras.act.calculatelevel.name")
        dict = twitch.get_users(logins=[username])['data'][0]
        ### triggering get_gifters to find out total gift count...
        #get_gifters()
        get_gifters_fresh()
        

        #print(dict)
        if dict:       
            user_id = dict['id']
            ## running follow_age from twitch_api, since its ciruclar dependency from user_database.py
            #returning a dictionary if following, returning 'non_follower' if not...
            follow_age_dict = followage_months(user_id)  
            if follow_age_dict == "NON_FOLLOWER":
                follow_age = 0
                calculate_points(user_id, follow_age, dict)
            else:
                calculate_points(user_id, follow_age_dict, dict)  ## located in user_database
        elif not dict:
            print("The Dict is empty when Getting user Info... are they banned?")
        
    if data['actionId'] == "gitago.twitchextras.act.poll.start":
        poll_list = []
        poll_title = data['data'][0]['value']
        choice1 = data['data'][1]['value']
        choice2 = data['data'][2]['value']
        choice3 = data['data'][3]['value']
        choice4 = data['data'][4]['value']
        choice5 = data['data'][5]['value']
        poll_duration = data['data'][6]['value']
        cpoints_per_vote = data['data'][7]['value']
        poll_list.extend((choice1, choice2, choice3, choice4, choice5))

        create_preditions.create_poll(poll_title, poll_list, int(poll_duration), int(cpoints_per_vote))

    if data['actionId'] == "gitago.twitchextras.act.poll.end_poll":
       # close_chatbot_thread()
        ## end poll was bugging out
        #create_preditions.end_poll()
        pass

    if data['actionId'] == "gitago.twitchextras.act.save_chatbadges":
        get_badges()

    if data['actionId'] == "gitago.twitchextras.act.automod_action":
        automod_decision = data['data'][0]['value']
        confirm_case(automod_decision)

    if data['actionId'] == "gitago.twitchextras.act.check_raidlist":
        create_preditions.check_raid_list()

    g_log.debug(f"Action: {data}")
    if not (action_data := data.get('data')) or not (aid := data.get('actionId')):
        return
 
    #else:
     #   g_log.warning("Got unknown action ID: " + aid)







# Shutdown handler
@TPClient.on(TP.TYPES.onShutdown)
def onShutdown(data):
    try:
        g_log.info('Received shutdown event from TP Client.')        
        #### this may need globaled
        stop_run_continuously.set()
        schedule.clear()
        ##closing database
        cur.close()
        conn.close()
        ##unlistening to everything twitch related
        pubsub.unlisten(uuid=callback_listen_undocumented_topic_predictions)
        pubsub.unlisten(uuid=callback_listen_undocumented_topic_polls)
        pubsub.unlisten(uuid=callback_listen_undocumented_topic_following)
        pubsub.unlisten(uuid=callback_listen_automod_queue)
        pubsub.unlisten(uuid=callback_whisper)
        pubsub.unlisten(uuid=callback_listen_automod_queue)
        pubsub.unlisten(uuid=callback_listen_chat_moderator_actions)
        pubsub.stop()  ## stopping pubsub.. 
        
        
        ##shutting down chatbot connection.
        #bot_shutdown()
        stop_run_continuously.set()
       #t1.stop()

        TPClient.disconnect()
      #  close_chatbot_thread()
      # os.system("TASKKILL /F /IM twitch_extras.exe")
      # for process in (process for process in psutil.process_iter(print(psutil.process_iter)) if process.name()=="twitch_extras.exe"):
      #     process.kill()
    
        sys.exit()
       
    except (ConnectionResetError,AttributeError):
        pass
    
    #sys.exit()
    
    exit(0)




##  Error handler
## @TPClient.on(TP.TYPES.onError)
## def onError(exc):
##   g_log.error(f'Error in TP Client event handler: {repr(exc)}')
##   # ... do something ?
## 
## 
##  main
## def main():
##   global TPClient, g_log
##   ret = 0  # sys.exit() value
## 
##   # handle CLI arguments
##   parser = ArgumentParser()
##   parser.add_argument("-d", action='store_true',
##                       help="Use debug logging.")
##   parser.add_argument("-w", action='store_true',
##                       help="Only log warnings and errors.")
##   parser.add_argument("-q", action='store_true',
##                       help="Disable all logging (quiet).")
##   parser.add_argument("-l", metavar="<logfile>",
##                       help="Log to this file (default is stdout).")
##   parser.add_argument("-s", action='store_true',
##                       help="If logging to file, also output to stdout.")
## 
##   opts = parser.parse_args()
##   del parser
## 
##   # set up logging
##   if opts.q:
##       # no logging at all
##       g_log.addHandler(NullHandler())
##   else:
##       # set up pretty log formatting (similar to TP format)
##       fmt = Formatter(
##           fmt="{asctime:s}.{msecs:03.0f} [{levelname:.1s}] [{filename:s}:{lineno:d}] {message:s}",
##           datefmt="%H:%M:%S", style="{"
##       )
##       # set the logging level
##       if   opts.d: g_log.setLevel(DEBUG)
##       elif opts.w: g_log.setLevel(WARNING)
##       else:        g_log.setLevel(INFO)
##       # set up log destination (file/stdout)
##       if opts.l:
##           try:
##               # note that this will keep appending to any existing log file
##               fh = FileHandler(str(opts.l))
##               fh.setFormatter(fmt)
##               g_log.addHandler(fh)
##           except Exception as e:
##               opts.s = True
##               print(f"Error while creating file logger, falling back to stdout. {repr(e)}")
##       if not opts.l or opts.s:
##           sh = StreamHandler(sys.stdout)
##           sh.setFormatter(fmt)
##           g_log.addHandler(sh)
## 
##   # ready to go
##   g_log.info(f"Starting {TP_PLUGIN_INFO['name']} v{__version__} on {sys.platform}.")
## 
##   try:
##       print("Connected TP")
##       # Connect to Touch Portal desktop application.
##       # If connection succeeds, this method will not return (blocks) until the client is disconnected.
##       TPClient.connect()
##       g_log.info('TP Client closed.')
##   except KeyboardInterrupt:
##       g_log.warning("Caught keyboard interrupt, exiting.")
##   except Exception:
##       from traceback import format_exc
##       g_log.error(f"Exception in TP Client:\n{format_exc()}")
##       ret = -1
##   finally:
##       # Make sure TP Client is stopped, this will do nothing if it is already disconnected.
##       TPClient.disconnect()
##       #bot_shutdown()
## 
##   # TP disconnected, clean up.
##   del TPClient
## 
##   g_log.info(f"{TP_PLUGIN_INFO['name']} stopped.")
##   return ret






print("Connected TP")  
TPClient.connect()




#### Quoted this out when fixing the plugin staying open
##
##if __name__ == "__main__":
##    sys.exit(main())
    

