import mysql.connector

# conexion con la base de datos
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345678",
        database="softs_contrasenias"
    )
