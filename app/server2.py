import os
import json
import requests
from flask import Flask, request, render_template, redirect, url_for
from flask_login import UserMixin, login_required, login_user, logout_user, LoginManager, current_user

PATH = "../app/data/server2/"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret2'
app.config['SESSION_COOKIE_NAME'] = 'session_server2'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, name, cpf):
        self.id = id
        self.name = name
        self.cpf = cpf
    
@login_manager.user_loader
def load_user(user_id):
    if os.path.exists(f'{PATH}/passagers.json'):
        with open(f'{PATH}/passagers.json', 'r', encoding='utf-8') as file:
            passagers = json.load(file)
        for passager in passagers:
            if passager['id'] == int(user_id):
                return User(passager['id'], passager['name'], passager['cpf'])
    return None

@app.route('/', methods=["GET"])
@login_required
def index():
    return render_template("home.html", flights = get_all_flights())

@app.route('/filter-flights', methods=["POST"])
@login_required
def filter_flights():
    place_from = request.form.get("place_from")
    place_to = request.form.get("place_to")
    flights = get_all_flights(place_from, place_to)
    return render_template("home.html", flights = flights)

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        cpf = request.form.get("cpf")
        if os.path.exists(f'{PATH}/passagers.json'):
            with open(f'{PATH}/passagers.json', 'r', encoding='utf-8') as file:
                passagers = json.load(file)
                
            for passager in passagers:
                if passager['cpf'] == cpf:
                    user = User(passager['id'], passager['name'], passager['cpf'])
                    login_user(user)
                    return redirect(url_for('index'))
                    
        return render_template("login.html", error="CPF não encontrado.")
        
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=["POST","GET"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        cpf = request.form.get("cpf")

        if os.path.exists(f'{PATH}/passagers.json'):
            with open(f'{PATH}/passagers.json', 'r', encoding='utf-8') as file:
                passagers = json.load(file)

            for passager in passagers:
                if passager['cpf'] == cpf:
                    return render_template("register.html", error="CPF já cadastrado!")

            new_passager = {"id": passagers[-1]["id"] + 1,"name": name, "cpf": cpf}
            passagers.append(new_passager)
        # Adicionar novo passageiro
        else:
            passagers = [{"id": 1, "name": name, "cpf": cpf}]
 
        with open(f'{PATH}/passagers.json', 'w', encoding='utf-8') as file:
            json.dump(passagers, file, ensure_ascii=False)

        return redirect(url_for('login'))
        
    return render_template("register.html")

@app.route('/flights', methods=["GET"])
def get_flights():
    if os.path.exists(f'{PATH}/flights.json'):
        with open(f'{PATH}/flights.json', 'r', encoding='utf-8') as file:
            flights = json.load(file)
        for flight in flights:
            flight['server'] = 2
        return flights
    return []

@app.route('/allocate-seat/<int:id>', methods=["POST"])
def allocate_seat(id):
    if os.path.exists(f'{PATH}/flights.json'):
        with open(f'{PATH}/flights.json', 'r', encoding='utf-8') as file:
            flights = json.load(file)
        for flight in flights:
            if flight['id'] == id:
                flight['available_seats'] -= 1
                with open(f'{PATH}/flights.json', 'w', encoding='utf-8') as file:
                    json.dump(flights, file, ensure_ascii=False)
                return flight
    return None

@app.route('/buy-ticket/<int:id>', methods=["POST"])
@login_required
def buy_ticket(id):
    server = request.args.get('server', type=int)
    try:
        if server == 2:
            flight = allocate_seat(id)
        elif server == 1:
            response = requests.post(f'http://127.0.0.1:5000/allocate-seat/{id}', timeout=0.5)
            flight = response.json()
        elif server == 3:
            response = requests.get(f'http://127.0.0.1:5002/allocate-seat/{id}', timeout=0.5)
            flight = response.json()

        if os.path.exists(f'{PATH}/tickets.json'):
            with open(f'{PATH}/tickets.json', 'r', encoding='utf-8') as file:
                tickets = json.load(file)
                tickets.append({"id":tickets[-1]["id"] + 1,"passager_id": current_user.id, "flight_id": id,"place_from": flight["place_from"],"place_to": flight["place_to"] ,"server": server})
        else:
            tickets = [{"id": 1 ,"passager_id": current_user.id, "flight_id": id,"place_from": flight["place_from"],"place_to": flight["place_to"] ,"server": server}]

        with open(f'{PATH}/tickets.json', 'w', encoding='utf-8') as file:
            json.dump(tickets, file, ensure_ascii=False)

    except requests.exceptions.Timeout:
        print(f"A requisição ao servidor {server} excedeu o tempo limite.")
    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro na requisição ao servidor {server}: {e}")
    
    return redirect(url_for('index'))

def get_other_servers_flights():
    response = []
    try:
        response_server1 = requests.get('http://127.0.0.1:5000/flights', timeout=0.5)
        response_server1.raise_for_status()  # Levanta uma exceção para códigos de status HTTP de erro
        response.extend(response_server1.json())
    except requests.exceptions.Timeout:
        print("A requisição ao servidor 1 excedeu o tempo limite.")
    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro na requisição ao servidor 1: {e}")
    
    try:
        response_server3 = requests.get('http://127.0.0.1:5002/flights', timeout=0.5)
        response_server3.raise_for_status()  # Levanta uma exceção para códigos de status HTTP de erro
        response.extend(response_server3.json())
    except requests.exceptions.Timeout:
        print("A requisição ao servidor 3 excedeu o tempo limite.")
    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro na requisição ao servidor 3: {e}")

    return response

def get_all_flights(place_from=None, place_to=None):
    flights = get_flights()
    other_server_flights = get_other_servers_flights()
    flights.extend(other_server_flights)
    if place_from and place_to:
        flights = [flight for flight in flights if flight['place_from'].lower() == place_from.lower() and flight['place_to'].lower() == place_to.lower()]
    return flights

@app.route("/my-flights", methods=["GET"])
@login_required
def my_flights():
    my_flights = []
    if os.path.exists(f'{PATH}/tickets.json'):
        with open(f'{PATH}/tickets.json', 'r', encoding='utf-8') as file:
            flights = json.load(file)
        my_flights = [flight for flight in flights if flight['passager_id'] == current_user.id]
    return render_template("my-flights.html", flights=my_flights)
    
if __name__ == '__main__':
    app.run(port=5001, debug=True)
