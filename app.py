from flask import Flask, request, render_template, redirect, url_for, session
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = "chave_super_secreta"

# Acessa as variáveis de ambiente
DELETE_PASSWORD = os.getenv("DELETE_PASSWORD")
MONGO_URI = os.getenv("MONGO_URI")
ACCESS_PASSWORD = os.getenv("ACCESS_PASSWORD")


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ACCESS_PASSWORD:
            session["authenticated"] = True
            return redirect(url_for("index"))
        else:
            return "<h2 style='color: red; font-size: 250px;'>No no no no 🤪!</h2>"

    return render_template("login.html")

# Conecta ao MongoDB
client = MongoClient(MONGO_URI)
db = client["db_1"]
collection = db["clientes"]

@app.route("/index")
def index():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template("index.html", clients=[])

@app.route("/logout")
def logout():
    session.pop("authenticated", None)
    return redirect(url_for("login"))

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    rg = request.form['rg']
    cpf = request.form['cpf']
    tel = request.form['tel']
    address = request.form['address']
    collection.insert_one({"name": name, "rg": rg, "cpf": cpf, "tel": tel , "address": address})
    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search():
    name = request.form['search_name']
    clients = list(collection.find({"name": {"$regex": name, "$options": "i"}}))
    return render_template('index.html', clients=clients)

@app.route('/delete/<id>')
def delete(id):
    password = request.args.get("password")
    if password == DELETE_PASSWORD:
        collection.delete_one({"_id": ObjectId(id)})
        return redirect(url_for('index'))
    return "<h2 style='color: red; font-size: 250px;'>No no no no...🤪</h2>", 403

if __name__ == '__main__':
    app.run(debug=False)
