from persistencia import *
from Redes.InterfazRed import *
from AnalisisDeSentimiento.interfaz import *

class EstudioDatos:

    def __init__(self,identificador):
        self.identificador = identificador
        self.persistencia = Persistencia()


    #se cargan en memoria las correspondencias de id del tweet con el usuario que lo realizo
    def analisisDeConversaciones(self):

        cont = 0
        print("Procedemos a ejecutar la consulta")
        idUsuario = dict()
        iter = self.persistencia.getTweetSeguimiento(self.identificador)
        for k in iter:
            idUsuario[k["id_str"]] = k["user_id"]
        iter = self.persistencia.getReplicasSeguimiento(self.identificador)
        print("Consulta realizada")
        usuarios = set()
        relaciones = []
        for k in iter:
            print("Ronda: " + str(cont))
            cont += 1
            usuario1 = k["user_id"]
            try:
                usuario2 = idUsuario[k["in_reply_to_status_id"]]
                try:
                    sentimiento = self.sentimientos[k["text"]]
                except:
                    sentimiento = None
                relaciones.append([usuario1, usuario2,sentimiento])
            except Exception as err:
                None
                print("Error: "+str(err))
                # print(k["text"])
        print("Número de réplicas a estados: " + str(cont))
        print("Número de réplicas a estados: " + str(cont))
        print(usuarios)
        print(relaciones)

        ventanaRed = VentanaRed()
        for k in usuarios:
            ventanaRed.addNodo(k)
        print(relaciones)
        for k in relaciones:
            ventanaRed.addRelacionPeso(k[0], k[1], k[2])

        ventanaRed.analisisClustering()
        ventanaRed.pintarRed()
        ventanaRed.loop()

    def analisisSentimientos(self,archivo,crearRed=False):
        textosClasif = self.cargarPositivosYNegativos(archivo)
        persistencia = Persistencia()
        print("Identificador:" +str(self.identificador))
        resultados = persistencia.getTweetSeguimiento(str(self.identificador))
        cont = 0
        cont2 = 0
        clasificador = ClasificadorNB()
        clasificador.crearYEntrenar(textosClasif)
        self.sentimientos = dict()
        for k in resultados:
            self.sentimientos[k["text"]] = clasificador.procesarDocumentoSolo(k["text"])
        for k in textosClasif:
            self.sentimientos[k[0]] = k[1]
        #print("Sentimientos:"+str(self.sentimientos))
        #self.analisisDeConversaciones()

        ventanaResultado = Toplevel()
        ventanaResultado.geometry("640x500")
        scrollbar = Scrollbar(ventanaResultado)
        scrollbar.pack(side=RIGHT, fill=Y)
        lista = Listbox(ventanaResultado)
        lista.pack(fill=BOTH, expand=1)
        lista.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=lista.yview)
        textos = self.sentimientos
        if len(textos) == 0:
            ventanaResultado.destroy()
            return
        # print(textos)
        for k in self.sentimientos:
            resultado = self.sentimientos[k]
            try:
                lista.insert(END, k)
            except:
                lista.insert(END,k.encode("utf8"))
            #print(str(k) + ": " + resultado)
            if (resultado == "negative"):
                lista.itemconfig(END, background='coral1')
            elif (resultado=="positive"):
                lista.itemconfig(END, background='pale green')
            else:
                lista.itemconfig(END, background='light blue')

        if crearRed:
            self.analisisDeConversaciones()

    def cargarPositivosYNegativos(self,f):
        print("Abriendo Pos y Negs")
        if f is None:
            print("Es vacío el archivo")
            return
        arbol = ET.parse(f)
        raiz = arbol.getroot()
        textos = []
        for hijo in raiz:
            if hijo.tag == 'positivos':
                for k in hijo.findall('t'):
                    # print("Texto: " + k.text)
                    textos.append([k.text,'positive'])
            elif hijo.tag == 'negativos':
                for k in hijo.findall('t'):
                    # print("Texto: " + k.text)
                    textos.append([k.text, 'negative'])
        return textos

    def cargaEnBaseDatos(self):
        cont = 0
        iter = self.persistencia.getIteradorReplicasSeguimientoEnlazado(self.identificador)
        usuarios = set()
        relaciones = []
        for k in iter:
            print("Ronda: " + str(cont))
            cont += 1
            usuario1 = k["user_id"]
            usuario2 = k["replicaA"]
            usuarios.add(usuario1)
            if (len(usuario2)>0):
                usuarios.add(usuario2[0]['user_id'])
                relaciones.append([usuario1,usuario2[0]['user_id']])
            #print(k["text"])
        print("Número de réplicas a estados: "+str(cont))
        print(usuarios)
        print(relaciones)

        ventanaRed = VentanaRed()
        for k in usuarios:
            ventanaRed.addNodo(k)
        for k in relaciones:
            ventanaRed.addRelacion(k[0],k[1])

        ventanaRed.analisisClustering()
        ventanaRed.pintarRed()
        ventanaRed.loop()




if __name__=="__main__":
    estudio = EstudioDatos("#EurovisionTVE")
    estudio.analisisDeConversaciones()
