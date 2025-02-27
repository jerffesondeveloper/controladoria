from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return "Sistema de Controle de Pendências - Versão de Manutenção"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)  