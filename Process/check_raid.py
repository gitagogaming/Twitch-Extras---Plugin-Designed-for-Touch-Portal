#from twitchAPI.types import AutoModAction
#from twitch_api import *
#from tpclient import*

from pprint import pprint

adict = {'poll': {'choices': [{'choice_id': '0e4c8ac4-ecfd-40da-87cb-aa91fe4fa73b',
                       'title': 'Poll Choice 1',
                       'tokens': {'bits': 0, 'channel_points': 0},
                       'total_voters': 0,
                       'votes': {'base': 0,
                                 'bits': 0,
                                 'channel_points': 0,
                                 'total': 0}},
                      {'choice_id': 'd44519c5-e5c0-4533-b7d9-474b8911425a',
                       'title': 'Poll Choice 2',
                       'tokens': {'bits': 0, 'channel_points': 0},
                       'total_voters': 0,
                       'votes': {'base': 0,
                                 'bits': 0,
                                 'channel_points': 0,
                                 'total': 0}},
                      {'choice_id': 'd45d7475-c8fc-49fb-a0fb-a9e32e9de6b7',
                       'title': 'Poll Choice 3',
                       'tokens': {'bits': 0, 'channel_points': 0},
                       'total_voters': 1,
                       'votes': {'base': 1,
                                 'bits': 0,
                                 'channel_points': 0,
                                 'total': 1}},
                      {'choice_id': 'ad5e6181-bf09-413c-a205-94bc84645a4e',
                       'title': 'Poll Choice 4',
                       'tokens': {'bits': 0, 'channel_points': 0},
                       'total_voters': 0,
                       'votes': {'base': 0,
                                 'bits': 0,
                                 'channel_points': 0,
                                 'total': 0}},
                      {'choice_id': 'e596e032-9c14-434f-ae12-473a80c3bcee',
                       'title': 'Poll Choice 5',
                       'tokens': {'bits': 0, 'channel_points': 0},
                       'total_voters': 0,
                       'votes': {'base': 0,
                                 'bits': 0,
                                 'channel_points': 0,
                                 'total': 0}}],
          'created_by': '197028355',
          'duration_seconds': 30,
          'ended_at': None,
          'ended_by': None,
          'owned_by': '197028355',
          'poll_id': 'ed287070-070c-4b41-9a2a-483d05ae2869',
          'remaining_duration_milliseconds': 15496,
          'settings': {'bits_votes': {'cost': 0, 'is_enabled': False},
                       'channel_points_votes': {'cost': 25, 'is_enabled': True},
                       'multi_choice': {'is_enabled': True},
                       'subscriber_multiplier': {'is_enabled': False},
                       'subscriber_only': {'is_enabled': False}},
          'started_at': '2021-10-14T18:42:15.552071166Z',
          'status': 'ACTIVE',
          'title': 'Title',
          'tokens': {'bits': 0, 'channel_points': 0},
          'top_bits_contributor': None,
          'top_channel_points_contributor': None,
          'top_contributor': None,
          'total_voters': 1,
          'votes': {'base': 1, 'bits': 0, 'channel_points': 0, 'total': 1}}}




#pprint(adict['poll']['choices'])



x = 0
for poll_choice in adict['poll']['choices']:
    #pprint(poll_choice)
    x = x +1
    print("")
    print(f"{x} Choice Selection")
    for item in poll_choice:
        print("Key: ", item, " Value: ", poll_choice[item])



