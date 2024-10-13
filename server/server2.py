from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Rota que se comunica com o servidor 1
@app.route('/comunicar_com_servidor1', methods=['GET'])
def comunicar_com_servidor1():
    try:
        # Faz a requisição GET para o servidor 1
        response = requests.get('http://127.0.0.1:5000/resposta_de_servidor1')
        # Pega a resposta do servidor 1
        resposta_de_servidor1 = response.json() # Resposta em formato JSON
       
        return jsonify({'mensagem': 'Resposta do servidor 1', 'data': resposta_de_servidor1})
    except requests.exceptions.RequestException as e:
        return jsonify({'erro': 'Falha na comunicação com o servidor 1', 'detalhes': str(e)})

# Rota que responde a requisições vindas do servidor 1
@app.route('/resposta_de_servidor2', methods=['GET'])
def resposta_de_servidor2():
    return jsonify({'mensagem': 'Olá do servidor 2!', 'status': 'sucesso'})

if __name__ == '__main__':
    app.run(port=5001)
