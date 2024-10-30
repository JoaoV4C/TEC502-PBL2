from flask import Flask, jsonify, request
import requests
from mocks.mocksServer2 import *
from models.passager import Passager
from models.ticket import Ticket
from models.airport import Airport
from models.flight import Flight

app = Flask(__name__)

# Rotas disponíveis no servidor 2
airport_list = []

usuarios_logados = {}

@app.route('/login', methods=["POST"])
def login():
    data = request.json
    username = data.get('username')
    cpf = data.get("cpf")
    if username and cpf:
        passager = Passager(username, cpf)
        usuarios_logados[cpf] = passager
        return jsonify({"mensagem": "Login bem-sucedido", "cpf": cpf }), 200
    else:
        return jsonify({"mensagem": "Credenciais inválidas!",}), 200


@app.route('/cidades', methods=["GET"])
def cidades():
    # Mostrar só as cidades disponiveis para viagem
    cidades_disponiveis = [aeroporto.name for aeroporto in airport_list]
    # Retorna a lista de cidades em formato JSON
    return jsonify({"Cidades": cidades_disponiveis}), 200

# Armazena dados de sessão temporariamente
session_data = {}    

@app.route('/confirmar_compra', methods=["POST",])
def confirmar_compra():
    dados = request.json
    confirmacao = dados.get('confirmacao')
    cpf_cliente = request.headers.get("Cliente-cpf") # Recebe o CPF para identificação
    if not confirmacao:
        return jsonify({"mensagem": "Confirmação não fornecida!"}), 400
    if cpf_cliente not in session_data:
        return jsonify({"mensagem": "Cliente não encontrado na sessão!"}), 404
    cliente_data = session_data.pop(cpf_cliente) # Recupera e remove os dados do cliente
    flights_needed = cliente_data["flights_needed"]

    if cpf_cliente in usuarios_logados:    
        print("Teste")
        passager = usuarios_logados[cpf_cliente]
        print(passager)
        send_client = reserve_flight(passager, flights_needed)
        return jsonify({'mensagem': 'Compra confirmada com sucesso!'}), 200
    return jsonify({"mensagem": "Erro ao confirmar compra!"}), 500

@app.route('/comprar_passagem', methods=['POST'])
def comprar_passagem():
    # Verifica se a requisição veio de um cliente ou outro servidor
    remetente = request.headers.get('From', 'desconhecido')
    cpf_cliente = request.headers.get("Cliente-cpf") # Recebe o CPF do cliente
    
    
    if remetente == 'cliente':
        dados = request.json
        origem = dados.get("origem")
        destino = dados.get("destino")
        
        possible_routes = find_routes(airport_list, origem, destino)
        
        if not possible_routes:
            return jsonify({"mensagem": "Nenhuma rota disponível entre os destinos fornecidos.",}), 404
        else:
            best_route = get_best_route(possible_routes)
            flights_needed = list_flights_needed(best_route)
            
            # Armazena dados temporários do cliente
            session_data[cpf_cliente]={
                'origem': origem,
                'destino': destino,
                'best_route': best_route,
                'flights_needed': flights_needed,
            }
            
            
            response_data = {
                "mensagem": "Melhor rota encontrada.",
                "melhor_rota": best_route,
                "voos_necessarios": [flight.__dict__ for flight in flights_needed]  # Converte para dicionário
            }
            return jsonify(response_data), 200
            

    else:
        print(f"Requisição recebida de {remetente}.")
    
    # Fazer requisição para o Servidor 1 para obter as rotas dele
    try:
        response = requests.get('http://127.0.0.1:5000/obter_rotas', headers={'From': 'servidor'})
        if response.status_code == 200:
            rotas_servidor1 = response.json().get("rotas", [])
            return jsonify({
                "mensagem": "Compra processada.",
                "remetente": remetente,  # Informar quem enviou a requisição
                "rotas_servidor2": rotas,
                "rotas_servidor1": rotas_servidor1
            }), 200
        else:
            return jsonify({"mensagem": "Erro ao chamar o Servidor 1", "status": response.status_code}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"mensagem": f"Erro na requisição ao Servidor 1: {e}"}), 500

