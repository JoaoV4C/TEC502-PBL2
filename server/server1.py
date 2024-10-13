from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Rota que se comunica com o servidor 2
@app.route('/comunicar_com_servidor2', methods=['GET'])
def comunicar_com_servidor2():
    try:
        # Faz a requisição GET para o servidor 2
        response = requests.get('http://127.0.0.1:5001/resposta_de_servidor2')
        
        # Resposta do servidor 2
        resposta_do_servidor2 = response.json()     # Pega a resposta em formato JSON
        
        return jsonify({'mensagem': 'Resposta do servidor 2', 'data': resposta_do_servidor2})
    except requests.exceptions.RequestException as e:
        return jsonify({'erro': 'Falha na comunicação com o servidor 2', 'detalhes': str(e)})

# Rota que responde a requisições vindas do servidor 2
@app.route('/resposta_de_servidor1', methods=['GET'])
def resposta_de_servidor1():
    return jsonify({'mensagem': 'Olá do servidor 1!', 'status': 'sucesso'})

if __name__ == '__main__':
    app.run(port=5000)
