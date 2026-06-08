import flet as ft
import mysql.connector

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='joacoagon2009',
            database='academia',
            ssl_disabled=True
        )
        if connection.is_connected():
            print('Conexión exitosa')
            
            return connection
    except Exception as ex:
        print('Conexión errónea')
        print(ex)
        return None
    

a = connect_to_db()
if a:
    cursor = a.cursor()
else:
    print('No se creó cursor porque la conexión a la base de datos falló.')
