import logging
from typing import Union, Annotated
import uvicorn
from fastapi import FastAPI, Header, Request, Body, Depends
from fastapi.responses import JSONResponse
from backend.Game.Game import Game
from backend.Utility import LOGGING_CONFIG, CustomException
from backend.Auth import JWTBearer, UserSchema, AuthDatabase
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="GenGame")
# Change CORS handling for prod!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
AuthDB = AuthDatabase()
API = Game()


def run_app():
    uvicorn.run(app, log_level="critical", log_config=LOGGING_CONFIG)


@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    headers = getattr(exc, "headers", None)
    if not headers:
        headers = {"Access-Control-Allow-Origin": "*"}
    if isinstance(exc, CustomException):
        logging.error(f"Custom exception found in: {request.url}: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"message": str(exc)},
            headers=headers
        )
    logging.exception(f"exception found in: {request.url}:")
    return JSONResponse(
        status_code=500,
        content={"message": "The server encountered an error while processing the request."},
        headers=headers
    )


@app.post("/login/", tags=["user"])
async def login(user: UserSchema = Body(...)):
    return AuthDB.authenticate_user(user)


@app.post("/register/", tags=["user"])
async def create_user(user: UserSchema = Body(...)):
    return AuthDB.register_user(user)


@app.get('/startup/')
def startup():
    return API.system_startup()


@app.get('/saves_list/', dependencies=[Depends(JWTBearer())])
def saves(authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.get_saves_list(username)


@app.get('/themes/')
def themes():
    return API.get_available_themes()


@app.get('/load/', dependencies=[Depends(JWTBearer())])
def load(save_name: str, images: Annotated[str | None, Header()], authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.load_save(username, save_name, images == "True")


@app.post('/new_save/', dependencies=[Depends(JWTBearer())])
def new_save(theme: str, body: dict, images: Annotated[str | None, Header()], authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.new_save(username, theme, body['background'], images == "True")


@app.get('/delete/', dependencies=[Depends(JWTBearer())])
def delete(save_name: str, authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.delete_save(username, save_name)


@app.get('/advance/', dependencies=[Depends(JWTBearer())])
def advance(action: str, save_name: str, images: Annotated[str | None, Header()], authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.advance_story(username, save_name, action, images == "True")


@app.get('/new_option/', dependencies=[Depends(JWTBearer())])
def new_option(new_action: str, save_name: str, authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.create_new_option(username, save_name, new_action)


@app.get('/spend/', dependencies=[Depends(JWTBearer())])
def spend(skill: str, save_name: str, authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.spend_action_point(username, save_name, skill)


@app.get('/shop/', dependencies=[Depends(JWTBearer())])
def shop(save_name: str, images: Annotated[str | None, Header()], authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.get_shop(username, save_name, images == "True")


@app.get('/buy/', dependencies=[Depends(JWTBearer())])
def buy(item_name: str, save_name: str, authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.buy_item(username, save_name, item_name)


@app.get('/sell/', dependencies=[Depends(JWTBearer())])
def sell(item_name: str, save_name: str, authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.sell_item(username, save_name, item_name)


@app.get('/image/', dependencies=[Depends(JWTBearer())])
def image(save_name: str, category: str, authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.get_image(username, save_name, category)

