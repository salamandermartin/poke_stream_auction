from flask import Flask

from sqlalchemy import create_engine, select
from sqlmodel import SQLModel, Session

from starlette.websockets import WebSocket
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_200_OK
from starlette.websockets import WebSocket, WebSocketDisconnect

from typing import Dict
import datetime

app = Flask(__name__)

@app.route("/")
def auction_client():
    return "<p>Hello</p>"