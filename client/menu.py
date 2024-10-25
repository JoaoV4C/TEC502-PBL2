#servidor_logado = None # Variável global para armazenar o servidor lgoado

def login():
    while True:
        print("\nEscolha o servidor para fazer login:")
        print("1. Servidor 1")
        print("2. Servidor 2")
        print("3. Sair")
        opcao = input("Digite sua opção (1/2/3): ").strip()
        match opcao:
            case '1'| '2':
                username = input("Digite o nome de usuário: ").strip()
                cpf = input("Digite o CPF: ").strip()
                return opcao, username, cpf
            case '3':
                return '3', None, None
            case _:
                print("Opção inválida! Tente novamente. \n")
            
def menu(username):
    print(f"""Hi {username}, Welcome To The Fast Pass Company!!
    1 - Buy Ticket
    2 - List your tickets
    3 - Logout""")
    option = input("Choose an option: ")
    return option    


def buy_ticket():
    origem = input("Digite a cidade origem: ")
    destino = input("Digite a cidade destino: ")
    return origem, destino
    
def listar_passagens():
    print("listar passagem\n")