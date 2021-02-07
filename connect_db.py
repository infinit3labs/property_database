import pyodbc
import config


def get_db_connection():
    server = config.DB_HOST
    database = config.DB_DATABASE
    username = config.DB_UNAME
    password = config.DB_PWD
    cnxn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER='+server+';'
        'DATABASE='+database+';'
        'UID='+username+';'
        'PWD='+password)
    return cnxn


