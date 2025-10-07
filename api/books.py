from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from scraping import scrapeBooks
import pandas as pd
import os

router = APIRouter()


#   load the latest csv file from \DATA folder
CSV_PATH = scrapeBooks.getLatestCSV()


#   read CSV
def loadData():

    if not os.path.exists(os.path.exists(CSV_PATH)):
        raise FileNotFoundError(f"Arquivo não encontrado. {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)
    df["id"] = df.index + 1
    df["category"] = df["NumPage"].apply(lambda p: f"Categoria {p}")

    return df

df = loadData()

#----------------------------
#   routes
@router.get("/books", summary="Lista de todos os livros")
def getBooks():
    return df.to_dict(orient="records")

#----------------------------
@router.get("/books/{bookID}", summary="Detalhes de um livro específico")
def getBook(bookID: int):

    book = df[df["id"] == bookID]
    if book.empty:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    return book.to_dict(orient="records")[0]

#----------------------------
@router.get("/books/search", summary="Busca livros por título e/ou categoria")
def searchBooks(title: str = Query(None, description="Título parcial ou completo"),
                 category: str = Query(None, description="Categoria do livro")):
    
    """Busca livros filtrando por título e/ou categoria."""
    results = df.copy()

    if title:
        results = results[results["Title"].str.contains(title, case=False, na=False)]

    if category:
        results = results[results["category"].str.contains(category, case=False, na=False)]

    if results.empty:
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado")
    
    return results.to_dict(orient="records")

#----------------------------
@router.get("/categories", summary="Lista todas as categorias")
def getCategories():

    """Retorna todas as categorias únicas da base."""
    categories = sorted(df["category"].unique().tolist())
    return {"categories": categories}

#----------------------------
@router.get("/health", summary="Verifica status da API")
def healthCheck():

    """Verifica se a API está funcionando e acessando os dados."""
    return JSONResponse(content={
        "status": "ok",
        "records": len(df),
        "csv_path": CSV_PATH
    })