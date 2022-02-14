from urllib.parse import quote
import webbrowser
from server import hostName
from server import serverPort


bfile = open("benchmark.txt", mode='r', encoding='utf-8')
for line in bfile:
    if line == "\n":
        continue
    if line.startswith('#'):
        print(line.replace("# ", "").replace("\n", ""))
    else:
        print("Q: " + line)
        query = quote(line).replace("%0A", "");
        while(input("Inserisci 'c' per continuare: ") != 'c'): pass
        webbrowser.open("http://" + hostName + ":" + str(serverPort) + "/search?query=" + query)
        print("------------------------------------------------------")


