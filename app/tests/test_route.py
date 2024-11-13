import requests
import concurrent.futures

# Configurações
SERVER_URLS = ['http://127.0.0.1:9000', 'http://127.0.0.1:9001', 'http://127.0.0.1:9002']
FLIGHT_ID = 1  # ID do voo que será testado
NUM_REQUESTS = 1500  # Número de requisições simultâneas

# Função para registrar um usuário
def register_user(server_url, user_id):
    register_data = {'name': f'User{user_id}', 'cpf': f'123{user_id}'}
    response = requests.post(f'{server_url}/register', data=register_data)
    return response.status_code == 200

# Função para autenticar um usuário
def authenticate_user(server_url, user_id):
    login_data = {'cpf': f'123{user_id}'}
    session = requests.Session()
    response = session.post(f'{server_url}/login', data=login_data)
    return session if response.status_code == 200 else None

# Função para enviar uma requisição de compra de passagem
def buy_ticket(session, server_url, user_id):
    try:
        response = session.post(f'{server_url}/buy-ticket/{FLIGHT_ID}', params={'server': 1}, timeout=1)
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Request failed for user {user_id} on server {server_url}: {e}"

# Função principal para executar o teste de concorrência
def main():
    # Registrar um usuário por servidor
    for server_url in SERVER_URLS:
        register_user(server_url, 1)

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_REQUESTS) as executor:
        futures = []
        for i in range(NUM_REQUESTS):
            server_url = SERVER_URLS[i % len(SERVER_URLS)]
            # Autenticar o usuário
            session = authenticate_user(server_url, 1)
            if session:
                futures.append(executor.submit(buy_ticket, session, server_url, 1))
            else:
                print(f"Failed to authenticate user 1 on server {server_url}")
        for future in concurrent.futures.as_completed(futures):
            print(future.result())

if __name__ == '__main__':
    main()