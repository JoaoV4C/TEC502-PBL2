import os
from flask import Flask, request, render_template, redirect, url_for
from flask_login import UserMixin, login_required, login_user, logout_user, LoginManager
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
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
    if os.path.exists('../app/data/passagers.json'):
        with open('../app/data/passagers.json', 'r', encoding='utf-8') as file:
            passagers = json.load(file)
        for passager in passagers:
            if passager['id'] == int(user_id):
                return User(passager['id'], passager['name'], passager['cpf'])
    return None

@app.route('/', methods=["GET"])
@login_required
def index():
    return render_template("home.html")

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        cpf = request.form.get("cpf")
        if os.path.exists('../app/data/passagers.json'):
            with open('../app/data/passagers.json', 'r', encoding='utf-8') as file:
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

        if os.path.exists('../app/data/passagers.json'):
            with open('../app/data/passagers.json', 'r', encoding='utf-8') as file:
                passagers = json.load(file)

            for passager in passagers:
                if passager['cpf'] == cpf:
                    return render_template("register.html", error="CPF já cadastrado!")

            new_passager = {"id": passagers[-1]["id"] + 1,"name": name, "cpf": cpf}
            passagers.append(new_passager)
        # Adicionar novo passageiro
        else:
            passagers = [{"id": 1, "name": name, "cpf": cpf}]
 
        with open('../app/data/passagers.json', 'w', encoding='utf-8') as file:
            json.dump(passagers, file, ensure_ascii=False)

        return redirect(url_for('login'))
        
    return render_template("register.html")



# @app.route('/comprar_passagem', methods=['POST'])
# def comprar_passagem():
#     # Verifica se a requisição veio de um cliente ou outro servidor
#     remetente = request.headers.get('From', 'desconhecido')
    
#     if remetente == 'cliente':
#         print("Requisição de compra recebida do cliente.")
#     else:
#         print(f"Requisição recebida de {remetente}.")
    
#     # Mostrar as rotas disponíveis no servidor 1
#     rotas = rotas_servidor1
#     print("Rotas disponíveis no Servidor 1:", rotas)
    
#     # Fazer requisição para o Servidor 2 para obter as rotas dele
#     try:
#         response = requests.get('http://127.0.0.1:5001/obter_rotas', headers={'From': 'servidor'})
#         if response.status_code == 200:
#             rotas_servidor2 = response.json().get("rotas", [])
#             return jsonify({
#                 "mensagem": "Compra processada.",
#                 "remetente": remetente, # Informar quem enviou a requisiçaõ
#                 "rotas_servidor1": rotas,
#                 "rotas_servidor2": rotas_servidor2
#             }), 200
#         else:
#             return jsonify({"mensagem": "Erro ao chamar o Servidor 2", "status": response.status_code}), response.status_code
#     except requests.exceptions.RequestException as e:
#         return jsonify({"mensagem": f"Erro na requisição ao Servidor 2: {e}"}), 500

# @app.route('/obter_rotas', methods=['GET'])
# def obter_rotas():
#     # Verifica o remetente da requisição
#     remetente = request.headers.get('from', ' desconhecido')
#     if remetente == 'cliente':
#         print('Requisição de lisagem de rotas recebida do cliente.\n')
#     else:
#         print(f'Requisição de lsitagem de rotas recebida de {remetente}.\n')
#     return jsonify({"rotas": rotas_servidor1, "remetente": remetente}), 200

# # Rota para mostrar os usuários online
# @app.route('/usuarios_online', methods=['GET'])
# def usuarios_online():
#     if usuarios_logados:
#         return jsonify({"usuarios_online": usuarios_logados}), 200
#     else:
#         return jsonify({"mensagem": "Nenhum usuário online no momento"}), 200


if __name__ == '__main__':
    app.run(port=5000, debug=True)
