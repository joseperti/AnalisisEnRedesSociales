from tkinter import *
from Redes.nodo import *


class AnalisisCluster:
    def __init__(self):
        #Cargamos los nodos
        self.nodos = dict()
        self.root = Tk()
        self.ventana = Toplevel()
        self.ventana.geometry("640x480")
        # Cargamos los componentes de la ventana
        self.cargarMenu()
        self.ventana.title("Herramienta de análisis de clústers")
        self.canvas = Canvas(master=self.ventana, width=640, height=480)
        self.canvas.config(background="white")
        self.canvas.pack(fill=BOTH, expand=1)
        #Control de botones sobre el lienzo
        self.canvas.bind('<Button-1>',self.pulsado)
        #self.canvas.bind('<Button-3>',self.resaltarCluster)
        self.canvas.bind('<ButtonRelease-1>',self.botonLiberado)
        self.canvas.bind('<B1-Motion>',self.movimiento)
        self.canvas.bind('<Button-2>',self.mostrarInfoNodo)
        self.seleccionado = None
        self.representado = None
        self.gradoMaximo = 0

        #Ocultamos la ventana por defecto
        self.root.withdraw()

    def hello(self):
        print("Hello!")

    def cargarMenu(self):

        self.menuBar = Menu(self.ventana)

        # Menú de Archivo
        self.filemenu = Menu(self.menuBar, tearoff=0)
        self.filemenu.add_command(label="Abrir", command=self.hello)
        self.filemenu.add_command(label="Salir", command=self.root.quit)
        self.menuBar.add_cascade(label="Archivo", menu=self.filemenu)

        #Menú de herramientas
        self.toolsMenu = Menu(self.menuBar, tearoff=0)
        self.coloreadoMenu = Menu(self.menuBar,tearoff=0)
        self.coloreadoMenu.add_command(label="Centralidad de Grado",command=self.calcularGrados)
        self.toolsMenu.add_cascade(label="Coloreado",menu = self.coloreadoMenu)
        self.menuBar.add_cascade(label="Herramientas", menu=self.toolsMenu)

        self.ventana.config(menu=self.menuBar)

    def mostrarInfoNodo(self, event):
        # print("Movimiento de ratón en la posición: ", event.x, event.y)
        x = event.x
        y = event.y
        for k in self.nodos:
            actual = self.nodos[k]
            if (actual.colision(x, y)):
                # print("Colision con: "+k)
                actual.setMostrarInfo()
                self.pintarCluster()
                break

    def calcularGrados(self):
        max = 0
        for k in self.nodos:
            gr = len(self.nodos[k].getDestinos())
            if gr>max:
                max = gr
        print("El máximo es: "+str(max))
        if max == 0:
            for k in self.nodos:
                self.nodos[k].setGrado(100)
        else:
            for k in self.nodos:
                gr = len(self.nodos[k].getDestinos())
                print("Cantidad destinos: "+str(gr)+"\n"+str(self.nodos[k].getDestinos()))
                self.nodos[k].setGrado(int(gr*100/max))
        self.pintarCluster()

    def addNodo(self,identificador,nodo):
        self.nodos[identificador] = nodo

    def pintarCluster(self):
        self.canvas.create_rectangle(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(), fill="white")
        for k in self.nodos:
            posIni = self.nodos[k].getPos()
            for l in self.nodos[k].getDestinos():
                posDest = self.nodos[l].getPos()
                self.canvas.create_line(posIni[0],posIni[1],posDest[0],posDest[1])
            self.nodos[k].pintarNodoGrado(self.canvas)

    def pulsado(self, event):
        x = event.x
        y = event.y
        actual = None
        # print(x,y)
        for k in self.nodos:
            actual = self.nodos[k]
            if (actual.colision(x, y)):
                # print("Colision con: "+k)
                self.seleccionado = k
                break

    def botonLiberado(self, event):
        if (self.seleccionado != None):
            self.nodos[self.seleccionado].setPos(event.x, event.y)
            self.pintarCluster()
            self.seleccionado = None

    def movimiento(self, event):
        if (self.seleccionado != None):
            self.canvas.create_rectangle(event.x - 10, event.y - 10, event.x + 10, event.y + 10, fill="red")
            # self.nodos[self.seleccionado].setPos(event.x, event.y)
            # self.pintarRed()

if __name__=="__main__":
    analisis = AnalisisCluster()
    analisis.root.mainloop()