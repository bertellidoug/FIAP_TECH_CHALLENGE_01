from fastapi import FastAPI
from api.booksV1 import router as books_router
from api.auth import router as auth_router

app = FastAPI(
    title="Book API",
    description="API de consulta da books.toscrape",
    version="1.0.0"
)

#   register roots
app.include_router(books_router, prefix="/api/v1", tags=["Books"])
app.include_router(auth_router, tags=["Autenticação"])

#   optional root endpoint
@app.get("/", include_in_schema=False)
def root():
    return {"message": "Api de livros sendo executado"}