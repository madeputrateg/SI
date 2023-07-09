import time
time.clock = time.time
from fuzzywuzzy import fuzz
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
import re
from flask import Flask , request , render_template , jsonify , sessions , Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from flask_login import LoginManager,UserMixin,login_user,logout_user
import uuid
import mysql.connector
import pickle

app=Flask(__name__)

# mydb = mysql.connector.connect(
#   host="localhost",
#   user="root",
#   password="example",
#   database="flask"
# )
app.secret_key = 'your-secret-key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'example'
app.config['MYSQL_DB'] = 'flask'

mydb=MySQL(app)
login_manager=LoginManager(app)
newresult=[]
with app.app_context():
    cursor =mydb.connection.cursor()
    cursor.execute("SELECT pertanyaan,jawaban FROM data")
    result=cursor.fetchall()
    for i in result:
        newresult.append(i[0])
        newresult.append(i[1])
        newresult.append("\n")
    cursor.close()

# s=open("dataset.txt","r")
# isi=s.readlines()
# for i in range(0,len(isi)-1):
#     if len(isi[i])>2 and len(isi[i+1])>2:
#         cursor.execute("INSERT INTO data(pertanyaan,jawaban) VALUES(\"{}\",\"{}\")".format(isi[i],isi[i+1]))
# mydb.commit()
# s.close()



class User(UserMixin):
    def __init__(self, id):
        self.id = id

    @staticmethod
    def get(user_id):
        cur = mydb.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cur.fetchone()
        cur.close()

        if user_data is None:
            return None

        user = User(user_id)
        user.username = user_data['username']
        user.email=user_data['email']
        user.is_admin=user_data['is_admin']
        user.password=user_data["password"]
        return user

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        message=""
        data = request.json
        if data["email"]==None or data["password"]==None or data["username"]==None:
            message="data yang diterima kurang"
        else :
            id_user=str(uuid.uuid4())
            user={"id":id_user,"username":data["username"],"email":data["email"],"password":generate_password_hash(data["password"],method='scrypt'),"is_admin":0}
            try:
                with app.app_context():
                    cur =mydb.connection.cursor()
                    cur.execute("INSERT INTO users(id,username,password,email,is_admin) VALUES(%s,%s,%s,%s,%s)",(user["id"],user["username"],user["password"],user["email"],user["is_admin"]))
                    mydb.connection.commit()
                    message="user data added to database"
                    cur.close()
            except Exception as e:
                message="error occur during connection or excution of database:" + str(e)
        return jsonify({"message":message})
    else:
        return render_template("auth/signup.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        message=""
        returndata={}
        data = request.json
        if  data["password"]==None or data["username"]==None:
            message="data yang diterima kurang"
        else :
            try:
                with app.app_context():
                    cur =mydb.connection.cursor()
                    username=(data["username"],)
                    sql="SELECT id,username,password,email,is_admin FROM users WHERE username = %s"
                    cur.execute(sql,username)
                    user_data = cur.fetchall()
                    if user_data == None:
                        message="there is not user"
                    else:
                        if check_password_hash(user_data[0][2],data["password"]):
                            returndata["id"]=user_data[0][0]
                            message="logged"
                            user = User(user_data[0][0])
                            user.username = user_data[0][1]
                            user.password=user_data[0][2]
                            user.email=user_data[0][3]
                            user.is_admin=user_data[0][4]
                            login_user(user)
                        else:
                            message="there is not user"
                    cur.close()
            except Exception as e:
                message="error occur during connection or excution of database" +" " +str(e)
        return jsonify({"message":message,"data":returndata})
    else:
        return render_template("auth/login.html")


threshold = 80

chatbot = ChatBot("Chatpot")

trainer = ListTrainer(chatbot)
trainer.train(newresult)


# # Simpan model ke dalam file
# with open('chatbot_model.pkl', 'wb') as file:
#     pickle.dump(chatbot, file)

def authAdmin(id):
    with app.app_context():
        try:
            cur =mydb.connection.cursor()
            id=(id,)
            sql="SELECT id,username,password,email,is_admin FROM users WHERE id = %s"
            cur.execute(sql,id)
            user_data = cur.fetchall()
        except Exception as e:
            raise e
        if user_data==None:
            return False
        if user_data[0][4]==1:
            return user_data
        else: 
            return False
        

@app.route('/admin/addbody',methods=['POST'])
def input():
    data=request.json
    message="data succes fully inserted"
    if data["pertanyaan"]==None or data["jawaban"]==None or data["id"]==None:
        message="data input kurang"
    else:
        user_id=data["id"]
        try:
            auth = authAdmin(user_id)
        except Exception as e:
            message="error authication : " + str(e)
            auth=False
        if auth:
            with app.app_context():
                try:
                    cur= mydb.connection.cursor()
                    sql="INSERT INTO data (pertanyaan,jawaban) VALUES(%s,%s)"
                    val = (data["pertanyaan"],data["jawaban"],)
                    cur.execute(sql,val)
                    mydb.connection.commit()
                    cur.close()
                except Exception as e:
                    message = "error database : " + str(e)
        else :
            message = "no user id detected"
    return jsonify({"message":message})


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
                with app.app_context():
                    try:
                        cursor = mydb.connection.cursor()
                        cursor.execute("INSERT INTO data(pertanyaan,jawaban) VALUES(\"{}\",\"{}\")".format(matches1[0],matches2[0]))
                        mydb.connection.commit()
                        cursor.close()
                        response="terimakasih inputan datanya :)"
                    except Exception as e:
                        response="error in insertion : " + str(e)
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

@app.route('/admin/listdata',methods=['GET'])
def listdata():
    return render_template('admin/listdata.html')

@app.route('/admin/listuser',methods=['GET'])
def listuser():
    return render_template('admin/listuser.html')