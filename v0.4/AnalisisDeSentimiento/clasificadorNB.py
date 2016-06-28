# URL de guia: http://www.laurentluce.com/posts/twitter-sentiment-analysis-using-python-and-nltk/
#
#

import nltk

class ClasificadorNB():

    def divideTweetInWords(self,tweetIn):
        datos = [e.lower() for e in tweetIn.split() if len(e) >= 3]
        return datos

    def divideTweetInWordsSent(self,tweetsIn):
        tweets = []
        for k in tweetsIn:
            datos = datos = [e.lower() for e in k[0].split() if len(e) >= 3]
            tweets.append([datos,k[1]])
        return tweets

    def get_words_in_tweets(self,tweets):
        all_words = []
        for (words, sentiment) in tweets:
          all_words.extend(words)
        return all_words

    def get_word_features(self,wordlist):
        wordlist = nltk.FreqDist(wordlist)
        #print(wordlist)
        word_features = wordlist.keys()
        return word_features

    def extract_features(self,document):
        document_words = set(document)
        features = {}
        for word in word_features:
            features['contains(%s)' % word] = (word in document_words)
        return features

    def crearYEntrenar(self,tweetsIn):

        tweets = self.divideTweetInWordsSent(tweetsIn)
        # print(tweets)
        global word_features
        words_in_tweets = self.get_words_in_tweets(tweets)
        # print(words_in_tweets)
        word_features = self.get_word_features(words_in_tweets)

        # Entrenamiento
        training_set = nltk.classify.apply_features(self.extract_features, tweets)

        # Entrenamos el clasificador
        self.classifier = nltk.NaiveBayesClassifier.train(training_set)

    def procesarDocumentoSolo(self, documento):
        tweet = documento
        features = self.extract_features(tweet.split())
        # print(features)
        # print(classifier.show_most_informative_features(32))
        return self.classifier.classify(features)

    def procesarDocumento(self,tweetsIn,documento):
        self.crearYEntrenar(tweetsIn)
        self.procesarDocumentoSolo(documento)



    def estudioAceptacion(self,tweetsIn):
        longitud = len(tweetsIn)
        num = 0
        aciertos = 0
        for k in range(longitud):
            aux = tweetsIn[0:k]
            aux += tweetsIn[k+1:longitud]
            documento = tweetsIn[k]
            clasificacion = self.procesarDocumento(aux,documento[0])
            #print("Esperado: "+documento[1]+" devuelto: "+clasificacion)
            if (str(documento[1])==str(clasificacion)):
                aciertos += 1
            num += 1

        return str(int(100*(aciertos*100)/num)/100)+"%"

    def estudioPartes(self,datosIn):
        longitud = len(datosIn)
        p1 = 0.3
        p2 = 0.7


    def clasificadorSimple(self,tweetsIn,documento):
        clasificacion = self.procesarDocumento(tweetsIn, documento)
        return clasificacion

######################################################################
# Ejecución principal
######################################################################

if __name__=="__main__":

    clasif = ClasificadorNB()
    clasif.estudioAceptacion([])