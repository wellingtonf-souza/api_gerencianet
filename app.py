from flask import Flask, request, render_template, redirect, url_for
from gerencianet import Gerencianet
import json

client = json.load(open('credentials.json'))
# formato de credentials.json
#  {
#     "client_id": "Client_Id_*",
#     "client_secret": "Client_Secret_*",
#     "account_identifier": "*"
#  }

credentials = {
    'client_id': client['client_id'],
    'client_secret': client['client_secret'],
    'sandbox': True
}


def adjust_number_of_whats(s, i=2):
    return s[:i] + s[i+1:]


gn = Gerencianet(credentials)
app = Flask(__name__)


# define a variavel account_identifier como global em todos os templates
@app.context_processor
def insert_account_identifier():
    return dict(account_identifier=client['account_identifier'])


@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.route('/information_banking_billet/')
def inform_banking_billet():
    return render_template('banking_billet.html')


@app.route('/information_credit_card/')
def information_credit_card():
    return render_template('credit_card.html')


@app.route('/information_carnet/')
def information_carnet():
    return render_template('carnet.html')


@app.route('/create_banking_billet/', methods=['POST'])
def create_banking_billet():
    descricao = request.form['descricao']
    valor_format_real = request.form['valor']
    valor = int(valor_format_real.replace(',', '').replace('.', ''))
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
        link_download = response[u'data'][u'pdf'][u'charge']
        barcode = response[u'data'][u'barcode']

        shareLink = 'https://api.whatsapp.com/send'
        shareLink += '?phone=55'+adjust_number_of_whats(telefone)+'+&'
        shareLink += 'text=Olá, segue o boleto no valor de R$ '+valor_format_real+'. '
        shareLink += 'Cobrança referente à '+descricao+', '
        shareLink += 'com vencimento para '+vencimento+'. '
        shareLink += 'Acesse o boleto pelo link: '+link_download+''
        shareLink += ' ou pague usando o código de barras: '+barcode+'.'
        return render_template('conf_banking_billet.html', link_down=link_download, shareLink=shareLink, copy=barcode)
    else:
        return render_template('error.html')


@app.route('/create_credit_card/', methods=['POST'])
def create_credit_card():
    descricao = request.form['descricao']
    valor = int(request.form['valor'])
    quantidade = int(request.form['quantidade'])
    nome_cliente = request.form['nome_cliente']
    cpf = request.form['cpf']
    telefone = request.form['telefone'].replace(" ", "").replace("-", "")
    rua = request.form['rua']
    numero = request.form['numero']
    bairro = request.form['bairro']
    cep = request.form['cep']
    cidade = request.form['cidade']
    estado = request.form['estado']
    payament_token = request.form['payament_token']
    installments = int(request.form['installments'])
    email = request.form['email']
    nascimento = request.form['nascimento']
    body = {
        'items': [{
            'name': descricao,
            'value': valor,
            'amount': quantidade
        }],
        'payment': {
            'credit_card': {
                'installments': installments,
                'payment_token': payament_token,
                'billing_address': {
                    'street': rua,
                    'number': numero,
                    'neighborhood': bairro,
                    'zipcode': cep,
                    'city': cidade,
                    'state': estado
                },
                'customer': {
                    'name': nome_cliente,
                    'email': email,
                    'cpf': cpf,
                    'birth': nascimento,
                    'phone_number': telefone
                }
            }
        }
    }
    response = gn.create_charge_onestep(params=None, body=body)
    if response[u'code'] == 200:
        charge_id = str(response[u'data'][u'charge_id'])
        print('chegou aqui')
        return render_template('conf_credit_card.html', copy=charge_id)
    else:
        return render_template('error.html')


@app.route('/create_carnet/', methods=['POST'])
def create_carnet():
    descricao = request.form['descricao']
    valor = int(request.form['valor'].replace(',', '').replace('.', ''))
    quantidade = int(request.form['quantidade'])
    nome_cliente = request.form['nome_cliente']
    cpf = request.form['cpf'].replace(".", "").replace("-", "")
    telefone = request.form['telefone'].replace(" ", "").replace("-", "")
    email = request.form['email']
    parcelas = int(request.form['parcelas'])
    vencimento = request.form['vencimento']
    message = request.form['instrucao']
    body = {
        'items': [{
            'name': descricao,
            'value': valor,
            'amount': quantidade
        }],
        'customer': {
            'name': nome_cliente,
            'email': email,
            'cpf': cpf,
            'phone_number': telefone
        },
        'repeats': parcelas,
        'expire_at': vencimento
    }
    if len(message) > 0:
        body.update({'message': message})
    response = gn.create_carnet(body=body)
    if response[u'code'] == 200:
        carnet_link = response[u'data'][u'pdf'][u'carnet']
        carnet_id = response[u'data'][u'carnet_id']
        charges = response[u'data'][u'charges']
        return render_template('conf_carnet.html', carnet_id=carnet_id, carnet_link=carnet_link, charges=charges)
    else:
        return render_template('error.html')


if __name__ == "__main__":
    app.run(debug=True)
