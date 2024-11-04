import os
import json
import requests
from flask import Flask, flash, jsonify, request, render_template, redirect, url_for
from flask_login import UserMixin, login_required, login_user, logout_user, LoginManager, current_user

#Constantes para configuração do servidor
SERVER_NUMBER = 1
SERVER_PORT = 5000
OTHER_SERVERS_NUMBER = [2, 3]
OTHER_SERVERS_PORTS = [5001, 5002]

#Caminho para os arquivos JSON
PATH = f"../app/data/server{SERVER_NUMBER}/"

#Configuração variáveis do Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = f'secret{SERVER_NUMBER}'
app.config['SESSION_COOKIE_NAME'] = f'session_server{SERVER_NUMBER}'

#Configuração do LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Classe User para armazenar os dados do usuário logado
class User(UserMixin):
    def __init__(self, id, name, cpf):
        self.id = id
        self.name = name
        self.cpf = cpf

#Função para carregar o usuário logado
@login_manager.user_loader
def load_user(user_id):
    if os.path.exists(f'{PATH}/passagers.json'):
        with open(f'{PATH}/passagers.json', 'r', encoding='utf-8') as file:
            passagers = json.load(file)
        #Procura o usuário pelo id e retorna um objeto User
        for passager in passagers:
            if passager['id'] == int(user_id):
                return User(passager['id'], passager['name'], passager['cpf'])
    return None

#Rota para realizar o login do usuário e criar a sessão
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        cpf = request.form.get("cpf")
        if os.path.exists(f'{PATH}/passagers.json'):
            with open(f'{PATH}/passagers.json', 'r', encoding='utf-8') as file:
                passagers = json.load(file)
            #Procura o usuário pelo cpf e cria a sessão
            for passager in passagers:
                if passager['cpf'] == cpf:
                    user = User(passager['id'], passager['name'], passager['cpf'])
                    login_user(user)
                    return redirect(url_for('index'))
                    
        return render_template("login.html", error="CPF não encontrado.")
        
    return render_template("login.html")

#Rota para realizar o logout do usuário e encerrar a sessão
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#Rota para cadastrar um novo usuário
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
        else:
            passagers = [{"id": 1, "name": name, "cpf": cpf}]
 
        with open(f'{PATH}/passagers.json', 'w', encoding='utf-8') as file:
            json.dump(passagers, file, ensure_ascii=False)

        return redirect(url_for('login'))
        
    return render_template("register.html")

#Rota principal da aplicação
@app.route('/', methods=["GET"])
@login_required
def index():
    #Retorna a página home.html com os voos disponíveis
    return render_template("home.html", flights = get_all_flights())

#Rota para exibir os voos disponíveis  
@app.route('/flights', methods=["GET"])
def get_flights():
    if os.path.exists(f'{PATH}/flights.json'):
        with open(f'{PATH}/flights.json', 'r', encoding='utf-8') as file:
            flights = json.load(file)
        #Adiciona o número do servidor ao voo para identificação
        for flight in flights:
            flight['server'] = SERVER_NUMBER
        return flights
    return []

#Rota para filtrar os voos com base no local de origem e destino
@app.route('/filter-flights', methods=["POST"])
@login_required
def filter_flights():
    #Obtém os locais de origem e destino do formulário e filtra os voos
    place_from = request.form.get("place_from")
    place_to = request.form.get("place_to")
    flights = get_all_flights(place_from, place_to)
    return render_template("home.html", flights = flights)

#Rota para exibir os voos comprados pelo usuário logado
@app.route("/my-flights", methods=["GET"])
@login_required
def my_flights():
    my_flights = []
    if os.path.exists(f'{PATH}/tickets.json'):
        with open(f'{PATH}/tickets.json', 'r', encoding='utf-8') as file:
            flights = json.load(file)
        #Filtra os voos comprados pelo usuário logado
        my_flights = [flight for flight in flights if flight['passager_id'] == current_user.id]
    return render_template("my-flights.html", flights=my_flights)

# Função para preparar a transação nos outros servidores
def prepare_transaction(flight_id, server):
    response = {}
    if server == SERVER_NUMBER:
        request_response = requests.post(f'http://127.0.0.1:{SERVER_PORT}/prepare/{flight_id}', timeout=0.5)
        response = request_response.json()
    else :
        index = OTHER_SERVERS_NUMBER.index(server)
        response = requests.post(f'http://127.0.0.1:{OTHER_SERVERS_PORTS[index]}/prepare/{flight_id}', timeout=0.5)
        response = response.json()

    return response['status'] == 'prepared'

