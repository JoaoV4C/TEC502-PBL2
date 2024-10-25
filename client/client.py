import requests
from menu import login, menu, buy_ticket, listar_passagens

servidor_logado = None
def login_servidor1(username, cpf):
    global servidor_logado
    try:
        response = requests.post('http://127.0.0.1:5000/login', json = {'username': username, 'cpf': cpf})
        if response.status_code == 200:
            print("Resposta do Servidor 1: Login realizado com sucesso.")
            servidor_logado = 1
        else:
            print(f"Erro ao fazer login no Servidor 1: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição ao Servidor 1: {e}")

def login_servidor2(username, cpf):
    global servidor_logado
    try:
        response = requests.post('http://127.0.0.1:5001/login', json = {'username': username, 'cpf': cpf})
        if response.status_code == 200:
            print("Resposta do Servidor 2: Login realizado com sucesso.")
            servidor_logado = 2
        else:
            print(f"Erro ao fazer login no Servidor 2: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição ao Servidor 2: {e}")
        
        
def comprar_passagem():
    try:
        headers = {'From':'cliente'}
        if servidor_logado == 1:
            response = requests.get('http://127.0.0.1:5000/cidades', headers=headers)
        elif servidor_logado == 2:
            response = requests.get('http://127.0.0.1:5001/cidades', headers=headers)
        
        if response.status_code == 200:
            # Obetem a lista de cidades
            cidades = response.json().get("Cidades", [])
            # Verifica se a lista de cidades não está vazia
            if cidades:
                print("\nCidades disponíveis para compra de passagem:")
                for idx, cidade in enumerate(cidades, start=1):
                    print(f"{idx}. {cidade}")
            else:
                print("Nenhuma cidade disponível no momento.\n")
                
            origem, destino = buy_ticket()
            ticket_data = {'origem': origem, 'destino': destino}
            
            if servidor_logado == 1:
                response = requests.post('http://127.0.0.1:5000/comprar_passagem', json=ticket_data, headers=headers)
            elif servidor_logado == 2:
                response = requests.post('http://127.0.0.1:5001/comprar_passagem', json=ticket_data, headers = headers)
                
                if response.status_code == 200:
                    resposta_json = response.json()
                    melhor_rota = resposta_json.get('melhor_rota')
                    if melhor_rota:
                        print("Melhor rota encontrada:")
                        print("Cidades:", ", ".join(melhor_rota))  # Exibe as cidades da melhor rota
                                    # Exibir os voos necessários
                    voos_necessarios = resposta_json.get("voos_necessarios", [])
                    if voos_necessarios:
                        print("\nVoos necessários:")
                        for voo in voos_necessarios:
                            print(f'Origem: {voo['_place_from']} --> destino: {voo['_place_to']}')
                        
                elif response.status_code == 404:
                    print("Erro: Nenhuma rota disponível.")  
        
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
    ...
        
def listar_passagens():
    
    ...


def run_client():
    logged = False
    while not logged:
        opclogin, username, cpf = login()
        
        match opclogin:
            case '1':
                print("Servidor 1\n")
                login_servidor1(username, cpf)
                logged = True
            case '2':
                print("Servidor 2\n")
                login_servidor2(username,cpf)
                logged = True
            case '3':
                print("Encerrando o cliente...\n")
                return
    
    while logged:
        opcao = menu(username)
        print("to aqui ???")
        match opcao:
            case "1":
                comprar_passagem()
            case "2":
                listar_passagens()
            case "3":
                logged = False
                return print("Logout realizado.")
            case _:
                print("Opção inválida! Tente novamente.")
                
    ...

if __name__ == '__main__':
    run_client()
