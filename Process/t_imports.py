from tpclient import *




### CHATBOT

from asyncio.windows_events import NULL
from os import name
from twitchio.ext import commands

from user_database import *    
#from twitch_api import *





#------------------------------------------#
#----------- TWITCH_API IMPORTS -----------#
#------------------------------------------#

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


from PIL import Image
from requests.models import HTTPError
import urllib.request 

#------------------------------------------#
#--------- END TWITCH_API IMPORTS ---------#
#------------------------------------------#




#------------------------------------------#
#-------------- NOTHING.PY  ---------------#
#------------------------------------------#
import sys
from websockets.legacy.client import *
from websockets.extensions import *
from websockets.legacy import *

import create_preditions
##  from user_database import *


#------------------------------------------#
#------------ END NOTHING.PY  -------------#
#------------------------------------------#