## Sulfate and Paraben Free.

Install [docker](https://docs.docker.com/engine/install/)

1. Clone the repo
   ```
    git clone https://github.com/clodman84/clodbot420.git
   ```
2. Run setup_db.py
   ```
    cd data && python3 setup_db.py
   ```
3. Create a settings.json in clodbot420 with this schema
   ```
   {
      "ERROR_WEBHOOK": link to a discord webhook where all the errors will be sent
      "DEV_GUILD": ID of the dev guild
      "COLOUR": this is the default colour of all embeds, should be an integer representation of the hex
      "DISCORD_TOKEN": _
   }
   ```
5. Move to ./clodbot420 and then docker compose up

The public python execution commands use [snekbox](https://github.com/python-discord/snekbox) for evaluation.
