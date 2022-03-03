
print("Create_predictions.py Loaded")


##########################################################################################################################################
##########################################################################################################################################
from twitchAPI.types import PollStatus, TwitchAuthorizationException
from twitch_api import *
#from nothing import TPClient   ## this is causing circular dependency... 
from tpclient import *  ### put TP client details in tpclient.py so now its shard info amongst all py files?
#########################



save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras')
a_file = open(save_path +"\main_config.json", "r")
the_config = json.load(a_file)
a_file.close()
current_token = the_config.get('Current Token')
a_refresh_token = the_config.get('Refresh Token')
the_broadcaster_id = the_config.get('Broadcaster ID')


global the_poll_id

                                                    ## make it so if its enabled then it does tag for enabling plus sets points per vote
def create_poll(poll_title, choice_list, poll_duration, cpoints_per_vote):
    try:
        if cpoints_per_vote == 0:
            new_poll_dict = twitch.create_poll(broadcaster_id=the_broadcaster_id, title=poll_title, choices=choice_list, duration=poll_duration)
        else:
            new_poll_dict = twitch.create_poll(broadcaster_id=the_broadcaster_id, title=poll_title, choices=choice_list, duration=poll_duration, 
                                                                                        channel_points_voting_enabled=True, channel_points_per_vote=cpoints_per_vote)
        global the_poll_id
        poll_dict_brokedown = new_poll_dict['data'][0]  
        the_poll_id = poll_dict_brokedown['id']
        poll_duration = poll_dict_brokedown['duration']
        poll_title = poll_dict_brokedown['title']
    except TwitchAPIException as err:
        fullerror = (f"[ERROR - create_poll] -> {err}, Are you an Affiliate or Partner?")
        debug_log(fullerror)

        ## Sending Poll Title to Touchportal
        TPClient.stateUpdate(stateId="gitago.twitchextras.state.poll.title",stateValue=str(poll_title))

    ## Poll Created, Lets Get Poll Info and Loop over it until its completed.
    #    get_poll(the_poll_id, poll_duration)

    #   for dict in poll_dict_brokedown:
    #       print(dict, poll_dict_brokedown[dict])

   ## this for loop breaks down the choices, votes, title, ID for the choice and other details
   ## and creates variable for it
   ##   x=0
   ##   for dict in new_poll_dict['data'][0]['choices']:
   ##       x = x + 1
   ##       for key in dict:
   ##           newkey = key + "_" + str(x)
   ##           exec(newkey + '=dict[key]')




####     Function get_poll no longer used since we are LISTENING to the topic to get the info at all times.
####   def get_poll(the_poll_id, p_time):
####       p_time = int(p_time)
####       loop_seconds = 4
####       loop_times = p_time // loop_seconds
####       print("ok we getting poll info..")
####   
####       ## wont even bother with loop if duration isnt longer then 10, just extra failsafe.
####       if p_time > 10:
####           for i in range(loop_times):
####               get_poll_dict = twitch.get_polls(broadcaster_id=the_broadcaster_id, poll_id=the_poll_id)
####               poll_dict_brokedown = get_poll_dict['data'][0]
####               poll_status = poll_dict_brokedown['status']
####               pprint (get_poll_dict)
####   
####               ## this for loop breaks down the choices, votes, title, ID for the choice and other details
####               x=0
####               for dict in poll_dict_brokedown['choices']:
####                   x = x + 1
####                   for key in dict:
####                       newkey = key + "_" + str(x)
####                       exec(newkey + '=dict[key]')
####   
####                       #TPClient.createState("gitago.twitchextras.state.poll."+str(newkey) +str(x) +".name", "TE | Poll Status " +str(x) + " Title  ||  " + str((dict[key])), "")    
####                       #TPClient.stateUpdate("gitago.twitchextras.state.poll."+str(newkey) +str(x) +".name", str((dict[key])))
####                       # TPClient.createState(stateId=f'gitago.twitchextras.state.poll.{newkey}', description=newkey, value="")
####                       print("State to be Updated: gitago.twitchextras.state.poll2."+newkey)
####                       TPClient.stateUpdate(stateId=f'gitago.twitchextras.state.poll.{newkey}', stateValue= str(dict[key]))  # dict[key]
####   
####   
####               ### maybe we should just update only the wanted states with updatestatemany (for now it will update ALL)
####               the_poll_id = poll_dict_brokedown['id']
####               poll_duration = poll_dict_brokedown['duration']
####               choice1_votes = poll_dict_brokedown['choices'][0]['votes']
####   
####               pprint (poll_dict_brokedown)
####               print("current votes ", choice1_votes)
####             
####               time.sleep(loop_seconds)
####   
####               if poll_status =="COMPLETED":
####                   print("Poll has Concluded, stop the loop")
####                   break
####   


