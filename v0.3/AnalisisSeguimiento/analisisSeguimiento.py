#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import *
from persistencia import *
import numpy as np
import matplotlib.pyplot as plt
import sys
import codecs
import os
import webbrowser
import networkx as nx
import community
from random import *
from mpl_toolkits.mplot3d import Axes3D

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

class analisisSeguimiento():

    def __init__(self,identificador):
        plt.ion()
        self.persistencia = Persistencia()
        self.tweets = []
        self.usuarios = []
        self.identificador = identificador
##        self.obtenerTweets()
##        print("Numero de tweets"+str(self.numeroTweets()))
##        print("Realizado proceso sobre los tweets")
##        self.obtenerUsuarios()
##        print("Realizado proceso sobre los usuarios")
        self.informe()
        print("Informe exportado con exito")
        print("Finalizado con exito")

    def pintarBarPlot(self,datosx,datosy,nombreX = "",nombreY= ""):

        
        N = len(datosx)
        ind = np.arange(N)
        width = 0.35

        p1 = plt.bar(ind, datosy, width, color='b')

        plt.ylabel(nombreY)
        plt.title(nombreX)
        plt.xticks(ind + width/2., datosx,rotation="vertical")
##        plt.yticks(np.arange(0, 81, 10))
        plt.subplots_adjust(bottom=0.3)

        #plt.show()    
    #Obtenemos los tweets
    #Si queremos quitar los rts y que no aparezcan utilizamos: rt=False
    def obtenerTweets(self,rt=True):
        if rt:
            self.tweets = self.persistencia.getTweetSeguimiento(self.identificador)
        else:
            self.tweets = self.persistencia.expresionRegularTextoNegada(self.identificador,"^RT ")

    #Obtenemos los usuaios que han realizado retweets
    def obtenerUsuarios(self):
        self.usuarios = self.persistencia.getUsuariosSeguimiento(self.identificador)
    
    def procesarTweets(self):
        with codecs.open("informes//tweets.html","w","utf-8") as file:
            file.write("<!DOCTYPE html><head><meta charset='utf-8'>\n\
                       <script type='text/javascript' src='js/bootstrap.js'>\n\
                       </script>\n\
                       <link rel='stylesheet' type='text/css' href='css/bootstrap.css'>\n\
                       <link rel='stylesheet' type='text/css' href='css/main.css'>\n\
                       </head>\n\
                        <body>\n")
            file.write("<table class='table'><thead><tr><td>Usuario</td><td>Id Tweet</td><td>Texto</td></tr></thead><tbody>")
       
            for k in self.tweets: 
                file.write("<tr><td>"+k["user_id"]+"</td><td>"+k["id_str"] +"</td><td>"+k["text"] +"</td></tr>\n")
            file.write("</tbody></table></body></html>")
        webbrowser.open(os.path.abspath("informes//tweets.html"))


    def procesarUsuarios(self):
        texto = "<html><head><meta charset='utf-8'>\n\
                       <script type='text/javascript' src='js/bootstrap.js'>\n\
                       </script>\n\
                       <link rel='stylesheet' type='text/css' href='css/bootstrap.css'>\n\
                       <link rel='stylesheet' type='text/css' href='css/main.css'>\n\
                       </head>\n\
                        <body>\n"
        texto += "<table class='table'><thead><tr><td>Usuario</td><td>Número de tweets</td></tr></thead><tbody>"
        self.obtenerUsuarios()
        with codecs.open("informes//usuarios.html","w","utf-8") as file:
            for k in self.usuarios: 
                texto += "<tr><td>"+k["_id"]["user_id"]+"</td><td>"+str(k["count"])+"</td></tr>"
            file.write(texto)
        webbrowser.open(os.path.abspath("informes//usuarios.html"))

    #No están incluidos los RTs
    def procesarMensajesReplicas(self):
        texto = "<html><head><meta charset='utf-8'>\n\
                    <script type='text/javascript' src='js/jquery.js'>\n\
                       </script>\n\
                       <script type='text/javascript' src='js/bootstrap.js'>\n\
                       </script>\n\
                       <link rel='stylesheet' type='text/css' href='css/bootstrap.css'>\n\
                       <link rel='stylesheet' type='text/css' href='css/bootstrap-theme.css'>\n\
                       <link rel='stylesheet' type='text/css' href='css/main.css'>\n\
                       </head>\n\
                        <body>\n"
        texto += "<table class='table'><thead><tr><td>Usuario</td><td>Réplica a Tweet</td><td>Id Tweet</td><td>Texto</td><td>Tweet ppal en BBDD</td></tr></thead><tbody>"
        resultados = self.persistencia.getReplicasSeguimiento(self.identificador)
        with codecs.open("informes//mensajes.html","w","utf-8") as file:
            for k in resultados: 
                texto += "<tr><td>"+k["user_id"]+"</td><td>"+k["in_reply_to_status_id"]+"</td><td>"+k["id_str"]+"</td><td>"+k["text"]+"</td>\
                        <td>"+("<span class='glyphicon glyphicon-ok'></span>" if self.persistencia.tweetEnBBDD(k["in_reply_to_status_id"]) else "<span class='glyphicon glyphicon-remove'></span>")+"</td></tr>"
            file.write(texto)
        webbrowser.open(os.path.abspath("informes//mensajes.html"))

    def exportarGrafo(self,nodos,relaciones,colores):
        with open("informes//nodos.txt","w") as archivo:
            archivo.write(str(nodos))
        with open("informes//relaciones.txt","w") as archivo:
            archivo.write(str(relaciones))
        with open("informes//colores.txt","w") as archivo:
            archivo.write(str(colores))
    
    def redMensajesReplicas(self):
        resultados = self.persistencia.getReplicasSeguimiento(self.identificador)
        nodos = set()
        relaciones = set()
        for k in resultados:
            nodos.add(k["id_str"])
            nodos.add(k["in_reply_to_status_id"])
            relaciones.add((k["id_str"],k["in_reply_to_status_id"]))
        grafo = nx.Graph()
        grafo.add_nodes_from(nodos)
        grafo.add_edges_from(relaciones)
        print(nx.info(grafo))
        parts = community.best_partition(grafo)
        nodos = grafo.nodes()
        values = [parts.get(node) for node in nodos]
        comunidades = values
        colores = [rgb_to_hex((randint(100, 200), randint(120, 255), randint(100, 200))) for k in range(0,max(values))]
        valoresColores = []
        coloresCorresp = dict()
        for k in range(len(values)):
            valoresColores.append(colores[values[k]-1])
            coloresCorresp[nodos[k]] = values[k]
