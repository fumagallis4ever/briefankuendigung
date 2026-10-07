# Briefankündigung (WEB.DE / GMX) für Home Assistant

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

[![Öffne dein Home Assistant und füge dieses Repository in HACS hinzu.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=fumagallis4ever&repository=briefankuendigung&category=integration)

[![Öffne dein Home Assistant und starte die Einrichtung der Integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=briefankuendigung)

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

Diese Entitäten legt die Integration bei der Einrichtung **automatisch** an, du musst nichts selbst erstellen:

| Entität | Beschreibung |
|---|---|
| `sensor.briefankundigung_letzter_brief` | Absender des zuletzt angekündigten Briefs. Attribute: `datum`, `bild`, `anzahl`, `briefe` (Liste der letzten 10) |
| `image.briefankundigung_umschlag` | Umschlagbild des letzten Briefs |

Richtest du mehrere Postfächer ein, bekommen die weiteren Entitäten die Endung `_2`, `_3` usw. Die genauen Namen findest du unter *Einstellungen → Geräte & Dienste → Briefankündigung → Entitäten*.

Die Umschlagbilder werden zusätzlich unter `/local/briefe/` gespeichert, damit sie z. B. in Push-Nachrichten verwendet werden können.

### Optional: Hilfssensor „Brief angekündigt“

Soll eine Dashboard-Karte nur erscheinen, wenn heute oder gestern ein Brief angekündigt wurde, brauchst du zusätzlich einen Template-Hilfssensor. Den musst du **selbst anlegen**:

*Einstellu
