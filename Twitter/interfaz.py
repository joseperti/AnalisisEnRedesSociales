from tkinter import *
from tkinter.dialog import *
from persistencia import *
from time import *
from multiprocessing import *
from Twitter.streamer import *
from EstudioDeDatos.estudioDatos import *

persistencia = Persistencia()

########################################################

class Interfaz:

    def __init__(self):
        self.actual = None
        self.cargarBaseDatos()
        self.cargarConexionTwitter()
        self.procesosStream = dict()
        self.ventanasStream = dict()

        self.root = Tk()
        self.root.title("Herramienta de descarga de datos - Twitter")

        self.cargarMenu()
        self.cargarFormulario()
        self.cargarPanel()
        self.root.geometry("640x480")

        self.root.mainloop()

        #Acabamos con todos los procesos
        for k in self.procesosStream:
            self.procesosStream[k].disconnect()

    def cargarMenu(self):
        self.menuBar = Menu(self.root)

        # Menú de Archivo
        self.filemenu = Menu(self.menuBar, tearoff=0)
        self.filemenu.add_command(label="Salir", command=self.root.quit)
        self.menuBar.add_cascade(label="Archivo", menu=self.filemenu)

        #Menú Editar
        self.editMenu = Menu(self.menuBar, tearoff=0)
        self.editMenu.add_command(label="Eliminar todo", command=self.eliminarTodo)

        self.menuBar.add_cascade(label="Editar", menu=self.editMenu)

        #Menú Base de Datos
        self.baseDatosMenu = Menu(self.menuBar, tearoff=0)
        self.baseDatosMenu.add_command(label="Obtener Identificadores", command=self.obtenerIdentificadores)
        self.menuBar.add_cascade(label="Base de Datos", menu=self.baseDatosMenu)

        self.root.config(menu=self.menuBar)

    def cargarFormulario(self):
        self.formulario = PanedWindow(self.root,orient = HORIZONTAL)
        self.entrada = Entry(self.root)
        self.btn = Button(self.root,text="Crear Stream",command=self.addStream)
        self.formulario.add(self.entrada)
        self.formulario.add(self.btn)
        self.formulario.pack(pady=10)

    def cargarPanel(self):
        self.panelStreams = PanedWindow(self.root,orient = HORIZONTAL)
        self.listaStreams = Listbox(self.root)
        self.listaStreams.bind("<Double-Button-1>",self.obtenerInfoStream)
        ###Menú sobre la lista de Streams
        self.menuListaStreams= Menu(self.root, tearoff=0)
        self.menuListaStreams.add_command(label="Iniciar", command=self.crearStreamer)
        self.menuListaStreams.add_command(label="Parar", command=self.pararStreamer)
        self.menuListaStreams.add_separator()
        self.menuListaStreams.add_command(label="Estudio de seguimiento", command=self.estudioSeguimiento)
        self.listaStreams.bind('<Button-3>', self.popUpListaStream)

        self.panelDatos = PanedWindow(self.root,orient=VERTICAL)

        self.panelStreams.add(self.listaStreams)
        self.panelStreams.add(self.panelDatos,padx=10)
        self.panelStreams.pack(fill=BOTH,expand=1,padx=10,pady=10)

    def popUpListaStream(self,event):
        self.seleccionStream = self.listaStreams.curselection()
        # print(self.seleccion)
        if len(self.seleccionStream) > 0:
            self.menuListaStreams.post(event.x_root, event.y_root)

    def obtenerInfoStream(self,e):
        seleccionado = self.listaStreams.get(self.listaStreams.curselection()[0])
        #print(seleccionado)
        self.cargarDatosStream(seleccionado)

    def addStream(self):
        identificador = self.entrada.get()
        self.listaStreams.insert(END,identificador)
        self.entrada.delete(0,END)

    def eliminarTodo(self):
        self.listaStreams.delete(0, END)

    ##Acceso a BBDD

    def cargarBaseDatos(self):
        self.persistencia = Persistencia()

    def obtenerIdentificadores(self):
        identificadores = self.persistencia.getIdentificadores()
        #print(identificadores)
        for k in identificadores:
            self.listaStreams.insert(END,k)

    def cargarDatosStream(self,identificador):
        self.actual = identificador
        self.panelDatos.destroy()
        self.panelDatos = PanedWindow(self.root,orient=VERTICAL)
        Label(self.panelDatos,text="Identificador: "+identificador).grid(row=0,column=0)
        Label(self.panelDatos,text="Número de tweets: "+str(self.persistencia.numeroTweets(identificador))).grid(row=1,column=0)
        Label(self.panelDatos,text="Número de usuarios: "+str(self.persistencia.numeroUsuariosSeguimiento(identificador))).grid(row=2,column=0)
        self.panelStreams.add(self.panelDatos)

    ##Control de Streamer

    def crearStreamer(self):
        print("Creando Streamer")
        indice = self.listaStreams.curselection()
        self.listaStreams.itemconfig(indice,background="green",foreground="white")
        identificador = self.listaStreams.get(indice)
        titulo = identificador
        filtro = identificador
        myStreamListener = MyStreamListener()
        myStreamListener.inicializar(titulo,self.persistencia)
        print("Api: "+str(self.api.auth))
        myStream = tweepy.Stream(auth=self.api.auth, listener=myStreamListener)
        self.procesosStream[identificador] = myStream
        self.ventanasStream[identificador] = myStreamListener
        myStreamListener.setStream(myStream)
        myStream.filter(track=[filtro],async=True)

    def pararStreamer(self):
        indice = self.listaStreams.curselection()
        self.listaStreams.itemconfig(indice, background="white", foreground="black")
        identificador = self.listaStreams.get(indice)
        try:
            self.ventanasStream[identificador].cerrarConexion()
        except:
            None


    ##Establecemos la conexión a Twitter
    def cargarConexionTwitter(self):
        consumerKey = "MrOBuLfa1aJ4Yz7EpT4K650AZ"
        consumerSecret = "psSONPQbnkRf331GWORgEFASc1u8zZ3jYOKNq5cxzFm6l4mbr1"

        accessToken = "253145620-W7P74YI0ATn81s9w9SSBz7VD3GEcT3OLgW7toPvo"
        accessTokenSecret = "qryUeBgU43YJ2etFqEA1QcpReZgg5CvwXr9aiRsrprEEv"

        auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
        auth.secure = True
        auth.set_access_token(accessToken, accessTokenSecret)

        print("Creando api")
        self.api = tweepy.API(auth)

    def estudioSeguimiento(self):
        indice = self.listaStreams.curselection()
        identificador = self.listaStreams.get(indice)
        estudio = EstudioDatos(identificador)
        estudio.analisisDeConversaciones()


if __name__ == '__main__':
    Interfaz()