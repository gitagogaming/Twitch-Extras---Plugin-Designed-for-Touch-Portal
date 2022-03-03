############ CHATBOT 2.0
#### https://twitchtokengenerator.com/

from t_imports import *

##  from asyncio.windows_events import NULL
##  from os import name
##  from twitchio.ext import commands
##  
##  from user_database import *    
from twitch_api import *
##  import twitchio
##  from twitchio.ext import pubsub
##  from twitchio.ext.pubsub.models import PubSubChannelPointsMessage



### added these back in after moving things above to t_imports
import twitchio
from twitchio.ext import pubsub
from twitchio.ext.pubsub.models import PubSubChannelPointsMessage
print("CHATBOT IMPORTED???")


CHATBOT_NAME = full_config.config['Chatbot']['Chatbot Name']
ACCESS_TOKEN = full_config.config['Chatbot']['Chatbot Token']
CLIENT_SECRET = "gp762nuuoqcoxypju8c569th9wz7q5"  ### Not needed for Chatbot yet 

##   message.author.   - is_mod   or just _mod  -  is_turbo   -  is_subscriber   -  prediction   -   colour  -  display_name   -  badges  -  name - id
   
class TwitchChatBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=ACCESS_TOKEN,
            client_secret=CLIENT_SECRET,
            nick=CHATBOT_NAME,
            prefix="!",
            initial_channels=["CDNThe3rd"],
        )
        
        #self.pubsub_client=None
    #  client = twitchio.Client(token=ACCESS_TOKEN, client_secret=CLIENT_SECRET)
    #  client.pubsub = pubsub.PubSubPool(client)
    print("did we go in ?")
    async def event_ready(self):
        print(f"Ready | {self.nick}")
        
       # await self.pubsub_client.connect()    
        
    def the_log (logdata):
        save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras')
        a_file = open(save_path +"\log_data_chatbot2.txt", "a")
        a_file.write(str(logdata)+ "\n")
        a_file.close()

    async def event_message(self, message):
        """
        author.is_mod
        author.name
        author.display_name
        author.colour
        author.badges
        author.is_subscriber
        author.is_turbo
        author.prediction
        author.mention
        
        """
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return
        
        
      #  print(f"\n[MSG][{message.channel}] {message.author.display_name}: {message.content}")
        ## Checking Database for User..
        cur.execute(f'SELECT * FROM user_db WHERE id= {message.author.id}') 
        check_exists = (cur.fetchone())

        # if user does not exist, Submit data to DB via get_user_info which does an api pull on userinfo..
        if not check_exists:
            get_user_info(message.author.id, "user-id")
            print('Adding User to Database:', message.author.display_name)

        if check_exists:
            ### Incrementing Messages + Entering Into Database
            self.update_database_info(check_exists, message)

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)



    ### From Event_Raw_Data, We are extracting roomstate upon loading so we can set proper states inside of touchportal for followers only etc.
    async def event_raw_data(self, raw_data: str):
        
        
        if "first-msg=1" in raw_data:
            splitdata = raw_data.split(";")
            parsed_dict = {}
            for x in splitdata:
                parsed_dict[x.split("=")[0]] = x.split("=")[-1]
            print("[FIRST MESSAGE] ---- ", parsed_dict['display-name'], "---", parsed_dict['first-msg'])
        
        
        if "ROOMSTATE" in raw_data and "USERSTATE" in raw_data:
            preparselist = list(filter(None, raw_data.split("@")))
            parsed = self.roomstate_parse(preparselist[-1])
            print("\n[ROOM STATE]",parsed)
        
        
        elif "ROOMSTATE" in raw_data:
            parsed = self.roomstate_parse(raw_data)
            print("\n[ROOM STATE2]", parsed)
        
        
        elif "PRIVMSG" in raw_data:
            pass
        
        
        elif "USERNOTICE" in raw_data:
            parsed = self.user_notice_parse(raw_data)
            
            # If the notice is for subscriber
            if parsed['msg-id'] == "sub":
                if parsed['msg-param-was-gifted'] == "true":
                    print(f"[GIFTED SUB] {parsed['display-name']} was gifted")
                    print(f"Param Months:{parsed['msg-param-months']}   Cumulative Months:{parsed['msg-param-cumulative-months']}   Sub Plan: {parsed['msg-param-sub-plan']}  Tenure: {parsed['msg-param-multimonth-tenure']}")

                elif parsed['msg-param-was-gifted'] == "false":
                    print(f"{parsed['display-name']} user just subscribed")
                    print(f"Param Months:{parsed['msg-param-months']}   Cumulative Months:{parsed['msg-param-cumulative-months']}   Sub Plan: {parsed['msg-param-sub-plan']}  Tenure: {parsed['msg-param-multimonth-tenure']}")
                
            elif parsed['msg-id'] == "resub":                                   ## cumulative months is total months subscribed, not concurrent
                streak = parsed.get('msg-param-streak-months')
                if streak:
                    print(f"[RE-SUB / STREAK] {parsed['display-name']} They have subscribed for {parsed['msg-param-cumulative-months']} months currently on {parsed['msg-param-streak-months']} month streak")
                if not streak:
                     print(f"[RE-SUB] {parsed['display-name']} They have subscribed for {parsed['msg-param-cumulative-months']} months")
                     
            else:
                print("[FULL USER NOTICE]", parsed)
            
            
            
        elif "JOIN" in raw_data:
            parsed_join = raw_data.split("@")[0].split("!")[0].replace(":","")
            print("[JOIN]", parsed_join)
        else:
            print("\n[RAW]", raw_data)



    def roomstate_parse(self, raw_data: str):
        print(raw_data)
        try:
            preparse = raw_data.replace(":tmi.twitch.tv", ";").replace(" ", "").replace("#", "=")
            return dict(x.split("=") for x in preparse.strip("\r\n@").split(";"))
        except ValueError as err:
            print("ROOMSTATE ERROR:", raw_data)


    def user_notice_parse(self, raw_data: str):
        try:
       #     print("User notice parse?????", raw_data)
            preparse = raw_data.replace(":tmi.twitch.tv", ";").replace(" ", "").replace("#", "=").replace("color==", "color=")
            nextparse = dict(x.split("=") for x in preparse.strip("\r\n@").split(";"))
            print('[USER NOTICE PARSE]')
            
            
 
          #  TwitchChatBot.the_log("\n----------> Parse Failed")
          #  TwitchChatBot.the_log(raw_data)
                
            TwitchChatBot.the_log("\n------- > Clean Dictionary User Notice: ")
            TwitchChatBot.the_log(nextparse)
            return nextparse
        except err:
            TwitchChatBot.the_log("--------> THE ERROR:", err)
            TwitchChatBot.the_log(f"\nThe Raw Data\n {raw_data}\n")




    @classmethod
    def send_message(self):  
        pass


    async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
        print(event)
        print(event.status)
        print(event.timestamp)
        print(event.reward)
        print(pubsub.PubSubChannelPointsMessage)


    
    ### If chatter is not in database then this is called.
    def update_database_info(self, check_exists, message):
        subscriber_status = 0
        premium_status = 0
        vip_status = False
        sub_badge_month = 0
        badges = {} ## dont thin kthis is needed.
        
        ### Calculating Live Message Count  #### moved this from the end
        self.livechatter_count(message) ### adding + 1 to message count no matter what..


        #####  Pull user data from database, then replace with New  ################
        ## Checking for VIP Badge and splitting subscriber badge gcrap....
        if check_exists:
            if message.author.badges != None:
                if "subscriber" in message.author.badges:
                    subscriber_status = 1
                    sub_badge_month = message.author.badges['subscriber']
                    #print("Total Months=",sub_badge_month)
                    save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras\images\badges\subscriber_badges\\')
                    badge_image_path = save_path + sub_badge_month+".png"

                if "premium" in message.author.badges:
                    premium_status = 1
                    #print("[PREMIUM]", message.author.display_name)

                if "vip" in message.author.badges:
                    save_path = path.expandvars(r'%APPDATA%\TouchPortal\plugins\TwitchExtras\lists')
                    vip_status = True
                    vip_users_file = open(save_path+"\VIP_Chat_List.txt", "r")        


                    flag = 0  # setting flag and index to 0
                    index = 0                    

                    for line in vip_users_file:  
                        index + 1      
                        if message.author.display_name in line:        
                            flag = 1
                            break 
                    vip_users_file.close()    

                    # checking condition for string found or not
                    if flag == 0: 
                        print('VIP', message.author.display_name , 'Not Found')
                        with open(save_path + "\VIP_Chat_List.txt", "a") as f:  ## Open and Append
                            f.write(message.author.display_name+ "\n")    
                        f.close()               
                        ## now lets add to active list since TP is already running..
                        add_vip_list(message.author.display_name)   
                    else: 
                        print('VIP', message.author.display_name, 'Found In Line', index)

            ## Pulling users Total Messages and Incrementing..
            total_messages = int(check_exists[11])
            if total_messages == None:
                total_messages = 0 
            if total_messages >= 0:
                a_dict = {}
                id = check_exists[0]
            #  broadcaster_type = check_exists[1]
                display_name = message.author.display_name
                login = check_exists[3]
            #  description = check_exists[4]
            #  offline_image_url = check_exists[5]
            #  profile_image_url = check_exists[6]
            #  type = check_exists[7]
            #  view_count = check_exists[8]   ### get this updated..
            #  created_at = check_exists[9]
                follow_months = check_exists[10]
            #  #total_messages = int(check_exists[11])  ## we pull this info FIRST.. not needed here
            #  months_subscribed = sub_badge_month
            #  ###months_subscribed = check_exists[12]
                total_bits = check_exists[13]  ## total bits is only updated when requested
            #  level = check_exists[14]   ## level is only updated when level card is called for. 

                if total_bits == "null":
                    total_bits = 0
                if follow_months == "null":
                        follow_months = 0
                        
                #### Increment the Message Count  ####
                total_messages = total_messages + 1

                # Converting Badges to string to save into DB..
                badges = json.dumps(message.author.badges)
                if not badges:
                    badges = ""
            
                months_subscribed = sub_badge_month
                gifted_subs = None
                if display_name in full_config.Gift_Subs:
                    gifted_subs = full_config.Gift_Subs.get(display_name)
                    print(f"{display_name} has {gifted_subs} gifted subs")
                if gifted_subs:
                    print(gifted_subs)
                    gifted_sub_score = float(gifted_subs) * Points_Per_Gifted_Sub
                    print(gifted_sub_score)
                elif not gifted_subs:
                    gifted_subs = 0
                    gifted_sub_score = 0
                
                ### updating the CHATTERS dict with the chatters name and total messages.. now we can track total messages sent pers perosn..
                for variable in ["display_name", "id", "login", "total_messages", "months_subscribed", "badges"]:
                    a_dict[variable] = eval(variable)
                enter_user_dict(a_dict)

                TPClient.stateUpdate("gitago.twitchextras.state.chatmsgcount", total_messages)
                print ("[LIFETIME MSG COUNT]", display_name, total_messages) 

  
    def livechatter_count(self, message):
        import plug_config
        """ Keeping Track of Persons Message Count """
        
        ########## ACTIVE CHATTERS LIST ##############
        ##### Making a Full List of Chatters, maybe count total messages per stream like in other plugin?
        username = message.author.display_name


        if username in full_config.live_msg_count['Chatters MSG Count']:
            # Adding + 1 To users Total Live Chat Messages
            full_config.live_msg_count['Chatters MSG Count'][username] = full_config.live_msg_count['Chatters MSG Count'][username] + 1


        elif message.author.display_name not in full_config.live_msg_count['Chatters MSG Count']:
            #Adding Chatter to MSG Dict 
            full_config.live_msg_count['Chatters MSG Count'][username] = 1

        ### Instead of incrementing Total Chatters, and Total messages, we could just count the Dictionary length and total instead...
        print("Chatters:", full_config.calculate()['Total Chatters'], "Total Messages:", full_config.calculate()['Total Messages'])

import asyncio

def main():
    thebot = TwitchChatBot()
    client = twitchio.Client(token=ACCESS_TOKEN, client_secret=CLIENT_SECRET)
    thebot.pubsub_client = client
       # client.pubsub = pubsub.PubSubPool(client)
    thebot.run()
    
main()


#asyncio.run(main())
#if __name__ == '__main__':
#t1 = threading.Thread(target=main)
#t1.run()

print("ITS BLOCKING???")



#### https://discord.com/channels/490948346773635102/491048464831086592/812003463726366722

####        CUSTOM_COMMANDS = {"test1":"testing1", "test2":"testing2"} #Create example commands instead of going off asking a database
####        # Create a function inside of the bot that will be used 
####        class myBot(commands.Bot):
####          ...
####          async def sendCustomCommand(self, ctx):
####            await ctx.send(CUSTOM_COMMANDS[ctx.command.name])
####          
####          async def event_ready(self):
####            for commandName in CUSTOM_COMMANDS.keys():
####              self.add_command(commands.Command(name=commandName, func=self.sendCustomCommand))