#### Error in TP Client event handler: TypeError('keys must be str, int, float, bool or None, not PollStatus') 
def end_poll():
    twitch.end_poll(broadcaster_id=the_broadcaster_id, poll_id=str(the_poll_id), status="TERMINATED")




### create poll sample
#create_poll("ok", "the list", 5, True, False)

######### NEED TO MAKE GET_PREDICTIONS LOOP for EVERY X seconds for Y cycles based on the Prediction Length set...
### Need to get END Predictions to work...
class predictionssss:
    pass ## would love to know how to use a class here i think?

#TPClient.stateUpdate("gitago.twitchextras.state.prediction.title","Meeeh")


def get_predictions(p_time, p_id):
    if p_id == "helpme":
        print("we must need help.. MAYDAY!")
        global prediction_id
        global prediction_2_id
        global prediction_1_id
        dict = twitch.get_predictions(broadcaster_id=the_broadcaster_id, first=1)
        the_dict = dict['data'][0]
        #pprint(dict)

        status = the_dict['status']
        ptitle = the_dict['title']
        ended_at = the_dict['ended_at']
        locked = the_dict['locked_at']
        prediction_id = the_dict['id']

        prediction_1_dict = (the_dict['outcomes'][0])
        prediction_1_id = prediction_1_dict['id']
        prediction_1_votes = prediction_1_dict['users']
        prediction_1_cpoints = prediction_1_dict['channel_points']
        prediction_1_title = prediction_1_dict['title'] 

        prediction_2_dict = (the_dict['outcomes'][1])
        prediction_2_id = prediction_2_dict['id']
        prediction_2_votes = prediction_2_dict['users']
        prediction_2_cpoints = prediction_2_dict['channel_points']
        prediction_2_title = prediction_2_dict['title']  
        
        #### This could be made dyanmic since not everyone will get use out of them.. 

        TPClient.stateUpdate("gitago.twitchextras.state.prediction.title", ptitle)
        TPClient.stateUpdate("gitago.twitchextras.state.prediction.choice1", prediction_1_title)
        TPClient.stateUpdate("gitago.twitchextras.state.prediction.choice2", prediction_2_title)
        TPClient.stateUpdate("gitago.twitchextras.state.prediction.1points", prediction_1_cpoints)
        TPClient.stateUpdate("gitago.twitchextras.state.prediction.1votes", prediction_1_votes)
        TPClient.stateUpdate("gitago.twitchextras.state.prediction.2points", prediction_2_cpoints)
        TPClient.stateUpdate("gitago.twitchextras.state.prediction.2votes", prediction_2_votes)    



        

    p_time = int(p_time)
    loop_seconds = 3
    loop_times = p_time // loop_seconds
    #dict = twitch.get_predictions(broadcaster_id=the_broadcaster_id, prediction_ids="246e4385-2dd6-42ee-a11e-6f11ccabb424",first=1)
    ### currently loops over and get_predictions every X seconds, updating those variables needed which is the vote count for each side and the bits bet so far..

    ### Prediction 1 Data we don't need to for loop over..
    
    if p_time > 5:
        for i in range(loop_times):
            dict = twitch.get_predictions(broadcaster_id=the_broadcaster_id, prediction_ids=p_id,first=1)
            the_dict = dict['data'][0]
            status = the_dict['status']
            ended_at = the_dict['ended_at']
            locked = the_dict['locked_at']
            prediction_id = the_dict['id']

            if not ended_at:
                #print("its not ended yet, pick a winner...")
                ### if ended_at == NONE then it still needs icked...
                pass   
            if status == "LOCKED":
                print("Locked_at: ", locked)
                ### Trigger an event here?? When Prediction Ended ??

                #updating states once more for "good luck"
                TPClient.stateUpdate("gitago.twitchextras.state.prediction.1points", prediction_1_cpoints)
                TPClient.stateUpdate("gitago.twitchextras.state.prediction.1votes", prediction_1_votes)
                TPClient.stateUpdate("gitago.twitchextras.state.prediction.2points", prediction_2_cpoints)
                TPClient.stateUpdate("gitago.twitchextras.state.prediction.2votes", prediction_2_votes)    
                print("Time to Trigger the Results")
                break

            elif status == "CANCELED":
                print("lets clear all results")
                TPClient.stateUpdate("gitago.twitchextras.state.prediction.title", "")
                TPClient.stateUpdate("gitago.twitchextras.state.prediction.choice1", "")
                TPClient.stateUpdate("gitago.twitchextras.state.prediction.choice2", "")
                TPClient.stateUpdate("gitago.twitchextras.state.prediction.1points", "")
                TPClient.stateUpdate("gitago.twitchextras.state.prediction.1votes", "")
                TPClient.stateUpdate("gitago.twitchextras.state.prediction.2points", "")
                TPClient.stateUpdate("gitago.twitchextras.state.prediction.2votes", "")   

                break
            elif status == "RESOLVED":
                print("this is an old prediction, what are we doing here?")
                break
            elif status == "ACTIVE":
                print("Still Active...")

            #### Prediction 1 Data     ## this could possibly be optimized a little bit to not spend time updating the variables for title, color and ID.. 
            ### since these are things that will be set in stone til next prediction
            prediction_1_dict = (the_dict['outcomes'][0])
            prediction_1_votes = prediction_1_dict['users']
            prediction_1_cpoints = prediction_1_dict['channel_points']
            ###
            #prediction_1_id = prediction_1_dict['id']
            prediction_1_title = prediction_1_dict['title'] ## winner prediction ID is passed off from another function, we dont need to know the ID anymore , just the title
            #prediction_1_color = prediction_1_dict['color']  #not sure how useful this really is.. you cannot change color, always blue/pink far as i know.
            #prediction_1_top = prediction_1_dict['top_predictors']  #a list of the people who have top predictions.. (not currentling using this)

            print("Prediction 1: ", prediction_1_title, "The Votes:", prediction_1_votes, "Total Points Bet:", prediction_1_cpoints)


            #### Prediction 2 Data 
            ### The Data that needs sent to TP as updates
            prediction_2_dict = (the_dict['outcomes'][1])
            prediction_2_votes = prediction_2_dict['users']
            prediction_2_cpoints = prediction_2_dict['channel_points']
            ####
            #prediction_2_id = prediction_2_dict['id']      ## winner prediction ID is passed off from another function, we dont need to know the ID anymore , just the title
            #prediction_2_color = prediction_2_dict['color']
            prediction_2_title = prediction_2_dict['title']        
            #prediction_2_top = prediction_2_dict['top_predictors']

            TPClient.stateUpdate("gitago.twitchextras.state.prediction.1points", str(prediction_1_cpoints))
            TPClient.stateUpdate("gitago.twitchextras.state.prediction.1votes", str(prediction_1_votes))
            TPClient.stateUpdate("gitago.twitchextras.state.prediction.2points", str(prediction_2_cpoints))
            TPClient.stateUpdate("gitago.twitchextras.state.prediction.2votes", str(prediction_2_votes))

            print("Prediction 2: ", prediction_2_title, "Votes:",  prediction_2_votes, "  |  Total Points Bet:", prediction_2_cpoints)
            #print(the_dict)
            time.sleep(loop_seconds)
