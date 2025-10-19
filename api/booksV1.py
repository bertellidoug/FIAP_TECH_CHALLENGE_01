import threading
import time
from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import jwt, JWTError
from scraping import scrapeBooks
from .auth import getCurrentUser
import pandas as pd
import os
import secrets

router = APIRouter()

#   load the latest csv file from \DATA folder
CSV_PATH = scrapeBooks.getLatestCSV()
print(CSV_PATH)

#   read CSV
def loadData():

    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Arquivo não encontrado. {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)
    df["id"] = df.index + 1
    df["category"] = df["NumPage"].apply(lambda p: f"Categoria {p}")

    return df

df = loadData()
print(len(df))

#----------------------------
#   routes

@router.get("/books", summary="Lista de todos os livros")
def getBooks():

    """Get all books from the database"""
    return df.to_dict(orient="records")

#----------------------------
@router.get("/books/search", summary="Busca livros por título e/ou categoria")
def searchBooks(title: str = Query(None, description="Título parcial ou completo"),
                 category: str = Query(None, description="Categoria do livro")):
    
    """Get books filtered by title and/or category"""
    results = df.copy()

    if title:
        results = results[results["Title"].str.contains(title, case=False, na=False)]

    if category:
        results = results[results["Category"].str.contains(category, case=False, na=False)]

    if results.empty:
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado")
    
    return results.to_dict(orient="records")

#----------------------------
@router.get("/books/{bookID}", summary="Detalhes de um livro específico")
def getBook(bookID: int):

    """Get a specific book by ID"""
    book = df[df["id"] == bookID]
    if book.empty:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    return book.to_dict(orient="records")[0]

#----------------------------
@router.get("/categories", summary="Lista todas as categorias")
def getCategories():

    """Return all unique categories from the database"""
    categories = sorted(df["Category"].unique().tolist())
    return {"categories": categories}

#----------------------------
@router.get("/health", summary="Verifica status da API")
def healthCheck():

    """Check if the API is working and can access the data"""
    return JSONResponse(content={

        "status": "ok",
        "records": len(df),
        "csv_path": CSV_PATH
    })

@router.post("/scraping/trigger", summary="Dispara scraping (protegido)", status_code=status.HTTP_202_ACCEPTED)
def triggerScraping(user: str = Depends(getCurrentUser)):
    
    if scraping_status["running"]:
        return {"message": f"Scraping já em execução pelo {user}"}

    """Authenticated async execution to load the database via web scraping"""
    thread = threading.Thread(target=scrapingTask)
    thread.start()

    return {"message": f"Scraping iniciado pelo {user}. Favor aguardar alguns minutos"}

def scrapingTask():

    try:
        scraping_status["running"] = True
        scraping_status["success"] = None

        #time.sleep(3) -> we shoud use this, when we want to run tests.

        # call the real scraping
        scrapeBooks.runScraping()

        scraping_status["success"] = True

    except Exception as e:

        scraping_status["success"] = False
        print("Erro no scraping:", e)
    finally:
        scraping_status["running"] = False

@router.get("/scraping/status", summary="Status do scraping")
def scrapingStatus():

    if scraping_status["running"]:
        return {"status": "em processamento"}
    
    if scraping_status["success"] is True:
        return {"status": "finalizado com sucesso"}
    
    if scraping_status["success"] is False:
        return {"status": "erro no scraping"}
    
    return {"status": "parado"}


scraping_status = {
    "running": False,
    "success": None  # True, False = error, None = not started
}