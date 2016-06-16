from persistencia import *
import codecs

if __name__=="__main__":
    file = codecs.open("archivo.txt","w","utf-8")
    ident = "#EurovisionTVE"
    persist = Persistencia()
    resultados = persist.getTweetSeguimiento(ident)
    t1 = "INSERT INTO TWEET(identificador,texto,user_id,year,month,day,hour,minute,in_reply_to_status_id,id_str) values ("
    t3 = ");\n"
    for k in resultados:
        if k["in_reply_to_status_id"] is None:
            replica = "NULL"
        else:
            replica = "'"+k["in_reply_to_status_id"]+"'"
        t2 = "'%s','%s','%s',%s,%s,%s,%s,%s,%s,'%s'" %(k["identificador"],k["text"].replace("'",'"'),
                                                                  k["user_id"],k["year"],k["month"],
                                                                  k["day"],k["hour"],k["minute"],
                                                                  replica,k["id_str"])

        file.write(t1+t2+t3)
    print("Terminado")
    file.close()