# Home-Assistant Habitica Integration

Home Assistant:
Open-source home automation platform running on Python 3.
http://home-assistant.io/

Habitica:
Habitica is a free habit building and productivity app that treats your real life like a game.
https://habitica.com

This component will enable you to track the following attributes in Home Assistant:
* Name
* Level
* Class
* Gold
* EXP
* Next Level EXP
* HP
* max HP
* Mana
* max Mana



What you can do with it?
----------------------
* You can react on status changes using Hass.
* Your Hass instance could trigger changes using the REST component (not realted to this integration).
* You can plot your data for example using Grafana out of the box:


Installation
-----------

Copy the `habitica.py` file to your configuration path like so:

```
<config_dir>/custom_components/sensor/habitica.py
```

Usage
-----

You need your UserID and your API key which you can find on the Habitica.com website

```yaml
- platform: habitica
  api_user: <your_api_user_id>
  api_key: <your_api_key>
```

Thats it! :)
