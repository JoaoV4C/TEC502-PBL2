import requests
from menu import login, opcoes, comprar_passagem, listar_passagens

servidor_logado = None
def login_servidor1(username, cpf):
    global servidor_logado
    try:
        response = requests.post('http://127.0.0.1:5000/login', json = {'username': username, 'cpf': cpf})
        if response.status_code == 200:
            print("Resposta do Servidor 1:")
            servidor_logado = 1
        else:
            print(f"Erro ao fazer login no Servidor 1: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição ao Servidor 1: {e}")

def login_servidor2():
    global servidor_logado
    try:
        response = requests.get('http://127.0.0.1:5001/login', json = {'username': username, 'cpf': cpf})
        if response.status_code == 200:
            print("Resposta do Servidor 2:")
            servidor_logado = 2
        else:
            print(f"Erro ao fazer login no Servidor 2: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição ao Servidor 2: {e}")
        


def main():
    opcao, username, cpf = login()
    if opcao == '1':
        login_servidor1(username, cpf)
    elif opcao == "2":
        login_servidor2(username, cpf)
    while servidor_logado:
        acao = opcoes()
        if acao == 'comprar_passagem':
            comprar_passagem()
        elif acao == "listar_passagens":
            listar_passagens()
        elif acao == 'logout':
            break

if __name__ == '__main__':
    main()
