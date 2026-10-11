import email
import email.utils
from email.header import decode_header, make_header
import html
import imaplib
import logging
import os
import re
import urllib.request
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import ABSENDER, CONF_SERVER, DOMAIN, EVENT_NEU, MAX_BRIEFE, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)
MONATE = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# Formulierungen, in denen die Deutsche Post den Absender nennt
_MUSTER_FLIESSTEXT = [
    re.compile(r"Brief von\s+(.+?)\s+(?:ist|wird|kommt|wurde)\b", re.I),
    re.compile(r"Sendung von\s+(.+?)\s+(?:ist|wird|kommt|wurde)\b", re.I),
]
_MUSTER_ZEILE = re.compile(r"^\s*Absender\s*:\s*(.+?)\s*$", re.I | re.M)


def _text_aus_html(quelle: str, mit_zeilen: bool) -> str:
    if mit_zeilen:
        quelle = re.sub(r"<\s*(br|/p|/div|/td|/tr|/li|/h\d)[^>]*>", "\n", quelle, flags=re.I)
    text = html.unescape(re.sub(r"<[^>]+>", " ", quelle)).replace("\xa0", " ")
    if mit_zeilen:
        return "\n".join(re.sub(r"[ \t]+", " ", z).strip() for z in text.splitlines())
    return re.sub(r"\s+", " ", text)


def _bereinigen(name: str) -> str:
    name = name.strip(" .,:;\"'„“”‚‘’*_")
    return name if 1 < len(name) <= 120 else ""


def _absender_finden(msg, html_text: str, plain_text: str) -> str:
    try:
        betreff = str(make_header(decode_header(msg.get("Subject", ""))))
    except Exception:
        betreff = msg.get("Subject", "") or ""
    quellen = [q for q in (html_text, plain_text) if q]
    for quelle in quellen:
        fliesstext = _text_aus_html(quelle, mit_zeilen=False)
        for muster in _MUSTER_FLIESSTEXT:
            treffer = muster.search(fliesstext)
            if treffer and (name := _bereinigen(treffer.group(1))):
                return name
        treffer = _MUSTER_ZEILE.search(_text_aus_html(quelle, mit_zeilen=True))
        if treffer and (name := _bereinigen(treffer.group(1))):
            return name
    for muster in _MUSTER_FLIESSTEXT:
        treffer = muster.search(betreff)
        if treffer and (name := _bereinigen(treffer.group(1))):
            return name
    vorschau = _text_aus_html(quellen[0], mit_zeilen=False)[:400] if quellen else ""
    _LOGGER.info(
        "Kein Absender erkannt (Betreff: %s). Textanfang: %s", betreff, vorschau
    )
    return "Unbekannt"


class BriefCoordinator(DataUpdateCoordinator[list[dict]]):

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass, _LOGGER, name=DOMAIN,
            update_interval=SCAN_INTERVAL, config_entry=entry,
        )
        self.entry = entry
        self.store = Store(hass, 1, f"{DOMAIN}_{entry.entry_id}")
        self.bild_ordner = hass.config.path("www", "briefe")
        self.gesehen: list[str] = []
        self.briefe: list[dict] = []
        self._erster_lauf = True

    async def async_load(self) -> None:
        daten = await self.store.async_load()
        if daten:
            self.gesehen = daten.get("gesehen", [])
            self.briefe = daten.get("briefe", [])
            self._erster_lauf = False

    async def _async_update_data(self) -> list[dict]:
        try:
            neue_uids, neue_briefe = await self.hass.async_add_executor_job(self._abrufen)
        except imaplib.IMAP4.error as err:
            raise UpdateFailed(f"IMAP-Anmeldung fehlgeschlagen: {err}") from err
        except OSError as err:
            raise UpdateFailed(f"Verbindung fehlgeschlagen: {err}") from err

        self.gesehen = (self.gesehen + neue_uids)[-300:]
        if neue_briefe:
            self.briefe.extend(neue_briefe)
            await self.hass.async_add_executor_job(self._alte_entfernen)
            if not self._erster_lauf:
                for brief in neue_briefe:
                    self.hass.bus.async_fire(EVENT_NEU, {**brief, "konto": self.entry.title})
        self._erster_lauf = False
        await self.store.async_save({"gesehen": self.gesehen, "briefe": self.briefe})
        return list(self.briefe)

    def _abrufen(self) -> tuple[list[str], list[dict]]:
        daten = self.entry.data
        neue_uids, neue_briefe = [], []
        imap = imaplib.IMAP4_SSL(daten[CONF_SERVER], 993, timeout=30)
        try:
            imap.login(daten[CONF_USERNAME], daten[CONF_PASSWORD])
            imap.select("INBOX", readonly=True)
            d = dt_util.now() - timedelta(days=7)
            seit = f"{d.day:02d}-{MONATE[d.month - 1]}-{d.year}"
            _, ergebnis = imap.uid("search", None, f'(FROM "{ABSENDER}" SINCE {seit})')
            for uid in ergebnis[0].split():
                uid_s = uid.decode()
                if uid_s in self.gesehen:
                    continue
                _, msgdata = imap.uid("fetch", uid, "(BODY.PEEK[])")
                msg = email.message_from_bytes(msgdata[0][1])
                neue_briefe.append(self._verarbeite(msg, uid_s))
                neue_uids.append(uid_s)
        finally:
            try:
                imap.logout()
            except Exception:
                pass
        return neue_uids, neue_briefe

    def _verarbeite(self, msg, uid: str) -> dict:
        html_text, plain_text, bilder = "", "", []
        for teil in msg.walk():
            typ = teil.get_content_type()
            inhalt = teil.get_payload(decode=True)
            if not inhalt:
                continue
            zeichensatz = teil.get_content_charset() or "utf-8"
            if typ == "text/html":
                html_text = inhalt.decode(zeichensatz, errors="replace")
            elif typ == "text/plain":
                plain_text = inhalt.decode(zeichensatz, errors="replace")
            elif typ.startswith("image/"):
                bilder.append(inhalt)

        absender = _absender_finden(msg, html_text, plain_text)

        if not bilder and html_text:
            for url in re.findall(r'<img[^>]+src="(https?://[^"]+)"', html_text, re.I)[:5]:
                try:
                    with urllib.request.urlopen(html.unescape(url), timeout=15) as r:
                        bilder.append(r.read())
                except Exception as err:
                    _LOGGER.warning("Bild-Download fehlgeschlagen: %s", err)

        datei, bild = None, None
        if bilder:
            os.makedirs(self.bild_ordner, exist_ok=True)
            konto = re.sub(r"[^a-z0-9]", "_", self.entry.title.split("@")[0].lower())
            datei = f"brief_{konto}_{uid}.jpg"
            pfad = os.path.join(self.bild_ordner, datei)
            with open(pfad, "wb") as f:
                f.write(max(bilder, key=len))
            bild = f"/local/briefe/{datei}"

        try:
            datum = dt_util.as_local(email.utils.parsedate_to_datetime(msg["Date"]))
        except Exception:
            datum = dt_util.now()

        return {
            "absender": absender,
            "datum": datum.strftime("%d.%m.%Y %H:%M"),
            "bild": bild,
            "datei": datei,
        }

    def _alte_entfernen(self) -> None:
        while len(self.briefe) > MAX_BRIEFE:
            alt = self.briefe.pop(0)
            if alt.get("datei"):
                pfad = os.path.join(self.bild_ordner, alt["datei"])
                if os.path.exists(pfad):
                    os.remove(pfad)