# Função para confirmar a transação nos outros servidores
def commit_transaction(flight_id, server):
    if server == SERVER_NUMBER:
        request = requests.post(f'http://127.0.0.1:{SERVER_PORT}/commit/{flight_id}', timeout=0.5)
        return request.json()["flight"]
    else:
        index = OTHER_SERVERS_NUMBER.index(server)
        request = requests.post(f'http://127.0.0.1:{OTHER_SERVERS_PORTS[index]}/commit/{flight_id}', timeout=0.5)
        return request.json()["flight"]

# Função para abortar a transação nos outros servidores
def abort_transaction(server):
    if server == SERVER_NUMBER:
        abort()
    else:
        index = OTHER_SERVERS_NUMBER.index(server)
        try:
            requests.post(f'http://127.0.0.1:{OTHER_SERVERS_PORTS[index]}/abort', timeout=0.5)
        except requests.exceptions.RequestException as e:
            print(f"Ocorreu um erro na requisição ao servidor {OTHER_SERVERS_NUMBER[index]}: {e}")

# Processo coordenador para comprar um ticket
@app.route('/buy-ticket/<int:flight_id>', methods=['POST'])
def buy_ticket(flight_id):
    server = request.args.get('server', type=int)
    try:
        # Fase de Preparação
        if prepare_transaction(flight_id, server):
            flight = commit_transaction(flight_id,server)
            create_ticket(flight_id, flight, server)
            flash(f"Ticket bought successfully!")
        else:
            abort_transaction(server)
            flash("Purchase failed. There are no more available seats.")

    except requests.exceptions.Timeout:
        flash(f"Error when trying to buy ticket, server {server} is not responding")
        print(f"A requisição ao servidor {server} excedeu o tempo limite.")

    except requests.exceptions.RequestException as e:
        flash(f"Unknown error when trying to buy ticket")
        print(f"Ocorreu um erro na requisição ao servidor {server}: {e}")

    return redirect(url_for('index'))

def create_ticket(flight_id, flight, server):
    ticket = {
        "id": 1,
        "passager_id": current_user.id,
        "flight_id": flight_id,
        "place_from": flight["place_from"],
        "place_to": flight["place_to"],
        "server": server
    }
    if os.path.exists(f'{PATH}/tickets.json'):
        with open(f'{PATH}/tickets.json', 'r', encoding='utf-8') as file:
            tickets = json.load(file)
            ticket["id"] = tickets[-1]["id"] + 1
            tickets.append(ticket)
    else:
        tickets = [ticket]
    with open(f'{PATH}/tickets.json', 'w', encoding='utf-8') as file:
        json.dump(tickets, file, ensure_ascii=False)

# Rota para preparar a transação
@app.route('/prepare/<int:flight_id>', methods=['POST'])
def prepare(flight_id):
    flight = get_flight_by_id(flight_id)
    if flight and flight['available_seats'] > 0:
        return jsonify({'status': 'prepared'})
    else:
        return jsonify({'status': 'abort'})

# Rota para confirmar a transação
@app.route('/commit/<int:flight_id>', methods=['POST'])
def commit(flight_id):
    if os.path.exists(f'{PATH}/flights.json'):
        with open(f'{PATH}/flights.json', 'r', encoding='utf-8') as file:
            flights = json.load(file)
            
    flight = next((flight for flight in flights if flight['id'] == flight_id), None)
    if flight:
        flight['available_seats'] -= 1
        with open(f'{PATH}/flights.json', 'w', encoding='utf-8') as file:
            json.dump(flights, file, ensure_ascii=False)
        return jsonify({'status': 'committed', "flight": flight})
    return jsonify({'status': 'error'})

# Rota para abortar a transação
@app.route('/abort', methods=['POST'])
def abort():
    # Não é necessário fazer nada aqui, pois a transação foi abortada
    return jsonify({'status': 'aborted'})

@app.route('/get_flight_by_id/<int:flight_id>', methods=['GET'])
def get_flight_by_id(flight_id):
    if os.path.exists(f'{PATH}/flights.json'):
        with open(f'{PATH}/flights.json', 'r', encoding='utf-8') as file:
            flights = json.load(file)
        for flight in flights:
            if flight['id'] == flight_id:
                return flight
    return []

