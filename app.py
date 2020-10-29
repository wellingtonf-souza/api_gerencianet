from flask import Flask, request, render_template, redirect, url_for
from gerencianet import Gerencianet
import json

client = json.load(open('credentials.json'))

credentials = {
    'client_id': client['client_id'],
    'client_secret': client['client_secret'],
    'sandbox': True
}

gn = Gerencianet(credentials)
app = Flask(__name__)


@app.route('/information_banking_billet/')
def inform_banking_billet():
    return render_template('create_banking_billet.html')


@app.route('/create_banking_billet/', methods=['POST'])
def create_banking_billet():
    descricao = request.form['descricao']
    valor = int(request.form['valor'].replace(',', ''))
    quantidade = int(request.form['quantidade'])
    nome_cliente = request.form['nome_cliente']
    cpf = request.form['cpf'].replace(".", "").replace("-", "")
    telefone = request.form['telefone'].replace(" ", "").replace("-", "")
    vencimento = request.form['vencimento']

    body = {
        'items': [{
            'name': descricao,
            'value': valor,
            'amount': quantidade
        }],
        'payment': {
            'banking_billet': {
                'expire_at': vencimento,
                'customer': {
                    'name': nome_cliente,
                    'phone_number': telefone,
                    'cpf': cpf
                }
            }
        }
    }

    response = gn.create_charge_onestep(params=None, body=body)
    if response[u'code'] == 200:
        link_download = response[u'data'][u'pdf'][u'charge'].encode()
        return 'Success'
    else:
        return render_template('error.html')


if __name__ == "__main__":
    app.run(debug=True)
