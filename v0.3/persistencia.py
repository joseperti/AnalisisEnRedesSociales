from pymongo import *
import datetime
import re
from queue import *
'''
Guardar y consultar datos en MongoDB
#####################
Base de datos: "twitterAnalysis"
Tablas:
    · Tweets: "tweet"
    Datos:
        - text - created_at - user_id_str - id_str - in_reply_to_status_id - identificador
    · Usuarios: "usuarios"
    Datos:
        - screen_name - id_str - name 
'''

class Persistencia():

    def __init__(self):
        self.client = MongoClient(maxPoolSize=None)
        self.db = self.client.twitterAnalysis
        self.dbTweet = self.db.tweet
        self.dbUsuarios = self.db.usuario

    def getTweets(self):
        lista = []
        for k in self.dbTweet.find():
            lista.append(k)
        return lista

    def getUsuarios(self):
        lista = []
        for k in self.dbUsuarios.find():
            lista.append(k)
        return lista

    def getTweets(self,id_str):
        lista = []
        for k in self.dbTweet.find({"id_str":id_str}):
            lista.append(k)
        return lista

    def getUsuarios(self,id_str):
        lista = []
        for k in self.dbUsuarios.find({"id_str":id_str}):
            lista.append(k)
        return lista

    def obtenerUsuarioTweet(self,id_str):
        lista = []
        for k in self.dbTweet.find({"id_str":id_str}):
            print("Usuario obtenido: " + repr(k["user_id"]))
            lista.append(k["user_id"])
        return lista


    def insertarTweet(self,text,user_id_str,id_str,in_reply_to_status_id,year,month,day,hour,minute,identificador):
        self.dbTweet.insert_one({"text":text,"user_id":user_id_str,"id_str":id_str,
                                 "in_reply_to_status_id":in_reply_to_status_id,
                                 "year":year,"month":month,"day":day,"hour":hour,"minute":minute,"identificador":identificador,
                                 "fecha":datetime.datetime(year=year,month=month,day=day,hour=hour,minute=minute,second=30)})

    def insertarUsuario(self,screen_name,id_str,name):
        self.dbUsuarios.insert_one({"screen_name":screen_name,"id_str":id_str,"name":name})


    def getTweetSeguimiento(self,identificador):
        lista = []
        for k in self.dbTweet.find({"identificador":identificador}):
            lista.append(k)
        return lista

    def iteradorSeguimiento(self,identificador):
        iterador = iter(self.dbTweet.find({"identificador":identificador}))
        return iterador

    def numeroUsuariosSeguimiento(self,identificador):
        num = 0
        resultado = self.dbTweet.aggregate([{"$match": {"identificador": identificador}},
                                            {"$group": {"_id": {"user_id": "$user_id"}, "count": {"$sum": 1}}},
                                            {"$sort": {"count": -1}}])
        for k in resultado:
            num += 1
        return num

    def getUsuariosSeguimiento(self,identificador):
        lista = []
        resultado = self.dbTweet.aggregate([{ "$match":{"identificador":identificador}},
                                            { "$group": {"_id":{"user_id":"$user_id"}, "count":{"$sum":1 }} },
                                            { "$sort": { "count":-1 } }])
        for k in resultado:
            lista.append(k)
        return lista

    def getReplicasSeguimiento(self,identificador):
        lista = []
        resultado = self.dbTweet.find({"identificador":identificador,"in_reply_to_status_id":{"$ne":None},"text":{"$not":re.compile("^RT ")}})
        return resultado

    def getIteradorReplicasSeguimiento(self,identificador):
        return iter(self.dbTweet.find({"identificador":identificador,"in_reply_to_status_id":{"$ne":None},"text":{"$not":re.compile("^RT ")}}))

    def getIteradorReplicasSeguimientoEnlazado(self,identificador):
        cantidad = self.getReplicasSeguimiento(identificador).count() + 1
        return self.dbTweet.aggregate([
            {"$match":{"identificador": identificador, "in_reply_to_status_id": {"$ne": None}}},
        {
        "$lookup":
        {
        "from": "tweet",
              "localField": "in_reply_to_status_id",
                          "foreignField": "id_str",
        "as": "replicaA"
        }
        }
        ],batchSize=cantidad)

    def getDateSeguimiento(self,identificador,opcion = "Minuto"):
        lista = []
        resultado = []
        if opcion == "Minuto":
            resultado = self.dbTweet.aggregate(
               [
                { "$match":{"identificador":identificador}},
               { "$group": {"_id":"$fecha", "count":{"$sum":1 }} },
               { "$sort": { "_id":1 } }
               ]
            )
            '''cursor = self.dbTweet.find({"identificador":identificador})
            resultado = cursor.sort("fecha",DESCENDING)'''
        elif opcion == "Hora":
            resultado = self.dbTweet.aggregate(
                [
                    {"$match": {"identificador": identificador}},
                    {"$group": {"_id": {"Año": "$year", "Mes": "$month", "Día": "$day", "Hora": "$hour","Minuto":"00"}, "count": {"$sum": 1}}},
                    {"$sort": {"_id": 1}}
                ]
            )
        elif opcion == "Día":
            resultado = self.dbTweet.aggregate(
                [
                    {"$match": {"identificador": identificador}},
                    {"$group": {"_id": {"Año": "$year", "Mes": "$month", "Día": "$day","Hora": "00","Minuto":"00"}, "count": {"$sum": 1}}},
                    {"$sort": {"_id": 1}}
                ]
            )
        elif opcion == "Mes":
            resultado = self.dbTweet.aggregate(
                [
                    {"$match": {"identificador": identificador}},
                    {"$group": {"_id": {"year": "$year", "month": "$month", "Día": "1","Hora": "00","Minuto":"00"}, "count": {"$sum": 1}}},
                    {"$sort": {"_id": 1}}
                ]
            )
        lista = []
        for k in resultado:
            lista.append(k)
        return lista

    def tweetEnBBDD(self,id_str):
        resultado = self.dbTweet.find({"id_str":id_str})
        for k in resultado:
            return True
        return False

    def numeroTweets(self,identificador):
        #print("Buscando: '"+identificador+"'")
        resultado = self.dbTweet.find({"identificador":identificador}).count()
        return resultado

    def tweetsEnTiempo(self,identificador):
        resultado = self.dbTweet.aggregate()
    
    def expresionRegularTexto(self,identificador,expresion):
        lista = []
        resultado = self.dbTweet.find({"text":{"$regex":expresion},"identificador":identificador})
        for k in resultado:
            lista.append(k)
        return lista

    def expresionRegularTextoNegada(self,identificador,expresion):
        lista = []
        resultado = self.dbTweet.find({"text":{"$not":re.compile(expresion)},"identificador":identificador})
        for k in resultado:
            lista.append(k)
        return lista

    def getIdentificadores(self):
        lista = []
        resultado = self.dbTweet.distinct("identificador")
        for k in resultado:
            lista.append(k)
        return lista

    def enlacesIdentificadores(self,identificador1,identificador2):
        valores = self.dbTweet.find({"identificador":identificador2},{"user_id":1,"_id":0})
        lista = list([i["user_id"] for i in valores])
        return list(self.dbTweet.find({"identificador":identificador1,"user_id":{"$in":lista}},{"user_id":1,"_id":0,"identificador":1}))