#Função para obter os voos dos outros servidores
def get_other_servers_flights():
    response = []
    #Realiza a requisição para os outros servidores e adiciona os voos na lista de resposta
    for i in range(2):
        try:
            request_response = requests.get(f'http://127.0.0.1:{OTHER_SERVERS_PORTS[i]}/flights', timeout=0.5)
            request_response.raise_for_status()  # Levanta uma exceção para códigos de status HTTP de erro
            response.extend(request_response.json())
        except requests.exceptions.Timeout:
            print(f"A requisição ao servidor {OTHER_SERVERS_NUMBER[i]} excedeu o tempo limite.")
        except requests.exceptions.RequestException as e:
            print(f"Ocorreu um erro na requisição ao servidor {OTHER_SERVERS_NUMBER[i]}: {e}")

    return response

#Função para obter todos os voos
def get_all_flights(place_from=None, place_to=None):
    #Obtém os voos do servidor atual e dos outros servidores
    flights = get_flights()
    other_server_flights = get_other_servers_flights()
    flights.extend(other_server_flights)
    if place_from and place_to:
        flights = [flight for flight in flights if flight['place_from'].lower() == place_from.lower() and flight['place_to'].lower() == place_to.lower()]
    return flights

# #Rota para alocar um assento em um voo
# @app.route('/allocate-seat/<int:id>', methods=["POST"])
# def allocate_seat(id):
#     if os.path.exists(f'{PATH}/flights.json'):
#         with open(f'{PATH}/flights.json', 'r', encoding='utf-8') as file:
#             flights = json.load(file)
#         for flight in flights:
#             #Verifica se o voo possui assentos disponíveis e aloca um assento
#             if flight['id'] == id:
#                 if flight['available_seats'] > 0:
#                     flight['available_seats'] -= 1
#                     with open(f'{PATH}/flights.json', 'w', encoding='utf-8') as file:
#                         json.dump(flights, file, ensure_ascii=False)
#                     return flight
#     return []

# #Rota para comprar um ticket
# @app.route('/buy-ticket/<int:id>', methods=["POST"])
# @login_required
# def buy_ticket(id):
#     server = request.args.get('server', type=int)
#     try:
#         #Verifica qual o servidor do voo e realiza a solicitação de alocar um assento
#         if server == SERVER_NUMBER:
#             flight = allocate_seat(id)
#         elif server == OTHER_SERVERS_NUMBER[0]:
#             response = requests.post(f'http://127.0.0.1:{OTHER_SERVERS_PORTS[0]}/allocate-seat/{id}', timeout=0.5)
#             flight = response.json()
#         elif server == OTHER_SERVERS_NUMBER[1]:
#             response = requests.post(f'http://127.0.0.1:{OTHER_SERVERS_PORTS[1]}/allocate-seat/{id}', timeout=0.5)
#             flight = response.json()
#         #Verifica se o assento foi alocado com sucesso e cria o ticket
#         if flight:
#             if os.path.exists(f'{PATH}/tickets.json'):
#                 with open(f'{PATH}/tickets.json', 'r', encoding='utf-8') as file:
#                     tickets = json.load(file)
#                     tickets.append({"id":tickets[-1]["id"] + 1,"passager_id": current_user.id, "flight_id": id,"place_from": flight["place_from"],"place_to": flight["place_to"] ,"server": server})
#             else:
#                 tickets = [{"id": 1 ,"passager_id": current_user.id, "flight_id": id,"place_from": flight["place_from"],"place_to": flight["place_to"] ,"server": server}]
#             #Salva o ticket em um arquivo JSON
#             with open(f'{PATH}/tickets.json', 'w', encoding='utf-8') as file:
#                 json.dump(tickets, file, ensure_ascii=False)
#             flash(f"Ticket bought successfully! Flight from {flight['place_from']} to {flight['place_to']}")
#         else:
#             flash("Purchase failed. There are no more available seats.")
#     #Tratamento de exceções
#     except requests.exceptions.Timeout:
#         flash(f"Error when trying to buy ticket, server {server} is not responding")
#         print(f"A requisição ao servidor {server} excedeu o tempo limite.")
#     except requests.exceptions.RequestException as e:
#         flash(f"Unknown error when trying to buy ticket")
#         print(f"Ocorreu um erro na requisição ao servidor {server}: {e}")
    
#     return redirect(url_for('index'))

    
if __name__ == '__main__':
    app.run(port=SERVER_PORT, debug=True)