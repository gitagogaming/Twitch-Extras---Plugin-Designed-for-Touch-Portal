#### Only thing being utilized currently is Level Points in "config"

class full_config:
    config = {
        "Main":{
            "Current Token":"",
            "Refresh Token":"",
            "Broadcaster ID":"",
            "Broadcaster Username":""
        },
        "Chatbot":{
            "Chatbot Token": "txt04f8feq5g5im74l1wishs1j6t6c",
            "Chatbot Name": "Gitago_Tests",
        }, 
        "Level Points":{
            "Chat Message Points": "1.0",
            "Follow Age Points": "10.0",
            "Sub Months Points": "70.0",
            "Gifted Sub Points": "200.50",
            "Bit Points": "10.2",
            "Points Needed Per Level": "1000",
            "Max Level": "999",
    }}






    ### This Empty Dict is Filled with data when plugin starts.
    Gift_Subs = {}
    all_subscribers = {}


    ### This Empty Dict is Filled with data when people chat
    live_msg_count = {
        "Chatters MSG Count":{}
        }

    ## Function used to give total amount of chatters + combined message count.
    def calculate():
        values = full_config.live_msg_count['Chatters MSG Count'].values()
        total_messages = sum(values)
        total_chatters = (len(full_config.live_msg_count['Chatters MSG Count']))
        
        message_count_dict = {
            "Total Chatters": total_chatters,
            "Total Messages": total_messages 
        }
        return message_count_dict
    
class dictionary_tracker:
    mod_loop_count = 0
    get_gifters_loop_count = 0
#print(full_config.config['Chatbot']['Chatbot Name'])



