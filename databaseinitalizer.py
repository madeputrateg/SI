import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="example",
  database="flask"
)


cursor =mydb.cursor()

# s=open("dataset.txt","r")
# isi=s.readlines()
# for i in range(0,len(isi)-1):
#     if len(isi[i])>2 and len(isi[i+1])>2:
#         cursor.execute("INSERT INTO data(pertanyaan,jawaban) VALUES(\"{}\",\"{}\")".format(isi[i],isi[i+1]))
# mydb.commit()
# s.close()

cursor.execute("SELECT pertanyaan,jawaban FROM data")

result=cursor.fetchall()

newresult=[]
for i in result:
    newresult.append(i[0])
    newresult.append(i[1])
    newresult.append("\n")
