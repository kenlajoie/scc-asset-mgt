from fastapi import FastAPI, Request, status
from .models import Base
from .database import engine
from .routers import auth, todos, admin, users, assets
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="AssetMgtApp/static"), name="static")


@app.get("/")
def test(request: Request):
    return RedirectResponse(url="/assets/asset-page", status_code=status.HTTP_302_FOUND)


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


app.include_router(auth.router)
app.include_router(assets.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
