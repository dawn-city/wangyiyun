from flask import Flask 
from flask_mysqldb import MySQL


class Config:
    SECRET_KEY = 'secret'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'mysql36'
    MYSQL_DB = 'wyy_web'
    MYSQL_CURSORCLASS = 'DictCursor'



app=Flask(__name__)
app.config.from_object(Config)
mysql = MySQL(app)


from app.views import *