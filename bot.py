import time
time.clock = time.time
from fuzzywuzzy import fuzz
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
import re
from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
import mysql.connector
import pickle

app=Flask(__name__)

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

threshold = 80

chatbot = ChatBot("Chatpot")

trainer = ListTrainer(chatbot)
trainer.train(newresult)


# # Simpan model ke dalam file
# with open('chatbot_model.pkl', 'wb') as file:
#     pickle.dump(chatbot, file)

exit_conditions = (":q", "quit", "exit")

@app.route('/chatbot',methods=['POST'])
def chatbotnya():
    error=None
    if request.method=="POST":
        user_input = request.json
        user_input=user_input["chat"]
        pattern = r"pertanyaan : (.*?)(?:jawabaan : |$)"
        matches1 = re.findall(pattern, user_input, re.DOTALL)
        if len(matches1)>0:
            secondpat=r"jawabaan : (.*)"
            matches2 = re.findall(secondpat, user_input, re.DOTALL)
            if len(matches2)>0:
                cursor.execute("INSERT INTO data(pertanyaan,jawaban) VALUES(\"{}\",\"{}\")".format(matches1[0],matches2[0]))
                mydb.commit()
                response="terimakasih inputan datanya :)"
        else:
            highest_ratio = 0
            matched_question = ''
            for question in newresult:
                ratio = fuzz.ratio(user_input.lower(), question.lower())
                if ratio > highest_ratio and ratio >= threshold:
                    highest_ratio = ratio
                    matched_question = question

            if matched_question:
                response = chatbot.get_response(matched_question)
                response = response.serialize()
                response = response["text"]
            else:
                response = "Maaf, saya tidak memahami pertanyaan Anda."
        return jsonify({"response":response})

@app.route('/',methods=['GET'])
def index(name=None):
    return render_template('chatBOT/index.html')