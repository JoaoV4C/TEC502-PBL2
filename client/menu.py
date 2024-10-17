#servidor_logado = None # Variável global para armazenar o servidor lgoado

def login():
    global servidor_logado
    while True:
        print("\nEscolha o servidor para fazer login:")
        print("1. Servidor 1")
        print("2. Servidor 2")
        print("3. Sair")
        opcao = input("Digite sua opção (1/2/3): ")
        if opcao in ['1', '2']:
            username = input("Digite o nome de usuário: ").strip()
            cpf = input("Digite o CPF: ")
            return opcao, username, cpf
        elif opcao == '3':
            print("Saindo...")
            servidor_logado = None
            return None, None, None
        else:
            print("Opção inválida! Tente novamente.\n")
    
def opcoes():
    print("\nO que você gostaria de fazer?")
    print("1. Comprar passagem")
    print("2. Listar passagens")
    print("3. Logout")
    
    opcao = input("Digite sua opção (1/2/3): ")
    
    if opcao == '1':
        return 'comprar_passagem'
    
    elif opcao == '2':
        return 'listar_passagens'
    
    elif opcao == '3':
        print("Fazendo logout...")
        servidor_logado = None
        return 'logout'
    
    else:
        print("Opção inválida! Tente novamente.")

def comprar_passagem():
    print("comprar passagem\n")
    
def listar_passagens():
    print("listar passagem\n")