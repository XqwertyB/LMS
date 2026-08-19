import os

from action_logs.events import Events

if os.environ.get('RUN_MAIN', None) != 'true':
    default_app_config = 'action_logs.apps.ActionLogsConfig'

API_LOGGER_SIGNAL = Events()
