import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import time


class Comentarios():
    comentarios = []

    # CREATE
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,  
            password=password
            )
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute(f'USE {database}')
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f'CREATE DATABASE {database}')
                self.conn.database = database
            else:
                raise err
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS comentarios (
            id INT PRIMARY KEY AUTO_INCREMENT,
            provincia VARCHAR(255) NOT NULL,
            nombre VARCHAR(255) NOT NULL,
            comentario VARCHAR(1024) NOT NULL
            )''')
        self.conn.commit()
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

    
    def agregar_comentario (self,provincia,nombre,comentario):
    
        sql = "INSERT INTO comentarios \
            (provincia,nombre,comentario) \
            VALUES \
            ( %s , %s , %s )"
        valores = (provincia,nombre,comentario)
        self.cursor.execute(sql,valores)
        self.conn.commit()
        return True
    
    
    # READ
    
    def listar_por_provincia(self,provincia):
        # Mostramos en pantalla un listado de todos los productos en la tabla
        sql = f"SELECT * FROM comentarios WHERE provincia = '{provincia}' "
        self.cursor.execute(sql)
        comentarios = self.cursor.fetchall()
        return comentarios

    def consultar_comentario(self,id):
        sql = f'SELECT * FROM comentarios WHERE id = {id}'
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    # UPDATE

    def modificar_comentario(self, id, nueva_provincia,nuevo_nombre, nuevo_comentario):
    # Modificamos los datos de un producto a partir de su código
        sql = f"UPDATE comentarios SET provincia = '{nueva_provincia}' , nombre = '{nuevo_nombre}' , comentario = '{nuevo_comentario}' WHERE id = {id} "
        self.cursor.execute(sql)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    # DELETE

    def eliminar_comentario(self,id):
        # Eliminamos un producto de la tabla a partir de su código
        sql = f"DELETE FROM comentarios WHERE id = {id} "
        self.cursor.execute(sql)
        self.conn.commit()
        return self.cursor.rowcount > 0

#----------------------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)

comentarios = Comentarios(host='localhost',user='root',password='root',database='saboresdb')

@app.route("/comentarios",methods=["POST"])
def agregar_comentario():
    #Rocojo los datos del form
    provincia = request.form['provincia']
    nombre = request.form['nombre']
    comentario = request.form['comentario']
    if comentarios.agregar_comentario(provincia,nombre,comentario):
        return jsonify({"mensaje": "Comentario agregado"}), 201
    else:
        return jsonify({"mensaje": "Hubo un error al agregar el comentario"}), 500



@app.route("/comentarios/<string:provincia>",methods = ["GET"])
def listar_por_provincias(provincia):
    coments = comentarios.listar_por_provincia(provincia)
    return jsonify(coments), 200

@app.route("/comentarios/modificar/<int:id>",methods=["PUT"])
def modificar_comentario(id):
    #Recojo datos del form
    nueva_provincia = request.form['provincia']
    nuevo_nombre = request.form['nombre']
    nuevo_comentario = request.form['comentario']
    if comentarios.modificar_comentario(id,nueva_provincia,nuevo_nombre,nuevo_comentario):
        return jsonify({"mensaje": "Comentario modificado"}), 200
    else:
        return jsonify({"mensaje": "Comentario no encontrado"}), 404
    
@app.route("/comentarios/eliminar/<int:id>",methods=["DELETE"])
def eliminar_comentario(id):
    comentario = comentarios.consultar_comentario(id)
    if comentario:
        if comentarios.eliminar_comentario(id):
            return jsonify({"mensaje": "Comentario eliminado"}), 200
        else:
            return jsonify({"mensaje": "Error al eliminar el producto"}), 500
    else:
        return jsonify({"mensaje": "Comentario no encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True)