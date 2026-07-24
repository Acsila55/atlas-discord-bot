# Atlas Discord Bot

**Atlas** is a multi-purpose Discord bot I built for me and my friends.

Feel free to use this repo or fork it and change it to your liking, but I don't handle pull requests because this is just a fun side project for me.


## The Tech Stack

*   **Language:** Python 3.12
*   **Framework:** `discord.py` utilizing a modular "Cogs" structure.
*   **APIs:** Riot Games API (for live LoL data).
*   **Deployment:** Fully containerized with Docker for seamless updates.

## Features & Commands

Atlas comes with a variety of commands and background utilities. Here is everything it can do:

###  Admin Tools
*   `/shutdown` - Safely disconnects and shuts down the bot.
*   `/reload_module <module>` - Hot-reloads a specific module without restarting the bot.
*   `/change_status <status> <activity_type> <activity_text>` - Dynamically changes the bot's online status (e.g., Online, Do Not Disturb) and activity text (e.g., "Playing Just Gooning").
*   `/clear_messages <n>` - Bulk deletes a specified number of recent messages in the channel.

###  League of Legends
*   `/random_champion` - Provides a random League of Legends champion along with their icon.
*   `/link_account <username> <tag>` - Links your League of Legends account to your Discord profile.
*   `/admin_link_account <member> <username> <tag>` - *(Admin only)* Links a specific user's Discord profile to a League of Legends account. (Used for linking accounts for others)
*   `/my_account` - Displays your linked League of Legends account, including ranks (Solo/Duo, Flex), level, and top champion masteries.
*   `/get_account <member>` - Displays the linked League of Legends account for a specified Discord user.
*   **Server Leaderboard:** Creates a leaderboard of the registered accounts and displays their ranks in order. Automatically updates player profiles and a server leaderboard every 5 minutes.

### General Commands
*   `/edge <member> <n>` - *(Requires Move Members permission)* Repeatedly moves a user between public voice channels `n` times.

###  Background Tasks & Logging
*   **Command Logging:** Operates quietly in the background, logging all executed slash commands (who used it, what command, and where) to a designated admin channel.
*   **Error Handling:** Catches and logs bot errors to a designated error channel to keep chat clean.


## Bot Architecture (The Cogs)

To keep the codebase clean and maintainable, Atlas uses the `discord.py` Cogs extension to separate functionality into distinct files:

*   **`cogs/base.py`:** Acts as the foundational template that all other cogs inherit from. It manages standardized error handling and provides built-in utility functions for loading and saving JSON files universally across the bot.
*   **`cogs/lol.py`:** Powered by `modules/lol_module/`, this handles all the League of Legends commands, interacts with the Riot API, and manages the background leaderboard updater.
*   **`cogs/admin.py`:** Houses all the server management and bot control logic.
*   **`cogs/general.py`:** Contains fun, miscellaneous commands.
*   **`cogs/logging.py`:** An event listener module that strictly tracks interactions and sends formatted embed logs to the logging channel.


## How to host it yourself

If you want to run the bot on your server, here is how to run it:

### Get your API Keys / Discord Token
You will need a few things before starting:
*   [Discord Bot Token](https://discord.com/developers/home) (You have to give the bot all Intents)
*   [Riot Games API Key](https://developer.riotgames.com)

### Make the environment variables
Create a `.env` file in the root directory and add your keys exactly like this:

```env
DISCORD_TOKEN=your_discord_token_here
RIOT_API_KEY=your_riot_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### Run the bot
You can run the bot locally or use the built Docker Image.

**Terminal (Local):**
```bash
pip install -r requirements.txt
python main.py
```

**Docker:**
```bash
docker build -t atlas-bot .
docker run -d --name atlas-bot --env-file .env -v ./data:/app/data atlas-bot
```

---

## TODO:

### Gemini
    ask gemini

### LOL:
*    live game checker
*    history checker
*    champ counters
*    champ build
*    champ runes

### COMPLEX
* media player
* soundboard palayer

