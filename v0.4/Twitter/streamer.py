from time import *
from multiprocessing import *
from persistencia import *
import tweepy
import json
from pymongo import *
from persistencia import *
import datetime
from tkinter import *
import tweepy
from Redes.InterfazRed import *

textoTweets = "Cantidad de Tweets: "

#####Clase para streaming
class MyStreamListener(tweepy.StreamListener):

    def inicializar(self,identificador,pers):
        self.identificador = identificador
        self.ventana = Toplevel()
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrarConexion)
        self.ventana.geometry("300x50")
        self.ventana.title("Seguimiento de "+identificador)
        self.persistencia = pers
        self.cantidadTweets = self.persistencia.numeroTweets(identificador)
        self.labelCantidad = Label(self.ventana,text = textoTweets+str(self.cantidadTweets))
        Label(self.ventana,text="Seguimiento de "+identificador).pack(side=LEFT)
        self.labelCantidad.pack(side=LEFT)

    def updateCantidadTweets(self):
        self.labelCantidad.config(text=textoTweets+str(self.cantidadTweets))
        #self.ventana.update()

    def on_status(self, status):
        try:
            '''print(status.text,status.created_at,
                                            status.user.id_str,status.id_str,
                                            status.in_reply_to_status_id_str,
                                            status.created_at.year,status.created_at.month,
                                            status.created_at.day,status.created_at.hour,
                                            status.created_at.minute)'''
            #self.contador += 1
            #print("Tweet: ",self.contador)
            self.persistencia.insertarTweet(status.text,status.user.id_str,status.id_str,
                                            status.in_reply_to_status_id_str,
                                            status.created_at.year,status.created_at.month,
                                            status.created_at.day,status.created_at.hour,
                                            status.created_at.minute,self.identificador)
            self.cantidadTweets += 1
            self.updateCantidadTweets()
        except Exception as err:
            print("Fallo en el tweet!!!!: "+str(err))

    def setStream(self,stream):
        self.stream = stream

    def cerrarConexion(self):
        self.stream.disconnect()
        self.ventana.destroy()

class MyStreamListenerRepresentado(tweepy.StreamListener):

    def inicializar(self,identificador,pers):
        self.identificador = identificador
        self.ventana = VentanaRed()
        self.persistencia = pers
        self.idUsuario = dict()
        self.contador = 0

    def aumentarContador(self):
        self.contador +=1
        self.ventana.setTitle("Seguimiento: "+self.identificador+" - "+str(self.contador))

    def on_status(self, status):
        try:
            '''print(status.text,status.created_at,
                                            status.user.id_str,status.id_str,
                                            status.in_reply_to_status_id_str,
                                            status.created_at.year,status.created_at.month,
                                            status.created_at.day,status.created_at.hour,
                                            status.created_at.minute)'''
            #self.contador += 1
            #print("Tweet: ",self.contador)
            self.persistencia.insertarTweet(status.text,status.user.id_str,status.id_str,
                                            status.in_reply_to_status_id_str,
                                            status.created_at.year,status.created_at.month,
                                            status.created_at.day,status.created_at.hour,
                                            status.created_at.minute,self.identificador)
            self.aumentarContador()
            self.idUsuario[status.id_str] = status.user.id_str
            if not(status.in_reply_to_status_id_str is None):
                try:
                    usuarioDestino = self.idUsuario[status.in_reply_to_status_id_str]
                    self.ventana.addRelacion(status.user.id_str,usuarioDestino)
                    self.ventana.pintarNodoRels(status.user.id_str)
                    self.ventana.pintarNodoRels(usuarioDestino)
                except Exception as err:
                    print("No se encuentra en memoria: "+str(err))

        except Exception as err:
            print("Fallo en el tweet!!!!: "+str(err))

    def setStream(self,stream):
        self.stream = stream

    def cerrarConexion(self):
        self.stream.disconnect()
        self.ventana.destroy()

if __name__ == '__main__':
    stream = MyStreamListener()
    stream.inicializar("#Hola",Persistencia())