##        nx.draw_spring(grafo,node_color=valoresColores)
##        plt.savefig("informes/spring.png")
##        nx.draw_spectral(grafo,node_color=valoresColores)
##        plt.savefig("informes/spectral.png")
##        nx.draw(grafo,node_color=valoresColores)
        self.exportarGrafo(nodos,relaciones,colores)
        plt.savefig("informes/redReplicas.png")
##        nx.draw_circular(grafo,node_color=valoresColores)
##        plt.savefig("informes/circular.png")
        plt.close()
        grados = nx.degree(grafo,grafo.nodes()).values()
##        print(grados)
        lista = [0 for i in range(0,max(grados))]
        for k in grados:
            lista[k-1] += 1
##        print(lista)
        self.pintarBarPlot(range(1,len(lista)+1),lista,"Grado de los nodos","Número de nodos")
        plt.savefig("informes/histogramaGrados.png")
        plt.close()
        #Grafo multiplexado
##        pos = nx.spring_layout(grafo)
##        coords = [[k[0] for k in pos.values()],[k[1] for k in pos.values()]]
##        altura = []
##        fig = plt.figure()
##        ax = fig.add_subplot(111,projection="3d")
##        ax.scatter(coords[0],coords[1],zs=comunidades,c=valoresColores)
##        for k in relaciones:
##            ax.plot(lineas[0][k],lineas[1][k],lineas[2][k],color='r')
##            lineas[0].append([pos[k[0]][0],pos[k[0]][1]])
##            lineas[1].append([pos[k[1]][0],pos[k[1]][1]])
##            lineas[2].append([coloresCorresp[k[0]],coloresCorresp[k[1]]])
##        plt.show()
##        print(lineas)
        
    
    def numeroUsuarios(self):
        return len(self.usuarios)

    def rankingUsuarios(self):
        usuarios = []
        cont = []
        for k in range(5):
            usuarios.append(self.usuarios[k]["_id"]["user_id"])
            cont.append(self.usuarios[k]["count"])
        self.pintarBarPlot(usuarios,cont)

    def evolucionTemporalCantidad(self,savePath=None):
        resultado = self.persistencia.getDateSeguimiento(self.identificador)
        tiempo = []
        cantidad = []
        for k in resultado:
            year = k["_id"]["year"]
            month = self.formatear2Digitos(k["_id"]["month"])
            day = self.formatear2Digitos(k["_id"]["day"])
            hour = self.formatear2Digitos(k["_id"]["hour"])
            minute = self.formatear2Digitos(k["_id"]["minute"])
            tiempo.append(str(hour)+":"+str(minute))
            cantidad.append(k["count"])
        self.pintarBarPlot(tiempo,cantidad)
        if savePath!=None:
            plt.savefig(savePath)
            plt.close()

    def formatear2Digitos(self,dato):
        if len(str(dato))<2:
            return str("0"+str(dato))
        else:
            return str(dato)

    def numeroRTs(self):
        return(len(self.persistencia.expresionRegularTexto(self.identificador,"^RT ")))

    def numeroTweets(self):
        self.obtenerTweets()
        return(len(self.tweets))

    def informe(self):
        directory = "informes"
        nombreArchivo = "archivo.html"
        path = directory+"//"+nombreArchivo
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.evolucionTemporalCantidad(savePath=directory+"//"+"evolucionT.png")
        self.redMensajesReplicas()
        with codecs.open(path, "w", "utf-8") as file:
            file.write("<html><head><meta charset='utf-8'>\n\
                       <script type='text/javascript' src='js/bootstrap.js'>\n\
                       </script>\n\
                       <link rel='stylesheet' type='text/css' href='css/bootstrap.css'>\n\
                       <link rel='stylesheet' type='text/css' href='css/main.css'>\n\
                       </head>"+"\n")
            file.write("<body>"+"\n")
            file.write("<h1>Análisis de Twitter de: "+self.identificador+"</h1>"+"\n")
            file.write("<h2>Datos relevantes</h2>"+"\n")
            file.write("<table class='table'>"+"\n")
            file.write("<thead>"+"\n")
            file.write("<td>Dato</td><td>Cantidad</td>"+"\n")
            file.write("</thead>"+"\n")
            file.write("<tbody>"+"\n")
            file.write("<tr>"+"\n")
            file.write("<td>Número total de Tweets</td><td>"+str(self.numeroTweets())+"</td>"+"\n")
            file.write("</tr>"+"\n")
            file.write("<tr>"+"\n")
            file.write("<td>Número ReTweets</td><td>"+str(self.numeroRTs())+"</td>"+"\n")
            file.write("</tr>"+"\n")
            file.write("<tr>"+"\n")
            file.write("<td>Número de usuarios</td><td>"+str(self.numeroUsuarios())+"</td>"+"\n")
            file.write("</tr>"+"\n")
            file.write("</tbody>"+"\n")
            file.write("</table>"+"\n")
            file.write("<h2>Evolución temporal</h2>"+"\n")
            file.write("<img src='evolucionT.png' center>"+"\n")
            file.write("<h2>Red de réplicas</h2>"+"\n")
            file.write("<img src='redReplicas.png' center>"+"\n")
            file.write("<h3>Distribución de los grados</h3>"+"\n")
            file.write("<img src='histogramaGrados.png' center>"+"\n")
            file.write("</body></html>"+"\n")
        webbrowser.open(os.path.abspath(path))
##ana = analisisSeguimiento("#GotTalent2")
##print(ana.numeroRTs())
ana = analisisSeguimiento("#ElClasico")

