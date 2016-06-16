#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tkinter import *
from tkinter.filedialog import *
import xml.etree.ElementTree as ET
from pymongo import *
import datetime
import codecs
from AnalisisDeSentimiento.clasificadorNB import *

class InterfazSentimientos:
    def __init__(self):
        self.root = Toplevel()
        self.root.title("Herramienta de clasificación")
        self.root.geometry("1080x640")
        self.mainframe = Frame(master=self.root)
        self.cargarMenu()
        self.cargarColumnas()

    def cargarMenu(self):
        self.menuBar = Menu(self.root)

        #Menú de Archivo
        self.filemenu = Menu(self.menuBar, tearoff=0)
        self.filemenu.add_command(label="Abrir", command=self.abrirArchivo)
        self.filemenu.add_command(label="Guardar", command=self.guardarArchivo)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Importar", command=self.importarArchivo)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Salir", command=self.root.quit)
        self.menuBar.add_cascade(label="Archivo", menu=self.filemenu)

        #Menú de Edición
        self.editMenu = Menu(self.menuBar, tearoff=0)
        #self.editMenu.add_command(label="Seleccionar todo", command=self.seleccionarTodoIzq)
        self.editMenu.add_command(label="Eliminar todo", command=self.eliminarTodo)

        self.menuBar.add_cascade(label="Editar",menu = self.editMenu)

        #Menú de Clasificación
        self.clasifMenu = Menu(self.menuBar, tearoff=0)
        self.menuTiposClasificadores = Menu(self.menuBar,tearoff = 0)
        self.menuTiposClasificadores.add_command(label = "Clasificador Naive Bayes",command=self.testNB)
        self.clasifMenu.add_cascade(label="Test de clasificación", menu=self.menuTiposClasificadores)
        self.menuTipoClasificarTodo = Menu(self.menuBar,tearoff=0)
        self.menuTipoClasificarTodo.add_command(label="Clasificador Naive Bayes",command=self.clasificacionNB)
        self.clasifMenu.add_cascade(label="Clasificar Todos",menu=self.menuTipoClasificarTodo)
        self.menuBar.add_cascade(label="Clasificación", menu=self.clasifMenu)

        self.root.config(menu = self.menuBar)

    def cargarColumnas(self):
        scrollbar1 = Scrollbar(self.root)
        scrollbar1.pack(side=LEFT, fill=Y)
        self.listaIzq = Listbox(self.root,selectmode=EXTENDED)

        self.menuListaIzq = Menu(self.root, tearoff=0)
        self.menuListaIzq.add_command(label="Positivo", command=self.mandarPositivo)
        self.menuListaIzq.add_command(label="Negativo", command=self.mandarNegativo)
        self.menuListaIzq.add_separator()
        self.menuListaIzq.add_command(label="Insertar Texto",command=self.insertarTexto)

        self.menuInsListaIzq = Menu(self.root,tearoff=0)
        self.menuInsListaIzq.add_command(label="Insertar Texto", command=self.insertarTexto)

        self.listaIzq.bind('<Button-3>',self.popupListaIzq)
        self.listaIzq.pack(side=LEFT,fill=BOTH,expand=1)

        self.panelDerecho = PanedWindow(self.root,orient=VERTICAL)


        scrollbar2 = Scrollbar(self.panelDerecho)
        scrollbar2.pack(side=RIGHT, fill=Y)
        self.listaPositivo = Listbox(self.panelDerecho)
        self.listaPositivo.config(yscrollcommand=scrollbar2.set)
        scrollbar2.config(command=self.listaPositivo.yview)
        #self.listaDer.pack(side=RIGHT,fill=BOTH,expand=1)
        self.panelDerecho.add(self.listaPositivo)

        scrollbar3 = Scrollbar(self.panelDerecho)
        scrollbar3.pack(side=RIGHT, fill=Y)
        self.listaNegativo = Listbox(self.panelDerecho)
        # self.listaDer.pack(side=RIGHT,fill=BOTH,expand=1)
        self.panelDerecho.add(self.listaNegativo)
        self.listaNegativo.config(yscrollcommand=scrollbar3.set)
        scrollbar3.config(command=self.listaNegativo.yview)
        self.panelDerecho.pack(side=RIGHT,fill=BOTH,expand=1)

    def popupListaIzq(self,event):
        self.seleccionIzq = self.listaIzq.curselection()
        #print(self.seleccion)
        if len(self.seleccionIzq)>0:
            self.menuListaIzq.post(event.x_root, event.y_root)
        else:
            self.menuInsListaIzq.post(event.x_root,event.y_root)

    def insertarTexto(self):
        ventana = Toplevel()
        Label(ventana,text="Insertar Texto:").pack()
        texto = Text(ventana,height=2,width=50)
        texto.pack()
        Button(ventana,text="Insertar",command=lambda: [self.listaIzq.insert(END, texto.get("1.0",END)),ventana.destroy()]).pack()

    def addTexto(self,texto):
        try:
            self.listaIzq.insert(END, texto)
        except:
            self.listaIzq.insert(END, texto.encode("utf8"))

    def eliminarElmListaIzq(self,el):
        self.listaIzq.delete(el)

    def mandarPositivo(self):
        while len(self.listaIzq.curselection())>0:
            k = self.listaIzq.curselection()[0]
            valor = self.listaIzq.get(k)
            #print("Positivo: "+valor)
            self.insertarPositivo(valor)
            self.eliminarElmListaIzq(k)

    def mandarNegativo(self):
        while len(self.listaIzq.curselection())>0:
            k = self.listaIzq.curselection()[0]
            #print(self.listaIzq.curselection())
            valor = self.listaIzq.get(k)
            #print("Negativo: "+valor)
            self.insertarNegativo(valor)
            self.eliminarElmListaIzq(k)

    def insertarPositivo(self,valor):
        self.listaPositivo.insert(END, valor)
        self.listaPositivo.itemconfig(END, background="pale green")

    def insertarNegativo(self,valor):
        self.listaNegativo.insert(END, valor)
        self.listaNegativo.itemconfig(END, background="coral1")

    def hello(self):
        print("Hello!!")

    def ejemplosTextos(self):
        for k in range(100):
            self.listaIzq.insert(END,str(k))

    ##Tratamiento de Archivos

    def importarArchivo(self):
        with codecs.open(askopenfilename(), encoding='utf-8') as nombreArchivo:
            if nombreArchivo is None:
                return
            for line in nombreArchivo.readlines():
                #print(line)
                if (line!=""):
                    try:
                        self.listaIzq.insert(END,line)
                    except:
                        self.listaIzq.insert(END, line.encode("utf8"))

    def escribirArchivo(self,text):
        if (self.archivoSalida is None):
            return
        self.archivoSalida.write(text)

    def guardarArchivo(self):
        self.archivoSalida = asksaveasfile(mode='w',defaultextension='.xml')
        if self.archivoSalida is None:
            return
        textos = self.listaIzq.get(0,END)
        positivos = self.listaPositivo.get(0,END)
        negativos = self.listaNegativo.get(0,END)
        self.escribirArchivo("<xml>\n")
        self.escribirArchivo("<textos>\n")
        #print("Textos: "+str(textos))
        for k in textos:
            self.escribirArchivo("<t>\n")
            #print(k)
            try:
                self.escribirArchivo(k.decode("utf8"))
            except:
                self.escribirArchivo(str(k))
            self.escribirArchivo("</t>\n")
        self.escribirArchivo("</textos>\n")
        self.escribirArchivo("<positivos>\n")
        #print("Positivos: " + str(positivos))
        for k in positivos:
            self.escribirArchivo("<t>\n")
            #print(k)
            try:
                self.escribirArchivo(k.decode("utf8"))
            except:
                self.escribirArchivo(str(k))
            self.escribirArchivo("</t>\n")
        self.escribirArchivo("</positivos>\n")
        self.escribirArchivo("<negativos>\n")
        #print("Negativos: " + str(negativos))
        for k in negativos:
            self.escribirArchivo("<t>\n")
            #print(k)
            try:
                self.escribirArchivo(k.decode("utf8"))
            except:
                self.escribirArchivo(str(k))
            self.escribirArchivo("</t>\n")
        self.escribirArchivo("</negativos>\n")
        self.escribirArchivo("</xml>\n")
        self.archivoSalida.close()

    def abrirArchivo(self):
        f = askopenfile(filetypes=[("Text files", "*.xml")])
        if f is None:
            return
        arbol = ET.parse(f)
        raiz = arbol.getroot()
        for hijo in raiz:
            if hijo.tag == 'textos':
                for k in hijo.findall('t'):
                    #print("Texto: "+k.text)
                    self.listaIzq.insert(END,k.text)
            elif hijo.tag == 'positivos':
                for k in hijo.findall('t'):
                    #print("Texto: " + k.text)
                    self.insertarPositivo(k.text)
            elif hijo.tag == 'negativos':
                for k in hijo.findall('t'):
                    #print("Texto: " + k.text)
                    self.insertarNegativo(k.text)

    def eliminarTodo(self):
        self.listaIzq.delete(0,END)
        self.listaNegativo.delete(0,END)
        self.listaPositivo.delete(0,END)

    ###### Clasificadores

    def obtenerTextosSent(self):
        textos = []
        for k in self.listaNegativo.get(0, END):
            textos.append([k, 'negative'])
        for k in self.listaPositivo.get(0, END):
            textos.append([k, 'positive'])
        return textos

    def testNB(self):
        ventanaResultado = Toplevel()
        ventanaResultado.geometry("300x50")
        mensaje = Label(ventanaResultado,text="Ejecutando Tests con el clasificador seleccionado...")
        mensaje.pack()
        self.root.update()
        textos = self.obtenerTextosSent()
        if len(textos)==0:
            ventanaResultado.destroy()
            return
        print(textos)
        self.clasificadorNB = ClasificadorNB()
        resultado = self.clasificadorNB.estudioAceptacion(textos)
        mensaje.config(text="Porcentaje de acierto: "+resultado)

    def clasificacionNB(self):
        ventanaResultado = Toplevel()
        ventanaResultado.geometry("640x500")
        scrollbar = Scrollbar(ventanaResultado)
        scrollbar.pack(side=RIGHT, fill=Y)
        lista = Listbox(ventanaResultado)
        lista.pack(fill=BOTH,expand=1)
        lista.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=lista.yview)
        self.root.update()
        textos = self.obtenerTextosSent()
        if len(textos) == 0:
            ventanaResultado.destroy()
            return
        #print(textos)
        self.clasificadorNB = ClasificadorNB()
        candidatos = self.listaIzq.get(0,END)
        if len(candidatos)==0:
            ventanaResultado.destroy()
            return
        resultados = dict()
        for k in candidatos:
            resultado = self.clasificadorNB.clasificadorSimple(textos,k)
            lista.insert(END,k)
            print(str(k)+": "+resultado)
            if (resultado == "negative"):
                lista.itemconfig(END,background='coral1')
            else:
                lista.itemconfig(END,background = 'pale green')
            resultados[k] = resultado
        return resultados

    def abrirPositivosNegativos(self,f):
        print("Abriendo Pos y Negs")
        if f is None:
            print("Es vacío el archivo")
            return
        arbol = ET.parse(f)
        raiz = arbol.getroot()
        for hijo in raiz:
            if hijo.tag == 'positivos':
                for k in hijo.findall('t'):
                    # print("Texto: " + k.text)
                    self.insertarPositivo(k.text)
            elif hijo.tag == 'negativos':
                for k in hijo.findall('t'):
                    # print("Texto: " + k.text)
                    self.insertarNegativo(k.text)

if __name__ == "__main__":
    #print("Hello World")
    interf = InterfazSentimientos()
    interf.root.mainloop()