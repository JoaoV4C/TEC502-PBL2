from menu import login, opcoes, comprar_passagem, listar_passagens, choose_server
import requests

SERVERS_PORTS = [5000, 5001]
servidor_logado = None

def login_servidor(username, cpf, server):
    global servidor_logado
    try:
        response = requests.post(f'http://127.0.0.1:{SERVERS_PORTS[server-1]}/login', json = {'username': username, 'cpf': cpf})
        if response.status_code == 200:
            print(f"Resposta do Servidor {server}:")
            servidor_logado = server
        else:
            print(f"Erro ao fazer login no Servidor {server}: {response.status_code}")
    except requests.exceptions.RequestException:
        print(f"Erro na requisição ao Servidor {server} ")
  
def main():
    opcao = choose_server()
    if opcao in ['1', '2', '3']:
        login_servidor(username, cpf, int(opcao))
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