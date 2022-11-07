import requests
import json
from pathlib import Path

with open(Path(__file__).resolve().parent.parent / 'credenciais'/ 'telegram.json', 'r') as myfile:
    data=json.load(myfile)
token = data["teletoken"]
chat_id = data["mynot_chatid"]
method = "sendMessage"

def msgTele(msggram, silent: bool = False):
    response = requests.post(url='https://api.telegram.org/bot{0}/{1}'.format(token, method), data={
                             'chat_id': chat_id, 'text': msggram, 'disable_notification': silent})
