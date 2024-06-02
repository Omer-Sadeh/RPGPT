import logging
from typing import Union, Annotated
import uvicorn
from fastapi import FastAPI, Header, Request, Body, Depends
from fastapi.responses import JSONResponse
from backend.Game.Game import Game
from backend.Utility import LOGGING_CONFIG, CustomException
from backend.Auth import JWTBearer, UserSchema, AuthDatabase


app = FastAPI(title="GenGame")
AuthDB = AuthDatabase()
API = Game()


def run_app():
    uvicorn.run(app, log_level="critical", log_config=LOGGING_CONFIG)


@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, CustomException):
        logging.error(f"Custom exception found in: {request.url}: {str(exc)}")
        return JSONResponse(
            status_code=418,
            content={"message": str(exc)},
        )
    logging.exception(f"exception found in: {request.url}:")
    return JSONResponse(
        status_code=500,
        content={"message": "The server encountered an error while processing the request."},
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


@app.post('/load/', dependencies=[Depends(JWTBearer())])
def load(save_name: str, images: Annotated[str | None, Header()], authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.load_save(username, save_name, images == "True")


@app.post('/fetch/', dependencies=[Depends(JWTBearer())])
def fetch(save_name: str, authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.fetch_save(username, save_name)


@app.post('/new_save/', dependencies=[Depends(JWTBearer())])
def new_save(theme: str, body: dict, authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.new_save(username, theme, body['background'])


@app.post('/delete/', dependencies=[Depends(JWTBearer())])
def delete(save_name: str, authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.delete_save(username, save_name)


@app.post('/goals/', dependencies=[Depends(JWTBearer())])
def goals(save_name: str, regen: bool, authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.get_goals(username, save_name, regen)


@app.post('/new_story', dependencies=[Depends(JWTBearer())])
def new_story(save_name: str, goal: Union[str, None], authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.new_story(username, save_name, goal)


@app.post('/advance/', dependencies=[Depends(JWTBearer())])
def advance(action: str, save_name: str, images: Annotated[str | None, Header()], authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.advance_story(username, save_name, action, images == "True")


@app.post('/new_option/', dependencies=[Depends(JWTBearer())])
def new_option(new_action: str, save_name: str, authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.create_new_option(username, save_name, new_action)


@app.post('/spend/', dependencies=[Depends(JWTBearer())])
def spend(skill: str, save_name: str, authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.spend_action_point(username, save_name, skill)


@app.post('/shop/', dependencies=[Depends(JWTBearer())])
def shop(save_name: str, images: Annotated[str | None, Header()], authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.get_shop(username, save_name, images == "True")


@app.post('/buy/', dependencies=[Depends(JWTBearer())])
def buy(item_name: str, save_name: str, authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.buy_item(username, save_name, item_name)


@app.post('/sell/', dependencies=[Depends(JWTBearer())])
def sell(item_name: str, save_name: str, authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.sell_item(username, save_name, item_name)


@app.post('/end_story/', dependencies=[Depends(JWTBearer())])
def end(save_name: str, images: Annotated[str | None, Header()], authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.end_game(username, save_name, images == "True")


@app.post('/image/', dependencies=[Depends(JWTBearer())])
def image(save_name: str, authorization: str = Header(None)):
    username = AuthDB.decode_token(authorization.split(' ')[1])
    return API.get_image(username, save_name)

