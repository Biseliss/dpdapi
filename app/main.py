from fastapi import FastAPI
from .database import Base, engine
from .routers import auth, user, recipe, comment, admin, file
from fastapi.middleware.cors import CORSMiddleware

def create_tables():
    Base.metadata.create_all(bind=engine)

app = FastAPI()
app.router.redirect_slashes = False

# TODO подумать над удалением
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_tables()

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(recipe.router, prefix="/recipe", tags=["Recipe"])
app.include_router(comment.router, prefix="/comment", tags=["Comment"])
app.include_router(file.router, prefix="/file", tags=["File"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

@app.get("/")
def root():
    return {"message": "API is working!"}
