import requests
import re
import json
from bs4 import BeautifulSoup as bsoup
from datetime import datetime, timedelta

with open("output.json", "r", encoding="utf-8") as lista:
    entradas = json.load(lista)
listaexist = [d['idext'] for d in entradas]
#entradas = []
url = "http://www.cm-porto.pt/editais/c/assembleia-municipal"
page = requests.get(url)
idcal = "po9mags4q7olbkc8mmg79dd8h4"

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
        #verifica
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
                #print(dataeve)
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
                "titulo":nome,
                "datap": datapub,
                "datae": dataeve,
                "present": False,
                "texto": textonorm,
                "anexos": anexos
            }

            entradas.append(entrada)
            adicionados +=1

print("Foram descobertos %s eventos relevantes, adicionados %s novos" %(numero,adicionados))

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(entradas, f, default=str, indent=4, sort_keys=True,ensure_ascii=False)

#with open("sopa.html", "w") as file:
#    file.write(str(sopa.body.prettify()))
#
#with open("teste.txt", "w") as file:
#    file.write(str(mydivs))