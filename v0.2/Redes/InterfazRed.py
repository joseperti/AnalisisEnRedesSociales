from tkinter import *
import random
import math
from persistencia import *
from Redes.nodo import *
from Redes.analisisCluster import *
from tkinter.filedialog import *
import io
from PIL import Image,ImageDraw
import copy
import xml.etree.ElementTree as ET

class VentanaRed:

    def __init__(self):

        self.coloreado = "1"#1-Normal de cluster, 2-centralidad de grado

        self.root = Tk()
        self.root.title("Herramienta de análisis de Redes")
        self.cargarMenu()
        self.frame = Frame(master = self.root)
        self.nodos = dict()
        self.canvas = Canvas(master = self.root,width=640,height=480)
        self.canvas.config(background="white")
        self.canvas.pack(fill=BOTH,expand=1)
        #Control de botones sobre el lienzo
        self.canvas.bind('<Button-1>',self.pulsado)
        #self.canvas.bind('<Button-3>',self.resaltarCluster)
        self.canvas.bind('<Button-3>', self.popup)
        self.canvas.bind('<ButtonRelease-1>',self.botonLiberado)
        self.canvas.bind('<B1-Motion>',self.movimiento)
        self.canvas.bind('<Button-2>',self.mostrarInfoNodo)
        self.seleccionado = None
        self.representado = None

        # create a popup menu
        self.menuNodo = Menu(self.root, tearoff=0)

    def cargarMenu(self):

        self.menuBar = Menu(self.root)

        # Menú de Archivo
        self.filemenu = Menu(self.menuBar, tearoff=0)
        self.filemenu.add_command(label="Abrir", command=self.abrirArchivo)
        self.filemenu.add_command(label="Guardar", command=self.guardarArchivo)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exportar CSV",command=self.exportarCSV)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Salir", command=self.root.quit)
        self.menuBar.add_cascade(label="Archivo", menu=self.filemenu)

        #Menú de Análisis de Red
        self.analisisMenu = Menu(self.menuBar, tearoff=0)
        self.analisisMenu.add_command(label="Información de Red", command=self.mostrarInformacionRed)
        self.menuBar.add_cascade(label="Análisis", menu=self.analisisMenu)

        # Menú de Filtros
        self.filtermenu = Menu(self.menuBar, tearoff=0)
        self.restrNodosMenu = Menu(self.menuBar, tearoff=0)
        self.restrNodosMenu.add_command(label="Nodos con ellos mismos", command=self.eliminarNodosEllosMismos)
        self.filtermenu.add_cascade(label="Restricciones de Nodos", menu=self.restrNodosMenu)
        self.menuBar.add_cascade(label="Filtros", menu=self.filtermenu)

        #Menú de Distribución
        self.distrmenu = Menu(self.menuBar,tearoff = 0)
        self.distrmenu.add_command(label="Distribución aleatoria",command=self.redistribuirAleatoria)
        self.menuBar.add_cascade(label="Distribución",menu=self.distrmenu)

        #Menú de herramientas
        self.toolsMenu = Menu(self.menuBar, tearoff=0)
        self.coloreadoMenu = Menu(self.menuBar,tearoff=0)
        self.coloreadoMenu.add_command(label="Por grupo", command=lambda: self.setColoreado("1"))
        self.coloreadoMenu.add_command(label="Centralidad de Grado",command=self.calcularGrados)
        self.toolsMenu.add_cascade(label="Coloreado",menu = self.coloreadoMenu)
        self.menuBar.add_cascade(label="Herramientas", menu=self.toolsMenu)

        self.root.config(menu = self.menuBar)

    def popup(self,event):
        x = event.x
        y = event.y
        for k in self.nodos:
            actual = self.nodos[k]
            if (actual.colision(x, y)):
                self.menuNodo = Menu(self.root, tearoff=0)
                self.menuNodo.add_command(label="Visualizar Cluster", command=self.ventanaCluster)
                self.menuNodo.add_command(label="Resaltar Cluster", command=self.resaltarCluster)
                self.menuNodo.post(event.x_root, event.y_root)
                self.seleccionado = k
                break


    def pulsado(self,event):
        x = event.x
        y = event.y
        actual = None
        #print(x,y)
        for k in self.nodos:
            actual = self.nodos[k]
            if (actual.colision(x,y)):
                #print("Colision con: "+k)
                self.seleccionado = k
                break

    def botonLiberado(self,event):
        if (self.seleccionado!=None):
            self.nodos[self.seleccionado].setPos(event.x,event.y)
            self.pintarRed()
            self.seleccionado = None

    def movimiento(self, event):
        if (self.seleccionado != None):
            self.canvas.create_rectangle(event.x-10,event.y-10,event.x+10,event.y+10,fill="red")
            #self.nodos[self.seleccionado].setPos(event.x, event.y)
            #self.pintarRed()

    def mostrarInfoNodo(self,event):
        #print("Movimiento de ratón en la posición: ", event.x, event.y)
        x = event.x
        y = event.y
        for k in self.nodos:
            actual = self.nodos[k]
            if (actual.colision(x, y)):
                #print("Colision con: "+k)
                actual.setMostrarInfo()
                self.pintarRed()
                break

    def hello(self):
        print("Hello!")

    def resaltarCluster(self):
        #print("Resaltando el cluster seleccionado")
        if self.seleccionado!=None:
            nodosCluster = set()
            pila = list()
            pila.append(self.seleccionado)
            while len(pila)>0:
                elemento = pila.pop()
                print(pila)
                if not(nodosCluster.__contains__(elemento)):
                    nodosCluster.add(elemento)
                    #print("Nodos del cluster: ",repr(nodosCluster))
                    for k in self.nodos[elemento].getDestinos():
                        pila.append(k)
                else:
                    None
                    #print("Ya está estudiado")
            for k in nodosCluster:
                self.nodos[k].pintarNodoDif(self.canvas)
            self.seleccionado = None
        else:
            print("No se ha seleccionado ningún cluster")

    def analisisClustering(self):
        colores = ["red", "orange", "yellow", "green", "blue", "violet"]
        nodosAux = set(self.nodos.copy())
        while len(nodosAux)>0:
            seleccionado = nodosAux.pop()
            nodosCluster = set()
            pila = list()
            pila.append(seleccionado)
            while len(pila) > 0:
                elemento = pila.pop()
                print(pila)
                if not (nodosCluster.__contains__(elemento)):
                    nodosCluster.add(elemento)
                    print("Nodos del cluster: ", repr(nodosCluster))
                    try:
                        for k in self.nodos[elemento].getDestinos():
                            pila.append(k)
                    except:
                        print("Error con el nodo: ",elemento)
                else:
                    print("Ya está estudiado")
            print(repr(nodosCluster))
            color = random.choice(colores)
            for k in nodosCluster:
                try:
                    self.nodos[k].setColor(color)
                    nodosAux.remove(k)
                except:
                    print("Error al eliminar: ",k)

    def ventanaCluster(self):
        if self.seleccionado != None:
            analisis = AnalisisCluster()
            nodosCluster = set()
            pila = list()
            pila.append(self.seleccionado)
            while len(pila) > 0:
                elemento = pila.pop()
                print(pila)
                if not (nodosCluster.__contains__(elemento)):
                    nodosCluster.add(elemento)
                    # print("Nodos del cluster: ",repr(nodosCluster))
                    for k in self.nodos[elemento].getDestinos():
                        pila.append(k)
                else:
                    None
                    # print("Ya está estudiado")
            print("Nodos del cluster: ",repr(nodosCluster))
            for k in nodosCluster:
                self.nodos[k].pintarNodoDif(self.canvas)
                analisis.addNodo(k,copy.copy(self.nodos[k]))
            analisis.pintarCluster()
            self.seleccionado = None
        else:
            print("No se ha seleccionado ningún cluster")

    def addNodo(self,identificador):
        try:
            nodoAux = self.nodos[identificador]
        except:
            self.nodos[identificador] = nodo(identificador)
            self.nodos[identificador].setTextoInfo(identificador)
        #print(self.nodos)

    def addRelacion(self,identificador1,identificador2):
        self.addNodo(identificador1)
        self.addNodo(identificador2)
        self.nodos[identificador1].addEdge(identificador2)
        #Bidireccional
        self.nodos[identificador2].addEdge(identificador1)

    def obtenerNodosSolos(self):
        solos = set()
        for k in self.nodos:
            nodo = self.nodos[k]
            dest = nodo.getDestinos()
            if len(dest) == 0:
                solos.add(k)
            elif len(dest) == 1:
                if (next(iter(dest)) == k):
                    solos.add(k)
        return solos

    def eliminarNodosEllosMismos(self):
        eliminados = self.obtenerNodosSolos()
        for n in eliminados:
            self.nodos.pop(n)
        self.pintarRed()

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
        self.setColoreado("2")

    def setColoreado(self,coloreado):
        self.coloreado = coloreado
        self.pintarRed()

    def pintarRed(self):
        self.canvas.create_rectangle(0,0,self.canvas.winfo_width(),self.canvas.winfo_height(),fill="white")
        for k in self.nodos:
            posIni = self.nodos[k].getPos()
            for l in self.nodos[k].getDestinos():
                posDest = self.nodos[l].getPos()
                self.canvas.create_line(posIni[0],posIni[1],posDest[0],posDest[1])
            if self.coloreado=="1":
                self.nodos[k].pintarNodo(self.canvas)
            elif self.coloreado == "2":
                self.nodos[k].pintarNodoGrado(self.canvas)

    def exportarImagen(self):
        print("Esta función no está aún programada")
        #nombre = asksaveasfilename()
        #imagenSalida = Image(nombre)
        #draw = ImageDraw.Draw(imagenSalida)
        #draw.rectangle([0,0,self.canvas.winfo_width(),self.canvas.winfo_height()])

    def exportarCSV(self):
        archivo = asksaveasfile(mode='w', defaultextension='.csv')
        if archivo is None:
            return
        archivo.write("Source;Target\n")
        for k in self.nodos:
            nodoActual = self.nodos[k]
            destinos = nodoActual.getDestinos()
            for i in destinos:
                archivo.write(str(k)+";"+str(i)+"\n")
        archivo.close()

    def loop(self):
        self.root.mainloop()

    def guardarArchivo(self):
        archivo = asksaveasfile(mode='w',defaultextension='.xml')
        archivo.write("<xml>\n")
        for k in self.nodos:
            nodo = self.nodos[k]
            archivo.write("<nodo textInfo='"+nodo.getTextoInfo()+"' color='"+nodo.getColor()+"' x='"+str(nodo.getPos()[0])+
                          "' y='" +str(nodo.getPos()[1]) +"' id='"+nodo.getId()+"'>\n"+"</nodo>\n")
        for k in self.nodos:
            nodo = self.nodos[k]
            id1 = nodo.getId()
            destinos = nodo.getDestinos()
            for k in destinos:
                archivo.write("<relacion id1='"+id1+"' id2='"+k+"'>\n"+"</relacion>\n")
        archivo.write("</xml>\n")

    def abrirArchivo(self):
        f = askopenfile(filetypes=[("Text files", "*.xml")])
        if f is None:
            return
        arbol = ET.parse(f)
        raiz = arbol.getroot()
        self.nodos = dict()
        for hijo in raiz:
            if hijo.tag == 'nodo':
                # print("Texto: "+k.text)
                nuevoNodo = nodo(hijo.get("id"))
                nuevoNodo.setColor(hijo.get("color"))
                nuevoNodo.setTextoInfo(hijo.get("textInfo"))
                nuevoNodo.setPos(int(hijo.get("x")),int(hijo.get("y")))
                self.nodos[nuevoNodo.getId()] = nuevoNodo
            elif hijo.tag == 'relacion':
                self.addRelacion(hijo.get("id1"),hijo.get("id2"))
        self.pintarRed()

    def redistribuirAleatoria(self):
        for k in self.nodos:
            nodo = self.nodos[k]
            nodo.setRandPos([0,self.canvas.winfo_width()],[0,self.canvas.winfo_height()])
        self.pintarRed()

    def numeroNodos(self):
        return len(self.nodos)

    def numeroRelaciones(self):
        count = 0
        for k in self.nodos:
            count += len(self.nodos[k].getDestinos())
        return count

    def mostrarInformacionRed(self):
        nuevaVentana = Toplevel()
        listado = Label(nuevaVentana,text = "Información de la Red")
        listado.pack()
        listado = Label(nuevaVentana, text="Número de nodos: "+str(self.numeroNodos()))
        listado.pack()
        listado2 = Label(nuevaVentana, text=" Número de relaciones : " + str(self.numeroRelaciones()))
        listado2.pack()
        listado3 = Label(nuevaVentana, text=" Número de nodos aislados : " + str(len(self.obtenerNodosSolos())))
        listado3.pack()


