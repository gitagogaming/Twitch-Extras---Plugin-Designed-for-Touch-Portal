
import TouchPortalAPI as TP
import sys

# imports below are optional, to provide argument parsing and logging functionality
from argparse import ArgumentParser
from logging import (getLogger, Formatter, NullHandler, FileHandler, StreamHandler, DEBUG, INFO, WARNING)

print("TP Client Imported")
PLUGIN_ID = "gitago.twitchextras"
__version__ = "1.0"

TP_PLUGIN_INFO = {
    'sdk': 3,
    'version': int(float(__version__) * 100),  # TP only recognizes integer version numbers
    'name': "TE | Twitch Extras",
    'id': PLUGIN_ID,
    'configuration': {
        'colorDark': "#25274c",
        'colorLight': "#707ab5"
    }
}


try:
    TPClient = TP.Client(
        pluginId = PLUGIN_ID,  # required ID of this plugin
        sleepPeriod = 0.05,    # allow more time than default for other processes
        autoClose = True,      # automatically disconnect when TP sends "closePlugin" message
        checkPluginId = True,  # validate destination of messages sent to this plugin
        maxWorkers = 4,        # run up to 4 event handler threads
        updateStatesOnBroadcast = False,  # do not spam TP with state updates on every page change
    )
except Exception as e:
    sys.exit(f"Could not create TP Client, exiting. Error was:\n{repr(e)}")
