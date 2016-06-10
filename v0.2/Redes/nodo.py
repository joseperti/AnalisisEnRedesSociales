import random
from tkinter import *
import math

class nodo:

    def __init__(self,id):
        self.id = id
        self.destNodos = set()
        self.relacionIn = set()
        self.relacionOut = set()
        self.pos = [random.randrange(640),random.randrange(480)]
        self.radio = 10
        self.color = "blue"
        self.textoInfo = "Nodo"
        self.mostrarInfo = False
        self.grado = 100

    def addEdge(self,dest):
        if (dest != self.id):
            self.destNodos.add(dest)

    def addRelacionIn(self,dest):
        if (dest != self.id):
            self.relacionIn.add(dest)

    def addRelacionOut(self, dest):
        if (dest != self.id):
            self.relacionOut.add(dest)

    def pintarNodo(self,canvasIn):
        canvasIn.create_rectangle(self.pos[0]-self.radio,self.pos[1]-self.radio,self.pos[0]+self.radio,self.pos[1]+self.radio,fill=self.color)
        self.pintarInfo(canvasIn)

    def pintarNodoDif(self,canvasIn):
        canvasIn.create_rectangle(self.pos[0] - self.radio, self.pos[1] - self.radio, self.pos[0] + self.radio,
                                  self.pos[1] + self.radio, fill="cyan2")
        self.pintarInfo(canvasIn)
    def pintarNodoColor(self,canvasIn,color):
        canvasIn.create_rectangle(self.pos[0] - self.radio, self.pos[1] - self.radio, self.pos[0] + self.radio,
                                  self.pos[1] + self.radio, fill=color)
        self.pintarInfo(canvasIn)

    def pintarNodoGrado(self,canvasIn):
        x = self.grado
        color = '#%02x%02x%02x' % (255-(int(x*255/100)), 255- (int(x*136/100)), 255)
        canvasIn.create_rectangle(self.pos[0] - self.radio, self.pos[1] - self.radio, self.pos[0] + self.radio,
                                  self.pos[1] + self.radio, fill=color)
        self.pintarInfo(canvasIn)

    def getDestinos(self):
        return self.destNodos

    def getPos(self):
        return self.pos

    def colision(self,x,y):
        if (math.sqrt((self.pos[0]-x)**2+(self.pos[1]-y)**2)<10):
            return True
        else:
            return False

    def setPos(self,x,y):
        self.pos = [x,y]

    def getId(self):
        return self.id

    def getColor(self):
        return self.color

    def setColor(self,color):
        self.color = color

    def setTextoInfo(self, texto):
        self.textoInfo = texto

    def getTextoInfo(self):
        return self.textoInfo

    def pintarInfo(self,canvas):
        if (self.mostrarInfo):
            canvas.create_text(self.pos[0],self.pos[1],text=self.textoInfo)

    def getMostrarInfo(self):
        return self.mostrarInfo

    def setMostrarInfo(self):
        self.mostrarInfo = not(self.mostrarInfo)

    def setGrado(self,grado):
        self.grado = grado

    def setRandPos(self,x,y):
        self.pos = [random.randrange(x[0],x[1]), random.randrange(y[0],y[1])]

    def __str__(self):
        return "Nodo: "+str(self.id)