from datetime import timedelta

DOMAIN = "briefankuendigung"
CONF_SERVER = "server"
DEFAULT_SERVER = "imap.web.de"
ABSENDER = "ankuendigung@brief.deutschepost.de"
EVENT_NEU = "briefankuendigung_neu"
MAX_BRIEFE = 50
CONF_AUFBEWAHRUNG = "aufbewahrung_tage"
DEFAULT_AUFBEWAHRUNG = 14
DATUM_FORMAT = "%d.%m.%Y %H:%M"
SCAN_INTERVAL = timedelta(minutes=5)
