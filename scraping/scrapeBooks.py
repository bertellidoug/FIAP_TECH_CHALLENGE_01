import requests
from bs4 import BeautifulSoup
import pandas as pd
import glob, os, time
import csv
from datetime import datetime

def checkCacheFile() -> bool:

    CACHE_MINUTES = 5
    files = glob.glob("./data/books_*.csv")

    if files:
        
        latestFile = max(files, key=os.path.getctime)
        lastModified = os.path.getmtime(latestFile)

        if time.time() - lastModified < CACHE_MINUTES * 60:
            print(f"Usando cache local: {latestFile}")
            return True
        
    return False

def getLatestCSV():
    
    CSV_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CSV_FILE = os.path.join(CSV_DIR, "data")

    csvFile = glob.glob(os.path.join(CSV_DIR, "books_*.csv"))

    if not csvFile:
        raise FileNotFoundError("Nenhum arquivo CSV encontrado na pasta \data")
    
    latestFile = max(csvFile, key=os.path.getctime)
    return latestFile

#   check if CSV exists 
if checkCacheFile():
    exit()

#   create the file name
numPage = 0
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
fileName = f"./data/books_{timestamp}.csv"

print(f"Arquivo criado: {fileName}")

#   initial url of the website
BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

#   list to store the data
obj_data = []

#   number of pages to scrap (has 50 pages)
NUM_PAGES = 50

#   open csv in write mode and add header
with open(fileName, mode="w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow(["NumPage", "Title", "Price", "Stock", "Rating"])

    for page in range(1, NUM_PAGES + 1):

        print(f"Reading page {page}")

        url = BASE_URL.format(page)

        response = requests.get(url)
        response.encoding = "utf-8"

        if response.status_code != 200:
            print(f"Erro ao acessar página {page}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.find_all("article", class_="product_pod")

        for book in books:
            numPage = 0
            title = book.h3.a["title"]
            price = book.find("p", class_="price_color").text.strip()
            stock = book.find("p", class_="instock availability").text.strip()
            rating = book.p["class"][1]

            obj_data.append({
                "NumPage":page,
                "Title": title,
                "Price": price,
                "Stock": stock,
                "Rating": rating
            })

            writer.writerow([page, title, price, stock, rating])

print(f"Script finalizado.")