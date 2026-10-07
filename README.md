# Briefankündigung (WEB.DE / GMX) für Home Assistant

[![Öffne dein Home Assistant und füge dieses Repository in HACS hinzu.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=fumagallis4ever&repository=briefankuendigung&category=integration)

[![Öffne dein Home Assistant und starte die Einrichtung der Integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=briefankuendigung)

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz)
[![Validate](https://github.com/fumagallis4ever/briefankuendigung/actions/workflows/validate.yml/badge.svg)](https://github.com/fumagallis4ever/briefankuendigung/actions/workflows/validate.yml)

Holt die **Briefankündigung der Deutschen Post** aus deinem WEB.DE- oder GMX-Postfach und zeigt in Home Assistant an, welche Briefe unterwegs sind – mit Absender, Datum und Umschlagbild.

*English summary below.*

## Funktionen

- Einrichtung komplett über die Oberfläche, kein YAML nötig
- Mehrere Postfächer möglich (z. B. für jedes Familienmitglied eins)
- Sensor mit dem Absender des letzten Briefs und einer Liste der letzten 10 Ankündigungen
- Bild-Entität mit dem Umschlagbild für Dashboards
- Event `briefankuendigung_neu` für eigene Automationen, z. B. Push-Nachrichten
- Postfach wird nur gelesen, Mails werden nicht als gelesen markiert oder gelöscht

## Voraussetzungen

1. Ein Postfach bei **WEB.DE** oder **GMX** mit aktivierter [Briefankündigung](https://web.de/email/briefankuendigung/).
2. **IMAP-Zugriff** im Postfach erlaubt: *Einstellungen → POP3/IMAP-Abruf → POP3- und IMAP-Zugriff erlauben*.
3. Bei aktiver Zwei-Faktor-Authentifizierung ein **anwendungsspezifisches Passwort** (*Mein Account → Sicherheit*).
4. Home Assistant **2026.3** oder neuer.

## Installation

### Über HACS

1. HACS → **⋮** → **Benutzerdefinierte Repositories**
2. URL `https://github.com/fumagallis4ever/briefankuendigung`, Typ **Integration**
3. „Briefankündigung“ suchen, installieren und Home Assistant neu starten

### Manuell

Den Ordner `custom_components/briefankuendigung` in den Ordner `config/custom_components/` deiner Home-Assistant-Installation kopieren und neu starten.

## Einrichtung

*Einstellungen → Geräte & Dienste → Integration hinzufügen → **Briefankündigung***

| Feld | Wert |
|---|---|
| IMAP-Server | `imap.web.de` (WEB.DE) oder `imap.gmx.net` (GMX) |
| E-Mail-Adresse | vollständige Adresse, z. B. `name@web.de` |
| Passwort | Postfach-Passwort oder anwendungsspezifisches Passwort |

Für weitere Postfächer die Integration einfach noch einmal hinzufügen.

## Entitäten

| Entität | Beschreibung |
|---|---|
| `sensor.briefankundigung_letzter_brief` | Absender des zuletzt angekündigten Briefs. Attribute: `datum`, `bild`, `anzahl`, `briefe` (Liste der letzten 10) |
| `image.briefankundigung_umschlag` | Umschlagbild des letzten Briefs |

Weitere Postfächer erhalten die Endung `_2`, `_3` usw.

Die Umschlagbilder werden zusätzlich unter `/local/briefe/` gespeichert, damit sie z. B. in Push-Nachrichten verwendet werden können.

## Event

Bei jeder neuen Ankündigung wird das Event `briefankuendigung_neu` ausgelöst:

| Feld | Beispiel |
|---|---|
| `absender` | `Stadtwerke Musterstadt` |
| `datum` | `07.10.2026 01:05` |
| `bild` | `/local/briefe/brief_name_1234.jpg` |
| `konto` | `name@web.de` |

Beim allerersten Abruf werden die Ankündigungen der letzten 7 Tage übernommen, ohne Events auszulösen.

### Beispiel: Push-Nachricht mit Umschlagbild

```yaml
alias: Briefankündigung – Push-Nachricht
triggers:
  - trigger: event
    event_type: briefankuendigung_neu
actions:
  - action: notify.mobile_app_dein_handy
    data:
      title: "📬 Brief unterwegs"
      message: "Von {{ trigger.event.data.absender }} – kommt in den nächsten Tagen."
      data:
        image: "{{ trigger.event.data.bild }}"
mode: queued
```

Nur für ein bestimmtes Postfach: im Trigger `event_data: {konto: name@web.de}` ergänzen.

### Beispiel: Dashboard-Karte

```yaml
type: markdown
content: |-
  {%- set briefe = state_attr('sensor.briefankundigung_letzter_brief', 'briefe') or [] -%}
  <table width="100%">
  <tr><th align="left" width="30%">Eingang</th><th align="left">Absender</th></tr>
  {%- for b in briefe %}
  <tr><td>{{ (b.datum or '').split(' ')[0] }}</td><td>{{ b.absender }}</td></tr>
  {%- endfor %}
  </table>
```

## Hinweise

- Abfrageintervall: alle 5 Minuten.
- Steht der Absender nicht im Text der Ankündigung, zeigt der Sensor „Unbekannt“. Er ist dann meist auf dem Umschlagbild zu sehen.
- Dieses Projekt steht in keiner Verbindung zur Deutschen Post, zu WEB.DE oder GMX.

---

## English summary

Home Assistant integration that reads the *Briefankündigung* (letter announcement) service of Deutsche Post from a WEB.DE or GMX mailbox via IMAP. It provides a sensor with the sender of the latest announced letter (plus the last 10 as attributes), an image entity with the envelope scan, and fires a `briefankuendigung_neu` event for each new announcement. Setup is done in the UI; multiple mailboxes are supported. Only available in Germany.

## Lizenz

MIT