###    
###    from pprint import pprint
###    
###    
###    
###    raid_list = []
###    
###    
###    save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras\lists')
###    raid_list_file = open(save_path +"\Raid_Chat_List.txt", "r")
###    with raid_list_file as f:
###        lines = f.readlines()
###        raid_list = []
###        for line in lines:
###            stripped_line = line.rstrip()
###            raid_list.append(stripped_line)
###        f.close()
###    
###    print(raid_list)
###    
###    def check_raid_list():
###        x = 0
###        for channel in raid_list:
###            thedeets = twitch.get_streams(user_login=channel)
###            check = (thedeets['data'])
###            #pprint(check)
###            if check:
###                x = x + 1
###                ### If check, then they are online so lets create + update states.
###                user_name = check[0]['user_name']
###                game_name = check[0]['game_name']
###                mature = check[0]['is_mature']
###                title = check[0]['title']
###                views = check[0]['viewer_count']
###                print(user_name, "currently playing ", game_name, " with ", views, " viewers", " Is Mature Rated?: ", mature)
###    
###                TPClient.stateUpdateMany([
###                        {
###                            "id": 'gitago.twitchextras.state.raidcheck_{x}.user_name',
###                            "value": ""
###                        },
###                        {
###                            "id": 'gitago.twitchextras.state.raidcheck_{x}.game_name',
###                            "value": ""
###                        },
###                        {
###                            "id": 'gitago.twitchextras.state.raidcheck_{x}.mature',
###                            "value": ""
###                        },
###                        {
###                            "id": 'gitago.twitchextras.state.raidcheck_{x}.title',
###                            "value": ""
###                        },
###                        {
###                            "id": 'gitago.twitchextras.state.raidcheck_{x}.views',
###                            "value": ""
###                        },
###                        {
###                            "id": 'gitago.twitchextras.state.raidcheck_{x}.title',
###                            "value": ""
###                        },
###                        ])
###            else:
###                print(channel, " is currently offline")
###    
###    
###    #check_raid_list()
###    loop = 16
###    for num in range(loop):
###        print(num)
###    
###    
###    from dateutil.relativedelta import relativedelta
###    from datetime import datetime
###    
###    my_date = datetime.utcnow()   #using UTC time to match twitch ?  Apparently Z on end of it means
###    #print(my_date)
###    current_stamp = (my_date.strftime('%Y-%m-%d %H:%M:%S'))  # sets same time stamp format as Twitch.
###    
###    
###    
###    
###    #### ALL THIS IS CHECKING FOLLOWED AT TIME AND THEN FORMATTING  ####
###    followed_at = "2021-10-13T19:34:16Z" #shows the follow timestamp for that follower
###    followed_date = (followed_at.split('T')[0])   # this is splitting from T and returning the Date
###    match = re.search('T(.*)Z',followed_at) # this is searching for whats between between T and Z 
###    followed_time = (match.group(1)) # This is displaying the match found between T and Z
###    followed_at_formatted = followed_date + " " +followed_time  ## this is the formatted time needed to make the following command work.
###    
###    ##### Finding The Difference Between the Two Dates #################
###    start = datetime.strptime(current_stamp, '%Y-%m-%d %H:%M:%S')
###    ends = datetime.strptime(followed_at_formatted, '%Y-%m-%d %H:%M:%S')
###    diff = relativedelta(start, ends)
###    
###    print(f'Live for {diff.hours}h {diff.minutes}m {diff.seconds}s')
###    
###    
###    live_time = f"Live for {diff.hours}h {diff.minutes}m {diff.seconds}s"
###    print(live_time)
###    
###    
###    from pprint import pprint
###    
###    
###    adict = [{'content_classification': {'category': 'swearing', 'level': 2},
###      'message': {'content': {'fragments': [{'automod': {'topics': {'vulgar': 6}},
###                                             'text': 'fucking'},
###                                            {'text': ' eh'}],
###                              'text': 'fucking eh'},
###                  'id': '33739186-624e-4761-9ee8-1c2720502129',
###                  'sender': {'display_name': 'Gitago_Tests',
###                             'login': 'gitago_tests',
###                             'user_id': '698211221'},
###                  'sent_at': '2021-10-14T02:40:10.532555479Z'},
###      'reason_code': '',
###      'resolver_id': '',
###      'resolver_login': '',
###      'status': 'PENDING'},
###     {'content_classification': {'category': 'swearing', 'level': 4},
###      'message': {'content': {'fragments': [{'text': 'is this a '},
###                                            {'automod': {'topics': {'vulgar': 3}},
###                                             'text': 'shitty'},
###                                            {'text': ' dict ?'}],
###                              'text': 'is this a shitty dict ?'},
###                  'id': '837c8d15-a4fd-47e4-813e-d240715b069f',
###                  'sender': {'display_name': 'Gitago_Tests',
###                             'login': 'gitago_tests',
###                             'user_id': '698211221'},
###                  'sent_at': '2021-10-14T02:40:30.042433823Z'},
###      'reason_code': '',
###      'resolver_id': '',
###      'resolver_login': '',
###      'status': 'PENDING'},
###     {'content_classification': {'category': 'swearing', 'level': 2},
###      'message': {'content': {'fragments': [{'text': 'lets create a bigger '},
###                                            {'automod': {'topics': {'vulgar': 6}},
###                                             'text': 'fucking'},
###                                            {'text': ' dictionary to work thru'}],
###                              'text': 'lets create a bigger fucking dictionary to '
###                                      'work thru'},
###                  'id': '67a6da7b-e59e-48d2-8b39-1a29043e86eb',
###                  'sender': {'display_name': 'Gitago_Tests',
###                             'login': 'gitago_tests',
###                             'user_id': '698211221'},
###                  'sent_at': '2021-10-14T02:40:42.268950068Z'},
###      'reason_code': '',
###      'resolver_id': '',
###      'resolver_login': '',
###      'status': 'PENDING'}]
###    
###    
###    
###    # Python3 code to demonstrate 
###    # to delete dictionary in list
###    # using del + loop 
###      
###    # initializing list of dictionaries
###    test_list = [{"id" : 1, "data" : "HappY"},
###                 {"id" : 2, "data" : "BirthDaY"},
###                 {"id" : 3, "data" : "Rash"}]
###      
###    
###    
###    
###    
###    
###    automod_query_length = len(adict)
###    current_case_num = 0

