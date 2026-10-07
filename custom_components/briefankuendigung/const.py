from datetime import timedelta

DOMAIN = "briefankuendigung"
CONF_SERVER = "server"
DEFAULT_SERVER = "imap.web.de"
ABSENDER = "ankuendigung@brief.deutschepost.de"
EVENT_NEU = "briefankuendigung_neu"
MAX_BRIEFE = 10
SCAN_INTERVAL = timedelta(minutes=5)
