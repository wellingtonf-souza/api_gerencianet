from flask import Flask, request, render_template, redirect, url_for
from gerencianet import Gerencianet
import json

client = json.load(open('credentials.json'))

credentials = {
    'client_id': client['client_id'],
    'client_secret': client['client_secret'],
    'sandbox': True
}


def adjust_number_of_whats(s, i=2):
    return s[:i] + s[i+1:]


gn = Gerencianet(credentials)
app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.route('/information_banking_billet/')
def inform_banking_billet():
    return render_template('banking_billet.html')


@app.route('/create_banking_billet/', methods=['POST'])
def create_banking_billet():
    descricao = request.form['descricao']
    valor_format_real = request.form['valor']
    valor = int(valor_format_real.replace(',', ''))
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
        return render_template('conf_banking_billet.html', link_down=link_download, shareLink=shareLink, barcode=barcode)
    else:
        return render_template('error.html')


if __name__ == "__main__":
    app.run(debug=True)