'''ventanica = ventana()
nodos = {'724327303539490816', '724332877014556673', '724335342703239168', '724327053043097602', '724323187467628544', '724329364993769472', '724332633388404736', '724323209420627968', '724333430700388352', '724336630853734404', '724335450865979392', '724332301816082434', '724335804500328448', '724333808615567361', '724333764772552709', '724335942727806977', '724326696539840518', '724324580743999488', '724324303970426880', '724328003606552577', '724325278722457600', '724331003620278274', '724323704088461312', '724326010561376256', '724333780060778498', '724335770006335490', '724327262070427648', '724325065790124033', '724321489001025536', '724334043874103296', '724324847699013637', '724323536354066432', '724325049419714560', '724325488882274305', '724328192996048896', '724325498013274112', '724336466093027328', '724336884315467778', '724331162408235008', '724328307228061696', '724336132591378432', '724333586246148096', '724335712900882432', '724335287527178240', '724326926211538945', '724336080779091968', '724326557754515457', '724334960665059328', '724335548995895298', '724335912184872961', '723825133295702016', '724333590939619329', '724328773039063045', '724333098314436609', '724334942096756738', '724328718848667648', '724336720842502144', '724333534559739905', '724327881699151876', '724325069242003456', '724336195501744130', '724325060492677120', '724328342124695552', '724333396361678848', '724335823555014657', '724335934351773696', '724325893146087424', '724335776415256576', '724332000908316673', '724332174871285761', '724325580087410688', '724322279421784067', '724328006278365185', '724329025649426432', '724334137612619776', '724336575711174656', '724333950609559552', '724325064200445952', '724328678335885312', '724323261996261376', '724329285998268417', '724335241863790592', '724336267375288320', '724331316028825601', '724334062782001152', '724322624797585408', '724329304130203649', '724327304776830976', '724322429212958721', '724336072033996800', '724333095214845952', '724329573689778176', '724332045044948994', '724322963399516160', '724332644532686848', '724328733381910528', '724325575729537024', '724327168025747457', '724323472516743168', '724335527948853248', '724329908189683715', '724326198541688833', '724335523825897474', '724330558034194433', '724323596542324740', '724325070571737092', '724322848681136130', '724326687748546560', '724332172124000256', '724331870155096066', '724335531031695362', '724333955005198336', '724324661446742016', '724323243600056320', '724334879396257792', '724333862671802368', '724335671079538690', '724325067362955265', '724331535231516673', '724336663883821057', '724325062631780352', '724330044194168835', '724324721039388672', '724333832909000707'}
rels = {('724336720842502144', '724336466093027328'), ('724335942727806977', '724335531031695362'), ('724328307228061696', '724327881699151876'), ('724336132591378432', '724335823555014657'), ('724325065790124033', '724325064200445952'), ('724328006278365185', '724327053043097602'), ('724328773039063045', '724328003606552577'), ('724325069242003456', '724325067362955265'), ('724333808615567361', '724332644532686848'), ('724334043874103296', '724332877014556673'), ('724325062631780352', '724325049419714560'), ('724325067362955265', '724325065790124033'), ('724334062782001152', '724331535231516673'), ('724333764772552709', '724333098314436609'), ('724336080779091968', '724335548995895298'), ('724323472516743168', '724323243600056320'), ('724332174871285761', '724329908189683715'), ('724333095214845952', '724332000908316673'), ('724334879396257792', '724333862671802368'), ('724325488882274305', '724324847699013637'), ('724327262070427648', '724326687748546560'), ('724329285998268417', '724328718848667648'), ('724322963399516160', '724322279421784067'), ('724325575729537024', '724323243600056320'), ('724327168025747457', '724326198541688833'), ('724323536354066432', '724323261996261376'), ('724336072033996800', '724335523825897474'), ('724329304130203649', '724328342124695552'), ('724333396361678848', '724332172124000256'), ('724336575711174656', '724335934351773696'), ('724333955005198336', '724333098314436609'), ('724323209420627968', '724322848681136130'), ('724326557754515457', '724325893146087424'), ('724326010561376256', '724325278722457600'), ('724335450865979392', '724333590939619329'), ('724335804500328448', '724333534559739905'), ('724335912184872961', '724333430700388352'), ('724325064200445952', '724325062631780352'), ('724336884315467778', '724335776415256576'), ('724335342703239168', '724333780060778498'), ('724322624797585408', '724321489001025536'), ('724335523825897474', '724333586246148096'), ('724327303539490816', '724326696539840518'), ('724329025649426432', '724323187467628544'), ('724336195501744130', '724335671079538690'), ('724334960665059328', '724332301816082434'), ('724325580087410688', '724322429212958721'), ('724334942096756738', '724333832909000707'), ('724336663883821057', '724335712900882432'), ('724325070571737092', '724324661446742016'), ('724326926211538945', '724326557754515457'), ('724325498013274112', '724324721039388672'), ('724336630853734404', '724336267375288320'), ('724329573689778176', '724328342124695552'), ('724330044194168835', '724325893146087424'), ('724328678335885312', '724323704088461312'), ('724330558034194433', '724323596542324740'), ('724331162408235008', '724327304776830976'), ('724324580743999488', '724324303970426880'), ('724329364993769472', '724328733381910528'), ('724331316028825601', '724328192996048896'), ('724332633388404736', '724331003620278274'), ('724335241863790592', '724334137612619776'), ('724335287527178240', '724333950609559552'), ('724325060492677120', '723825133295702016'), ('724335770006335490', '724335527948853248'), ('724332045044948994', '724331870155096066')}
usuariosTweets = {'724327168025747457': '135591166', '724325067362955265': '1179981192', '724336884315467778': '4452689554', '724325488882274305': '437688121', '724325580087410688': '16826631', '724336720842502144': '2547983690', '724325064200445952': '1179981192', '724336132591378432': '4452689554', '724325893146087424': '13426312', '724328192996048896': '338899906', '724335527948853248': '13426312', '724332644532686848': '351697614', '724325062631780352': '1179981192', '724327881699151876': '13426312', '724335241863790592': '714531252', '724325070571737092': '1335092845', '724331316028825601': '230828683', '724326010561376256': '882614304', '724333586246148096': '157482443', '724335712900882432': '228402657', '724325278722457600': '882614304', '724335548995895298': '338899906', '724326198541688833': '2485822796', '724329285998268417': '228423691', '724333764772552709': '2329395344', '724334062782001152': '369483881', '724323243600056320': '289523460', '724332301816082434': '217086329', '724333832909000707': '238094812', '724335287527178240': '714531252', '724336072033996800': '157482443', '724328307228061696': '253292813', '724326557754515457': '253292813', '724335342703239168': '714531252', '724328006278365185': '437688121', '724322848681136130': '13426312', '724329364993769472': '336490335', '724329573689778176': '253292813', '724328718848667648': '228423691', '724334942096756738': '238094812', '724323536354066432': '182777480', '724334879396257792': '705757877835796480', '724332877014556673': '482389606', '724333808615567361': '49690564', '724323261996261376': '182777480', '724326926211538945': '253292813', '724333950609559552': '503240852', '724333862671802368': '279649054', '724328733381910528': '336490335', '724333095214845952': '253292813', '724333396361678848': '17420939', '724332045044948994': '360101609', '724336466093027328': '2547983690', '724327262070427648': '324838933', '724333534559739905': '69060709', '724331535231516673': '586341114', '724325069242003456': '1179981192', '724336575711174656': '555500343', '724328773039063045': '116820076', '724336267375288320': '196370178', '724329025649426432': '250411481', '724331870155096066': '360101609', '724333780060778498': '143224338', '724328342124695552': '13426312', '724325065790124033': '1179981192', '724332174871285761': '161227542', '724326687748546560': '22954354', '724328003606552577': '116820076', '724324661446742016': '208915015', '724322963399516160': '278998217', '724322624797585408': '16592892', '724335804500328448': '714531252', '724335770006335490': '555500343', '724335523825897474': '714531252', '724336663883821057': '281675074', '724335450865979392': '714531252', '724331162408235008': '1118095687', '724324580743999488': '1335092845', '724328678335885312': '487894221', '724325498013274112': '344990111', '724323187467628544': '250411481', '724336195501744130': '286354111', '724332633388404736': '253292813', '724336080779091968': '361317039', '724335934351773696': '61053469', '724327303539490816': '344990111', '724335912184872961': '714531252', '724333430700388352': '122115502', '724325060492677120': '1179981192', '724323209420627968': '804579889', '724334043874103296': '2770967417', '724325575729537024': '289523460', '724333955005198336': '2569452784', '724335531031695362': '141953288', '724325049419714560': '1179981192', '724330044194168835': '486436112', '724324303970426880': '97424152', '724334960665059328': '449658834', '724332000908316673': '13426312', '724335942727806977': '141953288', '724322429212958721': '544079032', '724333590939619329': '1910582641', '724323472516743168': '289523460', '724326696539840518': '13426312', '724331003620278274': '13426312', '724327053043097602': '437688121', '724330558034194433': '161227542', '724335823555014657': '236910775', '724324847699013637': '338899906', '724329304130203649': '323245712', '724336630853734404': '196370178', '724333098314436609': '13426312', '724324721039388672': '13426312'}'''
'''
def grafoReplicasTweets():
    for k in nodos:
        ventanica.addNodo(k)
    for l in rels:
        ventanica.addRelacion(l[0],l[1])

def grafoReplicaUsuarios():
    moduloPersistencia = Persistencia()
    for k in nodos:
        #usuario = moduloPersistencia.obtenerUsuarioTweet(str(k))
        #if (len(usuario)>0):
        #    usuariosTweets[str(k)] = usuario[0]
        #    ventanica.addNodo(usuario[0])
        try:
            ventanica.addNodo(usuariosTweets[k])
        except:
            print("No se ha encontrado usuario")

    for l in rels:
        try:
            ventanica.addRelacion(usuariosTweets[str(l[0])],usuariosTweets[str(l[1])])
        except:
            print("Usuario no encontrado:",l[0],l[1])

grafoReplicaUsuarios()
ventanica.analisisClustering()
ventanica.pintarRed()
ventanica.loop()'''
#print(usuariosTweets)'''

if __name__=="__main__":
    ventanica = VentanaRed()
    ventanica.loop()
