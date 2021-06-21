# DiscordScraper

## Installation
* Install latest [python](https://www.python.org/downloads/)
* Install pip packages:
`pip install discum`
`pip install flask`

## Configuration
* Create a new file called `config.json` in the same folder
* Copy the contents of `config.example.json` into `config.json`
* Fill in the required information in the JSON config file:
`token`: Discord API token, instructions to get it  @ https://discordhelp.net/discord-token.
`target`: Target user or bot that you're gonna copy messages of. This must be the ID of the user/bot.
`from`: Array of channel IDs that you'll be copying from.
`to`: Array of channels IDs that you'll be copying to.
`httpApi`: Determine whether you want to spawn a ReST HTTP API or not.
`port`: Port that the HTTP API server will be listening to.
`host`: IP that you want the HTTP API server to bind to.
`limit`: Maximum number of messages that is allowed to be saved by the API.

Only `token`, `target`, `from` are mandatory.

## Running the Bot
* After you're done configuring the above, run the bot using:
`python Main.py`
* Your bot will not automatically copy any messages from the channels you selected, post them to the channels you want and expose them on the HTTP API.

## HTTP API
`/`
* This is the base index page. It will show "<> Discord Scraper <>".

`/feed?limit=10`
* This is the main feed GET API. There's an optional `limit` argument that the user can supply so that the feed only returns messages upto that number. Otherwise, the server will return all data upto the default message limit (100).

* By default, the latest messages are inserted at the **beginning** of the array.

If the channel you're copying from has:
Message1
Message2
Message3

The data returned from the feed will have an array of [Message3, Message2, Message1]. More on the data format below.

## Data Format
The HTTP API data format is:
```json
{ "data":[
{"id": "<ID>", content: "<CONTENT>" },
{"id": "<ID>", content: "<CONTENT>" },
...
] }
```