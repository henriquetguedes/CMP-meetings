from addcal import *
import requests
import re
import json
from pushbullet import Pushbullet
from bs4 import BeautifulSoup as bsoup
from datetime import datetime, timedelta
from pathlib import Path

with open(Path().resolve().parent / 'credenciais'/ 'pushbullet.json', 'r') as myfile:
    data=json.load(myfile)
api_key = data["pbtoken"]
pb = Pushbullet(api_key)

with open("output.json", "r", encoding="utf-8") as lista:
    entradas = json.load(lista)
listaexist = [d['idext'] for d in entradas]
#entradas = []
url = "http://www.cm-porto.pt/editais/c/assembleia-municipal"
page = requests.get(url)

sopa = bsoup(page.content, 'html.parser')
mydivs = sopa.findAll("div", {"class": "object 87"})
mydivs.reverse()
print("Encontrados %s anúncios, a comparar com um registo prévio de %s entradas" %(len(mydivs), len(entradas)))

numero = len(entradas)
adicionados = 0
for n in mydivs:
    if str(n).find("Convocatória") != -1:
        #ID unico do anuncio
        regex = 'class="info readspeakerInfo(\d*?)"'
        for m in re.findall(regex,str(n.findAll(None,{"class": "detalhe"})[0])):
            idext = m
        #verifica se ja esta na lista
        if idext in listaexist:
            pass
        else:
            numero +=1
            #nome do anuncio
            nomet = str(n.findAll(None,{"class": "name"})[0])
            nome = nomet[nomet.find(">")+1:nomet.find("<",nomet.find(">"))]
            #texto do anuncio
            regex = "(<.*?>)"
            texto = n.findAll(None,{"class": "body"})[0]
            textonorm = str(texto).strip().replace("\n"," ").replace("\r"," ").replace("\t", " ").replace('"',"«")
            finds = re.findall(regex,textonorm)
            for f in finds:
                textonorm = textonorm.replace(f,"").strip()
            #data de publicação
            datapub = str(n.findAll(None,{"class": "date"})[0])
            datapub = datapub[datapub.find(">")+1:datapub.find("<",datapub.find(">"))]
            datapub = datapub[6:10]+datapub[2:6]+datapub[:2]
            #data do evento
            regex = "(\d{1,2}).{0,4}(janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro).{0,4}(\d{4})"
            dataeve = re.findall(regex,nome)
            try:
                dataeve = dataeve[0][2]+"-"+dataeve[0][1].replace("dezembro","12").replace("novembro","11").replace("outubro","10").replace("setembro","09").replace("agosto","08").replace("julho","07").replace("junho","06").replace("maio","05").replace("abril","04").replace("março","03").replace("fevereiro","02").replace("janeiro","01")+"-"+str("{:02d}".format(int(dataeve[0][0])))
                if (datetime.strptime(dataeve,"%Y-%m-%d")-datetime.strptime(datapub,"%Y-%m-%d")).days < 1:
                    print("EVENTO NO MESMO DIA OU JÁ PASSADO \nPublicado a : %s\nPrevisto para: %s" %(datapub,dataeve))
            except Exception as e:
                print(e)
                dataeve = "erro"
            #anexos ao anuncio
            anexos = []
            regex = 'href="(.*?)" target="_blank">(.*?)<'
            for fic in re.findall(regex,str(n.findAll(None,{"class": "files"})[0])):
                anexos.append([fic[0],fic[1]])

            entrada = {
                "id_n": numero,
                "idext": idext,
                "titulo": "CMPorto " + nome,
                "datap": datapub,
                "datae": dataeve,
                "present": False,
                "texto": textonorm,
                "anexos": anexos,
                "link": ""
            }
            #elimina da lista de eventos a adicionar os que derem erro de data <-- ver mais tarde
            if dataeve == "erro":
                print("AQUI")
                entrada['present'] = True
            entradas.append(entrada)
            adicionados +=1

print("Foram descobertos %s eventos relevantes, adicionados %s novos" %(numero,adicionados))

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(entradas, f, default=str, indent=4, sort_keys=True,ensure_ascii=False)

eventados = 0
email = []

for eve in range(len(entradas)):
    if entradas[eve]['present'] == False:
        try:
            strteste = "<strong>Descrição:</strong><br>"+entradas[eve]['texto']
            if len(entradas[eve]['anexos'])>0:
                strteste = strteste+"<br><br><strong>Documentos:</strong><ul>"
                for an in range(len(entradas[eve]['anexos'])):
                    strteste = strteste+'<li><a href="'+entradas[eve]['anexos'][an][0]+'">'+entradas[eve]['anexos'][an][1]+'</a></li>'
                strteste = strteste+"</ul>"
            strteste = strteste + "<em><br>PROCESSADO POR COMPUTADOR<br>ID único: %s<br>ID evento: %s" %(entradas[eve]['idext'],entradas[eve]['id_n'])+'</em>'
            aaadicio = {
                "nome": entradas[eve]['titulo'],
                "desc": strteste,
                "dataini": entradas[eve]['datae']
            }
            link = adiciona(**aaadicio)

            entradas[eve]['link'] = link
            entradas[eve]['present'] = True
            email.append([entradas[eve]['titulo'],entradas[eve]['datae'],link])
            #push = pb.push_list("Adicionados", [entradas[eve]['titulo'],entradas[eve]['datae'],link])
            eventados +=1
        except Exception as e:
                print(e)

print("Foram adicionados %s novos eventos ao calendário" %(eventados))

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(entradas, f, default=str, indent=4, sort_keys=True,ensure_ascii=False)

if len(email) > 0:
    corpo = "Em " + str("hoje") + " foram adicionados<br><ul>"
    mensagem = "Adicionados hoje:"
    for i in range(len(email)):
        corpo = corpo + '<li><a href="'+ email[i][2] + '"> '+email[i][0]+'</a> - nm o dia '+email[i][1]+'</li>'
        mensagem = mensagem + "\n\n-Data: "+email[i][1]+"\n---"+email[i][0]+"\n---"+ email[i][2]
    corpo = corpo + "</ul>"
    #print(corpo) ### é para ser mandar o email aqui
    pb.push_note("Adicionados",mensagem)
