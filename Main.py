import discum
import json
import re
import threading
from flask import Flask, request


CONFIG_PATH = './config.json'
TOKEN_FIELD = 'token'
TARGET_USER = 'target'
FROM_CHANS = 'from'
TO_CHANS = 'to'
HOST = 'host'
PORT = 'port'
MSG_LIMIT = 'messageLimit'
HTTP_API = 'httpApi'

config = {}
with open(CONFIG_PATH) as f:
    config = json.load(f)

for field in [TOKEN_FIELD, FROM_CHANS, TARGET_USER]:
    if field not in config:
        raise RuntimeError(
            f"Field {field} must be declared in the config.json file!")

token = config[TOKEN_FIELD]
targetUser = config[TARGET_USER]
fromChans = config[FROM_CHANS]
toChans = config.get(TO_CHANS, [])
host = config.get(HOST, '0.0.0.0')
port = config.get(PORT, '3000')
msgLimit = config.get(MSG_LIMIT, 100)
httpApi = config.get(HTTP_API, False)

bot = discum.Client(
    token=token, log=True)

global data
data = []


def sendToChans(msg):
    for chan in toChans:
        bot.sendMessage(chan, msg)


def addToRestApi(id, msg):
    global data
    data.insert(0, {'id': id, 'content': msg})
    while len(data) > msgLimit:
        data.pop(msgLimit)


def getAllContent(msg):
    content = msg['content']
    embeds = msg['embeds']
    lines = []
    if content:
        content = re.sub(r"<.+?>", "", content)
        lines += [content]
    for embed in embeds:
        if 'title' in embed:
            lines += [embed['title']]
        if 'url' in embed:
            lines += [embed['url']]
        if 'fields' in embed:
            for field in embed['fields']:
                fieldValues = []
                if 'name' in field and field['name'] != 'undefined':
                    fieldValues += [field['name']]
                if 'value' in field and field['value'] != 'undefined':
                    fieldValues += [field['value']]
                if fieldValues:
                    fieldString = ' - '.join(fieldValues)
                    lines += [f"{fieldString}"]

    return "\n".join(lines)


@bot.gateway.command
def proxyMessages(resp):
    if resp.event.ready_supplemental:  # ready_supplemental is sent after ready
        user = bot.gateway.session.user
        print("Logged in as {}#{}".format(
            user['username'], user['discriminator']))
    if resp.event.message:
        msg = resp.parsed.auto()
        channelID = msg['channel_id']
        guildID = msg['guild_id'] if 'guild_id' in msg else None
        username = msg['author']['username']
        userId = msg['author']['id']
        discriminator = msg['author']['discriminator']
        allContent = getAllContent(msg)
        if userId == targetUser and allContent and channelID in fromChans:
            sendToChans(allContent)
            addToRestApi(msg.get('id', -1), allContent)
        print("> guild {} channel {} | {}#{}: {}".format(
            guildID, channelID, username, discriminator, allContent))


botThread = threading.Thread(target=bot.gateway.run, kwargs={
                             'auto_reconnect': True})

botThread.start()

if httpApi:
    app = Flask(__name__)

    @app.route("/")
    def root():
        return '<> Discord Scraper <>'

    @app.route("/feed")
    def feed():
        userLimit = int(request.args.get('limit', msgLimit))
        actualLimit = min(msgLimit, userLimit)
        return json.dumps({"data": data[:actualLimit]})
    apiThread = threading.Thread(target=app.run, kwargs={
        'host': host, 'port': port}, daemon=True)

    apiThread.start()

botThread.join()
