from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Rotas disponíveis no servidor 2
rotas_servidor2 = ["Rota D", "Rota E", "Rota F"]

@app.route('/comprar_passagem', methods=['POST'])
def comprar_passagem():
    # Mostrar as rotas disponíveis do servidor 2
    rotas = rotas_servidor2
    print("Rotas disponíveis no Servidor 2:", rotas)

    # Fazer requisição para o Servidor 1 para obter as rotas dele
    try:
        response = requests.get('http://127.0.0.1:5000/obter_rotas', headers={'From': 'servidor'})
        if response.status_code == 200:
            rotas_servidor1 = response.json().get("rotas", [])
            return jsonify({
                "mensagem": "Compra processada.",
                "rotas_servidor2": rotas,
                "rotas_servidor1": rotas_servidor1
            }), 200
        else:
            return jsonify({"mensagem": "Erro ao chamar o Servidor 1", "status": response.status_code}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"mensagem": f"Erro na requisição ao Servidor 1: {e}"}), 500

@app.route('/obter_rotas', methods=['GET'])
def obter_rotas():
    return jsonify({"rotas": rotas_servidor2}), 200

if __name__ == '__main__':
    app.run(port=5001)
