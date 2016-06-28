from persistencia import *

class AnalizadorDocumentos():

    def __init__(self,identificador):

        self.identificador = identificador
        self.persistencia = Persistencia()
        self.palabrasEliminadas = [
            "rt",identificador.lower()
        ]
        self.numCaracteresMinimo = 1

    def divideDocumentInWords(self,docIn):
        words = [e.lower() for e in docIn.split() if len(e) >= self.numCaracteresMinimo]
        return words

    def analisisFreqPalabras(self):
        frecuencias = dict()
        hashtags = set()
        documentos = self.persistencia.getTweetSeguimiento(self.identificador)
        cantidadIntervalo = 10000
        count = 0
        for t in documentos:
            words = self.divideDocumentInWords(t["text"])
            for w in words:
                try:
                    self.palabrasEliminadas.index(w)
                    continue
                except:
                    None
                try:
                    freqActual = frecuencias[w]
                    freqActual += 1
                    frecuencias[w] = freqActual
                    if (w[0]=="#"):
                        hashtags.add(w)
                except:
                    frecuencias[w] = 1
            count += 1
            if (count%cantidadIntervalo == 0):
                print("Procesados: ",count)
        cantidadImprimir = 5
        cola = []
        for k in sorted(frecuencias, key=frecuencias.__getitem__):
            #print(k,frecuencias[k])
            cola.append([k,frecuencias[k]])
            #if len(cola) > cantidadImprimir:
            #    cola.remove(cola[0])
        print("Procesadas las palabras más frecuentes")
        return cola,hashtags

    def obtenerHashtags(self):
        hashtags = set()
        documentos = self.persistencia.getTweetSeguimiento(self.identificador)
        for t in documentos:
            words = self.divideDocumentInWords(t["text"])
            for w in words:
                if (w[0] == "#"):
                    hashtags.add(w)
        return hashtags

