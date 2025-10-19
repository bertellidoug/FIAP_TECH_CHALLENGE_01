import requests
from bs4 import BeautifulSoup
import pandas as pd
import glob, os, time
import csv
from urllib.parse import urljoin
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

    csvFile = glob.glob(os.path.join(CSV_FILE, "books_*.csv"))

    if not csvFile:
        raise FileNotFoundError("Nenhum arquivo CSV encontrado na pasta \data")
    
    latestFile = max(csvFile, key=os.path.getctime)
    return latestFile

def runScraping():

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
    BASE_BASE = "https://books.toscrape.com/"
    BASE_CATOLOGUE = "https://books.toscrape.com/catalogue/"

    #   list to store the data
    obj_data = []

    #   number of pages to scrap (has 50 pages)
    NUM_PAGES = 2

    #   open csv in write mode and add header
    with open(fileName, mode="w", newline="", encoding="utf-8-sig") as file:

        writer = csv.writer(file)
        next_id = 1
        writer.writerow(["NumPage", "ID", "Title", "Price", "Rating", "Stock", "Category", "Image"])

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

                bookID = next_id
                title = book.h3.a["title"]
                price = book.find("p", class_="price_color").text.strip()
                rating = book.p["class"][1]
                stock = book.find("p", class_="instock availability").text.strip()

                image_url = book.find("img")["src"].replace("../../", BASE_BASE)
                image = image_url

                href = book.h3.a["href"]  # ex: "../../../a-light-in-the-attic_1000/index.html"
                
                detail_url = urljoin(url, href)  # monta a URL absoluta corretamente
                detail_resp = requests.get(detail_url)
                detail_resp.raise_for_status()
                detail_soup = BeautifulSoup(detail_resp.text, "html.parser")

                category = detail_soup.find("ul", class_="breadcrumb").find_all("a")[2].text.strip()

                writer.writerow([page, bookID, title, price, rating, stock, category, image])
                next_id += 1

    print(f"Script finalizado.")

if __name__ == "__main__":
    runScraping()