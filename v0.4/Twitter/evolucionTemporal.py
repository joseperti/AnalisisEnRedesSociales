from tkinter import *
from tkinter import ttk
from tkinter.dialog import *
from persistencia import *
from time import *
from multiprocessing import *
from Twitter.streamer import *
from EstudioDeDatos.estudioDatos import *
import queue
from Twitter.callTip import *

class InterfazEvolucion:

    def __init__(self,identificador):

        ##Colores:
        self.colorFondo = "azure2"
        self.colorInteriorRect = "white smoke"
        self.colorInteriorRectResaltado = "cyan"
        self.colorExteriorRect = "navy"

        self.seleccionadoAnterior = None
        #################
        self.persistencia = Persistencia()
        self.identificador = identificador
        self.ventana = Toplevel()
        self.ventana.geometry("640x500")
        self.ventana.resizable(width=True,height=True)
        self.ventana.update()
        self.canvas = Canvas(self.ventana,background="white",height=480,width=self.ventana.winfo_width())
        self.canvas.bind("<Button-3>",self.clickDerecho)
        self.canvas.pack()
        self.canvas.bind("<Motion>",self.movimientoGrafico)
        self.etiquetaInfo = Label(self.ventana,text="")
        self.etiquetaInfo.pack(side=BOTTOM)
        self.cargarMenu()
        self.asociacion = "Minuto"
        self.pintarInformacion()

    def clickDerecho(self,event):
        #print("Click Derecho")
        ###Menú sobre la lista de Streams
        self.menuBarraTiempo = Menu(self.ventana, tearoff=0)
        self.menuBarraTiempo.add_command(label="Obtener Tweets", command=lambda: self.informacionBarra(event.x))
        self.menuBarraTiempo.post(event.x_root,event.y_root)

    def informacionBarra(self,posx):
        posicion = int(posx/self.porc)
        #print("Obteniendo información: "+str(self.listadoCoord[posicion][5]))
        fecha = self.listadoCoord[posicion][5]
        year = None
        month = None
        day = None
        hour = None
        minute = None
        if self.asociacion == "Minuto":
            year = fecha.year
            month = fecha.month
            day = fecha.day
            hour = fecha.hour
            minute = fecha.minute
        elif self.asociacion == "Hora":
            year = fecha.year
            month = fecha.month
            day = fecha.day
            hour = fecha.hour
        elif self.asociacion == "Día":
            year = fecha.year
            month = fecha.month
            day = fecha.day
        elif self.asociacion == "Mes":
            year = fecha.year
            month = fecha.month
        resultado = self.persistencia.getTweetFecha(self.identificador,year = year,month = month , day = day, hour = hour ,minute = minute)
        nuevaVentana = Toplevel()
        lista = Listbox(nuevaVentana)
        scrollbar = Scrollbar(nuevaVentana)
        scrollbar.pack(side=RIGHT, fill=Y)
        nuevaVentana.geometry("640x480")
        nuevaVentana.title(self.identificador+" "+str(self.listadoCoord[posicion][5]))
        for k in resultado:
            #print(k)
            try:
                lista.insert(END,k["text"])
            except:
                lista.insert(END, k["text"].encode("utf8"))
        lista.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=lista.yview)
        lista.pack(fill=BOTH,expand=1)

    def movimientoGrafico(self,event):
        if not(self.seleccionadoAnterior is None):
            coords = self.listadoCoord[self.seleccionadoAnterior]
            self.canvas.create_rectangle(coords[0], coords[1], coords[2], coords[3], fill=self.colorInteriorRect,outline = self.colorExteriorRect)
            self.seleccionadoAnterior = None
        #print("("+str(event.x)+","+str(event.y)+")")
        posicion = int(event.x / self.porc)
        #print("Posicion: "+str(posicion)+" cantidad: "+str(self.listado[posicion]))
        coords = self.listadoCoord[posicion]
        self.canvas.create_rectangle(coords[0],coords[1],coords[2],coords[3],fill=self.colorInteriorRectResaltado)
        self.seleccionadoAnterior = posicion
        info = self.listadoCoord[posicion]
        '''try:
            self.etiquetaInfo.config(text=str(info[5]["Año"])+"-"+str(info[5]["Mes"])+"-"+str(info[5]["Día"])+" "+str(info[5]["Hora"])+":"+str(info[5]["Minuto"])+" "+str(info[4]))
        except:'''
        self.etiquetaInfo.config(
            text=str(str(info[5])+" "+str(info[4])))

    def cargarMenu(self):
        self.menuBar = Menu(self.ventana,tearoff=0)
        self.menuBar.add_cascade(label="Archivo")
        self.menuBar.add_cascade(label="Editar")
        self.menuConfig = Menu(self.menuBar,tearoff=0)
        self.menuConfigTiempo = Menu(self.menuBar,tearoff=0)
        self.menuConfigTiempo.add_radiobutton(label="Minuto",command=lambda: self.establecerTiempo(tiempo="Minuto"))
        self.menuConfigTiempo.add_radiobutton(label="Hora",command=lambda: self.establecerTiempo(tiempo="Hora"))
        self.menuConfigTiempo.add_radiobutton(label="Día",command=lambda: self.establecerTiempo(tiempo="Día"))
        self.menuConfigTiempo.add_radiobutton(label="Mes",command=lambda: self.establecerTiempo(tiempo="Mes"))
        self.menuConfig.add_cascade(label="Escala de tiempo",menu=self.menuConfigTiempo)
        self.menuBar.add_cascade(label="Configuración",menu=self.menuConfig)
        self.ventana.config(menu=self.menuBar)

    def pintarExtremos(self,maxi):
        self.canvas.create_text(5, 0, anchor=NW, text="Máximo:"+str(maxi))
        self.canvas.create_text(5, self.canvas.winfo_height() - 5, anchor=SW, text="0")

    def establecerTiempo(self,tiempo="Minuto"):
        self.asociacion = tiempo
        print("Asociacion de tiempo: "+tiempo)
        self.pintarInformacion()

    def pintarInformacion(self):
        self.seleccionadoAnterior = None
        self.canvas.config(width = self.ventana.winfo_width())
        self.canvas.update()
        self.canvas.create_rectangle(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(), fill=self.colorFondo)
        self.listado = self.persistencia.getDateSeguimiento(self.identificador,self.asociacion)
        self.len = 0
        maximo = 0
        for k in self.listado:
            if k["count"] > maximo:
                maximo = k["count"]
            self.len +=1
        x = self.canvas.winfo_width()
        self.porc = x/self.len
        posx = 0
        baseY = self.canvas.winfo_height()
        self.pintarExtremos(maximo)
        maximo = maximo*1.1
        self.listadoCoord = []
        for k in self.listado:
            #print(k["_id"])
            posy = baseY - baseY*k["count"]/maximo
            self.canvas.create_rectangle(int(posx),int(posy),int(posx+self.porc),baseY,fill=self.colorInteriorRect,outline=self.colorExteriorRect)
            self.listadoCoord.append([int(posx),int(posy),int(posx+self.porc),baseY,k["count"],k["fecha"]])
            posx += self.porc






if __name__=="__main__":
    root = Tk()
    interfaz = InterfazEvolucion("#GotTalent2")

    root.mainloop()
