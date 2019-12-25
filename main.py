import requests
import re
import json
from bs4 import BeautifulSoup as bsoup
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from cal_setup import get_calendar_service

url = "http://www.cm-porto.pt/editais/c/assembleia-municipal"
page = requests.get(url)
idcal = "po9mags4q7olbkc8mmg79dd8h4"

sopa = bsoup(page.content, 'html.parser')
mydivs = sopa.findAll("div", {"class": "object 87"})
print(len(mydivs))

entradas = []

numero = 0
for n in mydivs:
    if str(n).find("Convocatória") != -1:
        
        nomet = str(n.findAll(None,{"class": "name"})[0])
        nome = nomet[nomet.find(">")+1:nomet.find("<",nomet.find(">"))]

        texto = n.findAll(None,{"class": "body"})[0]
        textonorm = str(texto).strip().replace("\n"," ").replace("\r"," ").replace("\t", " ").replace('"',"«")

        datapub = str(n.findAll(None,{"class": "date"})[0])
        datapub = datapub[datapub.find(">")+1:datapub.find("<",datapub.find(">"))]

        regex = "(\d{1,2}).{0,4}(janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro).{0,4}(\d{4})"

        dataeve = re.findall(regex,nome)
        try:
            dataeve = dataeve[0][2]+"-"+dataeve[0][1].replace("dezembro","12").replace("novembro","11").replace("outubro","10").replace("setembro","09").replace("agosto","08").replace("julho","07").replace("junho","06").replace("maio","05").replace("abril","04").replace("março","03").replace("fevereiro","02").replace("janeiro","01")+"-"+str("{:02d}".format(int(dataeve[0][0])))
            print(dataeve)
        except Exception as e:
            print(e)
            dataeve = "erro"

        print("Título: " +nome)
        print("Publicado em " + datapub)
        print(textonorm)
        print(texto.findAll(">"))
        print("\n|"*10)

        entrada = {
            "titulo":nome,
            "datap": datapub,
            "datae": dataeve,
            "present": False,
            "texto": textonorm
        }

        entradas.append(entrada)
        numero +=1

print("Foram descobertos "+str(numero)+" eventos relevantes")

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(entradas, f, default=str, indent=4, sort_keys=True)

#with open("sopa.html", "w") as file:
#    file.write(str(sopa.body.prettify()))
#
#with open("teste.txt", "w") as file:
#    file.write(str(mydivs))