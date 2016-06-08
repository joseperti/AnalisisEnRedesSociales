from persistencia import *
from Redes.InterfazRed import *

class EstudioDatos:

    def __init__(self,identificador):
        self.identificador = identificador
        self.persistencia = Persistencia()

    def analisisDeConversaciones(self):
        cont = 0
        iter = self.persistencia.getIteradorReplicasSeguimientoEnlazado(self.identificador)
        usuarios = set()
        relaciones = []
        for k in iter:
            cont += 1
            usuario1 = k["user_id"]
            usuario2 = k["replicaA"]
            usuarios.add(usuario1)
            if (len(usuario2)>0):
                usuarios.add(usuario2[0]['user_id'])
                relaciones.append([usuario1,usuario2[0]['user_id']])
            #print(k["text"])
            print("Ronda: "+str(cont))
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

