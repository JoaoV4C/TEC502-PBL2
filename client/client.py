import requests

def fazer_requisicao_servidor1():
    try:
        response = requests.get('http://127.0.0.1:5000/obter_rotas', headers={'From': 'cliente'})
        if response.status_code == 200:
            print("Resposta do Servidor 1:")
            print(response.json())
        else:
            print(f"Erro ao chamar o Servidor 1: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição ao Servidor 1: {e}")

def fazer_requisicao_servidor2():
    try:
        response = requests.get('http://127.0.0.1:5001/obter_rotas', headers={'From': 'cliente'})
        if response.status_code == 200:
            print("Resposta do Servidor 2:")
            print(response.json())
        else:
            print(f"Erro ao chamar o Servidor 2: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição ao Servidor 2: {e}")

def main():
    while True:
        print("\nEscolha o servidor para fazer a requisição:")
        print("1. Servidor 1")
        print("2. Servidor 2")
        print("3. Sair")
        
        opcao = input("Digite sua opção (1/2/3): ")
        
        if opcao == '1':
            fazer_requisicao_servidor1()
        elif opcao == '2':
            fazer_requisicao_servidor2()
        elif opcao == '3':
            print("Saindo...")
            break
        else:
            print("Opção inválida! Tente novamente.")

if __name__ == '__main__':
    main()