#get_predictions(1)



#THE DICT - CREATE PRED: {'error': 'Forbidden', 'status': 403, 'message': 'channel points not enabled'}

global prediction_id
global prediction_1_id
global prediction_2_id
def create_prediction(item1, item2, p_title, p_time):
    global prediction_1_id
    global prediction_2_id
    global prediction_id
    p_time = int(p_time)
    teams = [item1, item2]
    #the_broadcaster_id = "197028355"
    try:
        dict =twitch.create_prediction(broadcaster_id=the_broadcaster_id, title=p_title, outcomes=teams, prediction_window=p_time)
        errorcheck = dict.get('error')
        if errorcheck:
            if dict['error']:
                fullerror = (f"[ERROR - create_predictions] -> {dict['status']} | {dict['message']}")
                debug_log(fullerror)
                print(fullerror)
        else:
            print("THE DICT - CREATE PRED:",dict)
            the_dict = dict['data'][0]
            print("The Creation")
            pprint(the_dict)

            ###making globals for prediciton ID's so it can be used in end precition
            prediction_id = the_dict['id'] 
            print("THE PREDICTION ID", prediction_id)    
            #### Prediction 1 Data 
            prediction_1_dict = (the_dict['outcomes'][0])
            #pprint(prediction_1_dict)
            prediction_1_id = prediction_1_dict['id']
            prediction_1_title = prediction_1_dict['title']
            prediction_1_color = prediction_1_dict['color']
            prediction_1_votes = prediction_1_dict['users']
            prediction_1_cpoints = prediction_1_dict['channel_points']
            prediction_1_top = prediction_1_dict['top_predictors']

            ### Prediction 2 Data
            prediction_2_dict = (the_dict['outcomes'][1])
            #pprint(prediction_2_dict)
            prediction_2_id = prediction_2_dict['id']
            prediction_2_title = prediction_2_dict['title']
            prediction_2_color = prediction_2_dict['color']
            prediction_2_votes = prediction_2_dict['users']
            prediction_2_cpoints = prediction_2_dict['channel_points']
            prediction_2_top = prediction_2_dict['top_predictors']

            print("Prediction 1 :", prediction_1_color, prediction_1_title, prediction_1_id, prediction_1_cpoints, prediction_1_votes, prediction_1_top)
            print("Prediction 2 :", prediction_2_color, prediction_2_title, prediction_2_id, prediction_2_cpoints, prediction_2_votes, prediction_2_top)

            TPClient.stateUpdateMany([
            {
                "id": 'gitago.twitchextras.state.prediction.title',
                "value": str(p_title)
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


            ###Now send to get_predictions for looping this data
            #get_predictions(p_time, prediction_id)
    except UnauthorizedException as err:
        debug_log(f"[ERROR - create_predictions \ create ] - > {err}")
    except TwitchAPIException as err:
        print(err)
        if err:
            print("Prediction must need chosen first...")
            ### lets gather that info again...
            dict = twitch.get_predictions(broadcaster_id=the_broadcaster_id,first=1)
            the_dict = dict['data'][0]
            status = the_dict['status']
            ended_at = the_dict['ended_at']
            locked = the_dict['locked_at']
            prediction_id = the_dict['id']
            if dict:
                TPClient.stateUpdateMany([
                {
                    "id": 'gitago.twitchextras.state.prediction.title',
                    "value": str(p_title)
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
            else:
                print("We received an error, Predictions came back empty.. user must not be an affiliate or partner")
                debug_log(f"[ERROR - create_prediction / Create Prediction ->  Predictions are EMPTY.  Are you an Affiliate/Partner?")

                TPClient.stateUpdate("gitago.twitchextras.state.prediction.title", "Must be Affiliate or Partner")
#create_prediction("success", "Stesam", "Another Test", 60)
    except NameError as err:
        print("The name error", err )






def end_the_prediction(winning_id):
    #print(winning_id)
    if winning_id == "choice1":
        try:
            twitch.end_prediction(broadcaster_id=the_broadcaster_id, prediction_id=prediction_id,winning_outcome_id=prediction_1_id, status=PredictionStatus.RESOLVED)
        except NameError as err2:
            dict = twitch.get_predictions(broadcaster_id=the_broadcaster_id,first=1)
            if dict['data']:
                the_dict = (dict['data'][0])
                recovered_id = (the_dict['id'])
                choice1_id = the_dict['outcomes'][0]['id']
                try:
                    twitch.end_prediction(broadcaster_id=the_broadcaster_id, prediction_id=recovered_id,winning_outcome_id=choice1_id, status=PredictionStatus.RESOLVED)
                except:
                    debug_log("[ERROR - end_prediction / Choice 1] - No Active Prediction, Cannot Select Winner.")
            elif not dict['data']:
                debug_log("[ERROR - end_prediction / Pick Winner Choice 1] -> Predictions are EMPTY, Are you an Affiliate/Partner?")
        except TwitchAPIException as err:
            debug_log(f"[ERROR - end_prediction] - pick a winner - {err}")
        except ValueError as err:
            print(err)
            print("prediction already ended, so  you can't end it, go pick a winner instead")


    if winning_id == "choice2":
        try:
            twitch.end_prediction(broadcaster_id=the_broadcaster_id, prediction_id=prediction_id,winning_outcome_id=prediction_2_id, status=PredictionStatus.RESOLVED)
        except NameError as err2:
            print("Name Error Occured on Choice 2 Selecting Winner: ")
            dict = twitch.get_predictions(broadcaster_id=the_broadcaster_id,first=1)

            ## if data exists...
            if dict['data']:
                the_dict = (dict['data'][0])
                recovered_id = (the_dict['id'])
                choice2_id = the_dict['outcomes'][1]['id']
                try:
                    twitch.end_prediction(broadcaster_id=the_broadcaster_id, prediction_id=recovered_id,winning_outcome_id=choice2_id, status=PredictionStatus.RESOLVED)
                except:
                    debug_log("[ERROR - end_prediction / Choice 2] - No Active Prediction, Cannot Select Winner.")
            elif not dict['data']:
                debug_log("[ERROR - end_prediction / Pick Winner Choice 2] -> Predictions are EMPTY, Are you an Affiliate/Partner?")
        except ValueError as err:
            print(err)
            print("prediction already ended, so  you can't end it, go pick a winner instead")
    
    if winning_id =="CANCELTHIS":
        try:
            twitch.end_prediction(broadcaster_id=the_broadcaster_id, prediction_id=prediction_id, status=PredictionStatus.CANCELED)
            
        except NameError as err:
            #print("must be invalid ID.. lets get it.. ")
            dict = twitch.get_predictions(broadcaster_id=the_broadcaster_id,first=1)
            errorcheck = dict.get('data')
            if errorcheck:
                if dict['data']:   
                    the_dict = (dict['data'][0])
                    recovered_id = (the_dict['id'])
                    try:
                        twitch.end_prediction(broadcaster_id=the_broadcaster_id, prediction_id=recovered_id, status=PredictionStatus.CANCELED)
                    except:
                         debug_log("[ERROR - end_prediction / Cancel Prediction] -> Tried to Cancel, but no active predictions.")
                elif not dict['data']:
                    debug_log("[ERROR - end_prediction / Cancel Prediction] -> Predictions are EMPTY, Are you an Affiliate/Partner?")
        except TwitchAPIException as err:
            debug_log(f"[ERROR - end_prediction / Cancel Prediction -> Are you an Affiliate/Partner?")








##########################################################################################################################################
##########################################################################################################################################
##########################################################################################################################################
##########################################################################################################################################



#### CHECK RAID LIST ####

#raid_list = []


#save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras\lists')
#raid_list_file = open(save_path +"\Raid_Chat_List.txt", "r")
#with raid_list_file as f:
#    lines = f.readlines()
#    raid_list = []
#    for line in lines:
#        stripped_line = line.rstrip()
#        raid_list.append(stripped_line)
#    f.close()

#print(raid_list)

def check_raid_list():
    raid_list = []
    save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras\lists')
    raid_list_file = open(save_path +"\Raid_Chat_List.txt", "r")
    with raid_list_file as f:
        lines = f.readlines()
        raid_list = []
        for line in lines:
            stripped_line = line.rstrip()
            raid_list.append(stripped_line)
        f.close()
    #print(raid_list)
    loop = 15
    for num in range(loop):
        TPClient.stateUpdateMany([
        {
            "id": f'gitago.twitchextras.state.raidcheck_{num}.user_name',
            "value": ""
        },
        {
            "id": f'gitago.twitchextras.state.raidcheck_{num}.game_name',
            "value": ""
        },
        {
            "id": f'gitago.twitchextras.state.raidcheck_{num}.mature',
            "value": ""
        },
        {
            "id": f'gitago.twitchextras.state.raidcheck_{num}.title',
            "value": ""
        },
        {
            "id": f'gitago.twitchextras.state.raidcheck_{num}.views',
            "value": ""
        },
        {
            "id": f'gitago.twitchextras.state.raidcheck_{num}.livetime',
            "value": ""
        }
        ])
    channels_online = 0
    x = 0
    for channel in raid_list:
        thedeets = twitch.get_streams(user_login=channel)
        check = (thedeets['data'])
        pprint(check)
        if check:
            channels_online = channels_online + 1
            x = x + 1
            ### If check, then they are online so lets create + update states.
            user_name = check[0]['user_name']
            game_name = check[0]['game_name']
            mature = check[0]['is_mature']
            title = check[0]['title']
            views = check[0]['viewer_count']
            started_at = check[0]['started_at']
            print(user_name, "currently playing ", game_name, " with ", views, " viewers", " Is Mature Rated?: ", mature)

            ### Check how long they have been live

            my_date = datetime.utcnow()   #using UTC time to match twitch ?  Apparently Z on end of it means
            #print(my_date)
            current_stamp = (my_date.strftime('%Y-%m-%d %H:%M:%S'))  # sets same time stamp format as Twitch.


            #### ALL THIS IS CHECKING FOLLOWED AT TIME AND THEN FORMATTING  ####
            followed_at = started_at #shows the follow timestamp for that follower
            followed_date = (followed_at.split('T')[0])   # this is splitting from T and returning the Date
            match = re.search('T(.*)Z',followed_at) # this is searching for whats between between T and Z 
            followed_time = (match.group(1)) # This is displaying the match found between T and Z
            followed_at_formatted = followed_date + " " +followed_time  ## this is the formatted time needed to make the following command work.

            ##### Finding The Difference Between the Two Dates #################
            start = datetime.strptime(current_stamp, '%Y-%m-%d %H:%M:%S')
            ends = datetime.strptime(followed_at_formatted, '%Y-%m-%d %H:%M:%S')
            diff = relativedelta(start, ends)

            live_time = f"{diff.hours}h {diff.minutes}m {diff.seconds}s"

            TPClient.stateUpdateMany([
                    {
                        "id": f'gitago.twitchextras.state.raidcheck_{x}.user_name',
                        "value": str(user_name)
                    },
                    {
                        "id": f'gitago.twitchextras.state.raidcheck_{x}.game_name',
                        "value": str(game_name)
                    },
                    {
                        "id": f'gitago.twitchextras.state.raidcheck_{x}.mature',
                        "value": str(mature)
                    },
                    {
                        "id": f'gitago.twitchextras.state.raidcheck_{x}.title',
                        "value": str(title)
                    },
                    {
                        "id": f'gitago.twitchextras.state.raidcheck_{x}.views',
                        "value": str(views)
                    },
                    {
                        "id": f'gitago.twitchextras.state.raidcheck_{x}.livetime',
                        "value": str(live_time)
                    }
                    
                    ])
        else:
            print(channel, " is currently offline")
            if channels_online ==0: 
                TPClient.stateUpdate('gitago.twitchextras.state.raidcheck_1.user_name', "-> 0 <- Online ")
                TPClient.stateUpdate('gitago.twitchextras.state.raidcheck_1.title', "ALL STREAMS ARE OFFLINE")    