@app.route('/obter_rotas', methods=['GET'])
def obter_rotas():
    # Verifica o remetente da requisição
    remetente = request.headers.get('from', 'desconhecido')
    if remetente == 'cliente':
        print('Requisição de listagem de rotas recebida do cliente.\n')
    else:
        print(f'Requisição de listagem de rotas recebida de {remetente}.\n')
    return jsonify({"rotas": rotas_servidor2, "remetente": remetente}), 200

# Rota para mostrar os usuários online
@app.route('/usuarios_online', methods=['GET'])
def usuarios_online():
    if usuarios_logados:
        return jsonify({"usuarios_online": usuarios_logados}), 200
    else:
        return jsonify({"mensagem": "Nenhum usuário online no momento"}), 200


# Encontra as rotas possíveis entre a origem e o destino
def find_routes(airports, origin, destination, current_route=None, possible_routes=None):
    if current_route is None:
        current_route = [origin]  # Inicializa a rota atual com o aeroporto de origin
    if possible_routes is None:
        possible_routes = []   # Inicializa a lista de rotas possíveis encontradas

    # Se a cidade atual na rota é o destination, adiciona a rota atual às rotas possíveis
    if origin == destination:
        possible_routes.append(list(current_route))
        return possible_routes

    # Encontra o objeto Airport correspondente à cidade de origin
    current_airport = next((airport for airport in airports if airport.name == origin), None)
    if not current_airport:
        return possible_routes  # Retorna se o aeroporto de origin não existe

    # Explora cada cidade adjacente (conectada) ao aeroporto de origin
    for prox_cidade in current_airport.connections:
        if prox_cidade not in current_route:  # Evita ciclos
            current_route.append(prox_cidade)  # Adiciona a próxima cidade à rota atual
            find_routes(airports, prox_cidade, destination, current_route, possible_routes)  # Busca recursiva
            current_route.pop()  # Remove a última cidade após explorar para permitir outras rotas

    possible_routes.sort(key=len)

    return possible_routes

# Retorna a melhor rota dentre as possíveis
def get_best_route(possible_routes):
    if len(possible_routes) == 0:
        return []
    return possible_routes[0]


def reserve_flight(passager, flights):
    """
    Reserva os voos necessários para o passageiro.

    Args:
        passager: O passageiro que está reservando os voos.
        flights: Lista de voos a serem reservados.

    Returns:
        bool: True se todos os voos foram reservados, False caso contrário.
    """
    
    all_reserved = True
    for flight in flights:
        if flight.available_seats == 0:
            all_reserved = False
            break

    # Se todos os voos tiverem assentos disponíveis, reserva-os e cria um ticket para o passager
    if all_reserved:
        for flight in flights:
            print(f"Passager: {passager.name} - Reservation made successfully for the flight {flight.place_from} --> {flight.place_to}")
            flight.reserve_seat()
            ticket = Ticket(passager.id, flight._id, flight._place_from, flight._place_to)
            passager.add_ticket(ticket)

    return all_reserved

# Cria a lista de voos necessários para a rota
def list_flights_needed(best_route):
    flights_needed = []
    for i in range(len(best_route) - 1):
        for flight in flights_list:
            if flight.place_from == best_route[i] and flight.place_to == best_route[i + 1]:
                flights_needed.append(flight)
    return flights_needed

# Cria a lista de aeroportos
def list_citys(airport_list):
    citys = []
    for airport in airport_list:
        citys.append(airport.name)
    return citys

# Encontra o passager pelo CPF
def find_passager(cpf):
    for passager in passager_list:
        if passager.cpf == cpf:
            return passager
    return None

if __name__ == '__main__':
    airport_list = create_airports()
    flights_list = create_flights(airport_list)
    app.run(port=5001)