## 
## ef get_new_case():
##    countbad = 0
##    countgood = 0
##    ### setting everything up from the dict
##    current_case_id = (adict[current_case_num]['message']['id'])
##    case_level = (adict[current_case_num]['content_classification']['level'])
##    case_category = (adict[current_case_num]['content_classification']['category'])
##    current_case_offender =(adict[current_case_num]['message']['sender']['display_name'])
##    
##    current_case_words = (adict[current_case_num]['message']['content']['fragments'])
##    current_case_full_message = (adict[current_case_num]['message']['content']['text'])
## 
##    if len(adict) > 0:
##        print ("Current Case Count: ", automod_query_length)
##        for word in current_case_words:
##            #print(word)
##            if "automod" in word:
##                #countbad = countbad + 1
##                #print(f"AUTOMOD WORD: {word['text']}")
##                automod_word = word['text']
##            else:
##                #countgood = countgood + 1
##                good_words = (f"Word #{countgood}, {word['text']}")
##                #print(good_words)
##                pass
##    print(f"Case ID: {current_case_id} \nOffender: {current_case_offender}\nOffending Word/Words: {automod_word}")
##    TPClient.stateUpdate("gitago.twitchextras.state.automod.case_offender", str(current_case_offender))
##    TPClient.stateUpdate("gitago.twitchextras.state.automod.case_id", str(current_case_id))
##    TPClient.stateUpdate("gitago.twitchextras.state.automod.case_word", str(automod_word))
##    TPClient.stateUpdate("gitago.twitchextras.state.automod.case_count", str(automod_query_length))
##    #print(f"There are {automod_query_length} automod cases in line.")
## 
## 
## et_new_case()
## 
##   case1 = automod_case(case_level,case_category)
## 
## ef confirm_case(case_id, decision):
##    if decision == "allow":
##        twitch.manage_held_automod_message(the_broadcaster_id, case_id, action=AutoModAction.ALLOW)
##    elif decision == "deny":
##        twitch.manage_held_automod_message(the_broadcaster_id, case_id, action=AutoModAction.DENY)
## 
##    
##    for i in range(len(adict)):
##        if adict[i]['message']['id'] == "67a6da7b-e59e-48d2-8b39-1a29043e86eb":
##            del adict[i]
##            print("Removed Case from List")
##            #pprint (adict)
##            break
##    ## lets get a new case
##    get_new_case()
## 

#####          
#####          

#####          adict = {'content_classification': {'category': 'swearing', 'level': 2}, 'message': {'content': {'text': 'biggger fucking test ok', 'fragments': [{'text': 'biggger '}, {'text': 'fucking', 'automod': {'topics': {'vulgar': 6}}}, {'text': ' test ok'}]}, 'id': '5c11370a-a6c9-4531-87d3-675170a64b28', 'sender': {'user_id': '698211221', 'login': 'gitago_tests', 'display_name': 'Gitago_Tests'}, 'sent_at': '2021-10-14T06:33:29.824891595Z'}, 'reason_code': '', 'resolver_id': '', 'resolver_login': '', 'status': 'PENDING'}#####          

#####          alist = []#####          

#####          current_case_id = (adict['message']['id'])#####          

#####          case_level = (adict['content_classification']['level'])
#####          case_category = (adict['content_classification']['category'])#####          

#####          current_case_offender =(adict['message']['sender']['display_name'])
#####          current_case_words = (adict['message']['content']['fragments'])
#####          current_case_full_message = (adict['message']['content']['text'])
#####          #print(adict)#####          

#####          newdict = {
#####              'current_case_id': adict['message']['id'],
#####              'case_level': case_level,
#####              'case_category': case_category,
#####              'case_offender': current_case_offender,
#####              'offending_words': current_case_words,
#####              'full_message': current_case_full_message
#####          }#####          

#####          pprint(newdict)
#####          alist.append(newdict)
#####          print(alist)

###   alist = []
###   #print(adict)
###   adict_copy = adict.copy()
###   alist.append(adict_copy)
###   
###   print(alist)
###   
###   current_case_id = "4f08e348-faca-4932-a6ce-481a193a419c"
###   
###   for i in range(len(alist)):
###     if alist[i]['message']['id'] == current_case_id:
###       print("This is i   ", alist[i])
###       del alist[i]
###       print("Removed Case from List")
###       print("after the removal    ", alist)
###       break


#print(current_case_words)








class automod_case:
    all = []

    def __init__(self, case_level, case_category, offender, content, automod_text, status):
        automod_case.all.append(self)
        pass

    def show_case():
        pass



