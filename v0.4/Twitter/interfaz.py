from tkinter import *
from tkinter import ttk
from tkinter.dialog import *
from persistencia import *
from time import *
from multiprocessing import *
from Twitter.streamer import *
from EstudioDeDatos.estudioDatos import *
import queue
from Twitter.evolucionTemporal import *
from AnalisisDatosDocumentos.analisis import *

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
        self.listaStreams = Listbox(self.root,selectmod=EXTENDED,width=40)
        self.listaStreams.bind("<Double-Button-1>",self.obtenerInfoStream)
        ###Menú sobre la lista de Streams
        self.menuListaStreams= Menu(self.root, tearoff=0)
        self.menuListaStreams.add_command(label="Iniciar Estático", command=lambda: self.crearStreamer(1))
        self.menuListaStreams.add_command(label="Iniciar Dinámico", command=lambda: self.crearStreamer(2))
        self.menuListaStreams.add_command(label="Parar", command=self.pararStreamer)
        self.menuListaStreams.add_separator()
        self.menuListaStreams.add_command(label="Estudio de seguimiento", command=self.estudioSeguimiento)
        menuRelacionSeguimientos = Menu(self.root,tearoff=0)
        menuRelacionSeguimientos.add_command(label="Sólo seleccionados",command=lambda: self.estudioRelacionSeguimientos())
        menuRelacionSeguimientos.add_command(label="Menciones a Hashtags",
                                             command=lambda: self.estudioRelacionSeguimientos(subHashtags = True))
        self.menuListaStreams.add_cascade(label = "Estudio de relación Seguimientos",menu=menuRelacionSeguimientos)
        self.menuListaStreams.add_separator()
        self.menuListaStreams.add_command(label="Estudio de palabras",command=self.analisisDocumentosPalabras)
        self.menuListaStreams.add_command(label="Estudio de Sentimiento",command=self.estudioSentimiento)
        self.listaStreams.bind('<Button-3>', self.popUpListaStream)

        self.panelDatos = PanedWindow(self.root,orient=VERTICAL)

        self.panelStreams.add(self.listaStreams)
        self.panelStreams.add(self.panelDatos)
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
        seg = self.persistencia.getDateSeguimiento(identificador)
        x = max(500,len(seg)*2)
        maximo = 0
        for i in seg:
            if (i["count"]>maximo):
                maximo = i["count"]
        maximo = maximo * 1.1
        grafico = Canvas(self.panelDatos,width=x,height=300)
        grafico.bind("<Double-Button-1>",lambda event,i=identificador: self.cargarEvolucionTemporal(i) )
        grafico.create_rectangle(0,0,x,300,fill="light blue")
        long = len(seg)
        porc = x/long
        posx = 0
        for k in seg:
            posy = k["count"]
            grafico.create_rectangle(int(posx),300-300*posy/maximo,int(posx+porc),300,fill="white")
            posx += porc
        grafico.grid(row=4,column=0)
        self.panelStreams.add(self.panelDatos,padx=50)

    #VentanaDatosEvoluciónTemporal
    def cargarEvolucionTemporal(self,identificador):
        #print("Creando ventana de evolución temporal: "+identificador)
        evolucion = InterfazEvolucion(identificador)

    ##Control de Streamer

    def crearStreamer(self,opcion):
        print("Creando Streamer")
        indice = self.listaStreams.curselection()
        self.listaStreams.itemconfig(indice,background="green",foreground="white")
        identificador = self.listaStreams.get(indice)
        titulo = identificador
        filtro = identificador
        if opcion == 1:#Guardado simple de tweets
            myStreamListener = MyStreamListener()
        elif opcion == 2:#StreamListener con representación directa en red
            myStreamListener = MyStreamListenerRepresentado()
        myStreamListener.inicializar(titulo,self.persistencia)
        #print("Api: "+str(self.api.auth))
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

    ###Creacion de las redes

    def estudioSeguimiento(self):
        indice = self.listaStreams.curselection()
        identificador = self.listaStreams.get(indice)
        estudio = EstudioDatos(identificador)
        estudio.analisisDeConversaciones()

    def estudioRelacionSeguimientos(self,subHashtags=False):
        indices = self.listaStreams.curselection()
        identificadores = self.listaStreams.get(min(indices),max(indices))
        ventana = VentanaRed()
        if (len(indices)<2):
            return
        for k in identificadores:
            ventana.addNodo(k)
            estudio = AnalizadorDocumentos(k)
            hashtags = estudio.obtenerHashtags()
            if subHashtags:
                for j in hashtags:
                   ventana.addRelacion(k,j)
            else:
                print(hashtags)
                for j in identificadores:
                    print("Buscando: ",j)
                    if j.lower() in hashtags:
                        ventana.addRelacion(k, j)
                        break
        ventana.pintarRed()

    ####Análisis de frecuencias en tweets

    def analisisDocumentosPalabras(self):
        indice = self.listaStreams.curselection()
        identificador = self.listaStreams.get(indice)
        estudio = AnalizadorDocumentos(identificador)
        freq, hashtags = estudio.analisisFreqPalabras()
        nuevaVentana = Toplevel()
        nuevaVentana.geometry("640x480")
        panel = PanedWindow(nuevaVentana,orient=HORIZONTAL)
        listado1 = Listbox(nuevaVentana,selectmod=EXTENDED)
        for k in freq:
            try:
                listado1.insert(0,"%s - %s" %(k[0],k[1]))
            except:
                listado1.insert(0, "%s - %s" % (k[0].encode("utf8"), k[1]))
        panel.add(listado1)
        listado2 = Listbox(nuevaVentana,selectmod=EXTENDED)
        for k in hashtags:
            try:
                listado2.insert(0, "%s" % (k))
            except:
                listado2.insert(0,
                                "%s" %(
                                    k[0].encode("utf8")))
        panel.add(listado2)
        panel.pack(ipadx=2,ipady=2,fill=BOTH,expand=True)
        print("Finalizado el estudio de frecuencias")

    #Estudios de Sentimiento y análisis Semántico
    def estudioSentimiento(self):
        ventana = Toplevel()
        ventana.title("Crear Clasificación de Sentimiento")
        Label(ventana,text="Tipo de clasificador",justify=LEFT).pack(fill=X)
        seleccionTipo = ttk.Combobox(ventana,state="readonly")
        seleccionTipo['values'] = ('Naive Bayes','LSA')
        seleccionTipo.current(0)
        seleccionTipo.pack(padx=10,pady=10)
        Label(ventana,text="Datos clasificados",justify=LEFT).pack(fill=X)
        panel = PanedWindow(ventana,orient=HORIZONTAL)
        self.mostrarNombreArchivo = Entry(ventana,width="30",state="readonly")
        try:
            if not(self.archivoSentClasif is None):
                self.mostrarNombreArchivo.config(state=NORMAL)
                self.mostrarNombreArchivo.insert(0, self.archivoSentClasif.name)
                self.mostrarNombreArchivo.config(state="readonly")
        except:
            self.mostrarNombreArchivo.config(state=NORMAL)
            self.mostrarNombreArchivo.insert(0,"Ninguno")
            self.mostrarNombreArchivo.config(state="readonly")
        panel.add(self.mostrarNombreArchivo)
        panel.add(Button(ventana,text="Abrir archivo",command = self.seleccionarArchivoSent))
        panel.pack(padx=10,pady=10)

        Label(ventana,text="Test sobre textos clasificados",justify=LEFT).pack(fill=X)
        panel = PanedWindow(ventana,orient=HORIZONTAL)
        seleccionTest = ttk.Combobox(panel,state="readonly")
        seleccionTest['values'] = ('1 Out', '30%/70%')
        seleccionTest.current(0)
        seleccionTest.pack(padx=10, pady=10)
        labelResultado = Label(ventana, text="Resultado test: ", justify=LEFT)
        boton = Button(panel,text="Testear",command=lambda: self.realizarTest(labelResultado,seleccionTipo,seleccionTest))
        boton.pack(ipadx=2)
        panel.pack(fill=X)

        labelResultado.pack(fill=X)
        seleccionCheck = IntVar()
        c = Checkbutton(ventana, text="Crear Red de conversaciones", variable=seleccionCheck)
        c.pack(pady=10)
        Button(ventana,text="Procesar Sentimientos",command=lambda: (self.procesarSentimientos(seleccionCheck),ventana.destroy())).pack(pady=20)

    def realizarTest(self,labelResultado,seleccionTipo,seleccionTest):
        print(seleccionTipo.selection_get())
        print(seleccionTest.selection_get())
        labelResultado.config(text=str(seleccionTipo.selection_get() + " - " + seleccionTest.selection_get()))
        estudio = EstudioDatos(self.listaStreams.get(self.seleccionStream[len(self.seleccionStream) - 1]))

    def procesarSentimientos(self,checkCrearRed):
        #print(checkCrearRed.get())
        if self.archivoSentClasif is None:
            return
        estudio = EstudioDatos(self.listaStreams.get(self.seleccionStream[len(self.seleccionStream)-1]))
        estudio.analisisSentimientos(self.archivoSentClasif,checkCrearRed.get())


    def seleccionarArchivoSent(self):
        self.archivoSentClasif = askopenfile(filetypes=[("Text files", "*.xml")])
        if self.archivoSentClasif is None:
            return
        self.mostrarNombreArchivo.delete(0,END)
        self.mostrarNombreArchivo.config(state=NORMAL)
        self.mostrarNombreArchivo.insert(0,self.archivoSentClasif.name)
        self.mostrarNombreArchivo.config(state="readonly")

if __name__ == '__main__':
    Interfaz()