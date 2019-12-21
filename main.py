import requests
from bs4 import BeautifulSoup as bsoup

url = "http://www.cm-porto.pt/editais/c/assembleia-municipal"
page = requests.get(url)

sopa = bsoup(page.content, 'html.parser')
mydivs = sopa.findAll("div", {"class": "object 87"})
print(len(mydivs))

numero = 0
for n in mydivs:
    if str(n).find("Convocatória") != -1:
        
        nomet = str(n.findAll(None,{"class": "name"})[0])
        nome = nomet[nomet.find(">")+1:nomet.find("<",nomet.find(">"))]

        texto = str(n.findAll(None,{"class": "body"})[0])
        print(nome)
        print(texto)
        print("\n|"*10)

        numero +=1

print(numero)


with open("sopa.html", "w") as file:
    file.write(str(sopa.body.prettify()))


with open("teste.txt", "w") as file:
    file.write(str(mydivs))