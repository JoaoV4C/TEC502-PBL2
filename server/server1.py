from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Rotas disponíveis no servidor 1
rotas_servidor1 = ["Rota A", "Rota B", "Rota C"]

@app.route('/comprar_passagem', methods=['POST'])
def comprar_passagem():
    # Mostrar as rotas disponíveis do servidor 1
    rotas = rotas_servidor1
    print("Rotas disponíveis no Servidor 1:", rotas)

    # Fazer requisição para o Servidor 2 para obter as rotas dele
    try:
        response = requests.get('http://127.0.0.1:5001/obter_rotas', headers={'From': 'servidor'})
        if response.status_code == 200:
            rotas_servidor2 = response.json().get("rotas", [])
            return jsonify({
                "mensagem": "Compra processada.",
                "rotas_servidor1": rotas,
                "rotas_servidor2": rotas_servidor2
            }), 200
        else:
            return jsonify({"mensagem": "Erro ao chamar o Servidor 2", "status": response.status_code}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"mensagem": f"Erro na requisição ao Servidor 2: {e}"}), 500

@app.route('/obter_rotas', methods=['GET'])
def obter_rotas():
    return jsonify({"rotas": rotas_servidor1}), 200

if __name__ == '__main__':
    app.run(port=5000)
