from flask import Flask, render_template, redirect, url_for, request, make_response, session, g
import pdfkit
import controler, teste
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

app = Flask(__name__)

app.secret_key = "PipocaSalgada"

class Cliente:

    def __init__(self, id):
        self.id = str(id)
        dados = controler.select_CursorDict('*', 'clientes', 'id_cliente='+self.id)[0]
        self.nome = dados['nome']
        self.data_de_nascimento = dados['data_de_nascimento']
        self.cpf = dados['cpf']
        self.telefone = dados['telefone']
        self.email = dados['email']
        self.senha = dados['senha']
        self.cep = dados['cep']
        self.endereco = dados['endereco']
        self.numero = dados['numero']
        self.complemento = dados['complemento']
        self.cidade = dados['cidade']
        self.estado = dados['estado']
        self.nome_responsavel = dados['nome_responsavel']
        self.cpf_responsavel = dados['cpf_responsavel']

    def set_nome(self, nome):
        controler.update({'nome':nome}, 'clientes', 'id_cliente='+self.id)
        self.nome = controler.select('nome', 'clientes', 'id_cliente='+self.id)[0][0]

    def set_senha(self, senha):
        controler.update({'senha':senha}, 'clientes', 'id_cliente='+self.id)
        self.nome = controler.select('senha', 'clientes', 'id_cliente='+self.id)[0][0]


class Profissional:
    def __init__(self, id):
        self.id = str(id)
        dados = controler.select_CursorDict('*', 'profissionais', 'id_profissional='+self.id)[0]
        self.nome = dados['nome']
        self.profissao = dados['profissao']
        self.registro_profissional = dados['registro_profissional']
        self.cpf = dados['cpf']
        self.telefone = dados['telefone']
        self.data_de_nascimento = dados['data_de_nascimento']
        self.email = dados['email']
        self.senha = dados['senha']
        self.cep = dados['cep']
        self.endereco = dados['endereco']
        self.numero = dados['numero']
        self.complemento = dados['complemento']
        self.cidade = dados['cidade']
        self.estado = dados['estado']

    def set_nome(self, nome):
        controler.update({'nome':nome}, 'profissionais', 'id_profissional='+self.id)
        self.nome = controler.select('nome', 'profissionais', 'id_profissional='+self.id)[0][0]

    def set_senha(self, senha):
        controler.update({'senha':senha}, 'profissionais', 'id_profissional='+self.id)
        self.nome = controler.select('senha', 'profissionais', 'id_profissional='+self.id)[0][0]

@app.route('/<nomeProfissional>/<regProf>/<profissao>/<nome>/<cpf>/<precoConsulta>/<email>/<enderecoComercial>/<telefone>/<cep>')
def pdf_template1(nomeProfissional, regProf, profissao, nome, cpf, precoConsulta, email, enderecoComercial, telefone, cep):
    rendered = render_template('pdf_template18+.html', nomeProfissional = nomeProfissional, regProf = regProf, profissao = profissao, nome = nome, cpf = cpf, precoConsulta = precoConsulta, email=email, enderecoComercial = enderecoComercial, telefone = telefone, cep = cep)
    pdf = pdfkit.from_string(rendered, False)

    response =  make_response(pdf)
    response.headers['Content-Type'] =  'applocation/pdf'
    response.headers['Content-Disposition'] =   'inline; filename = recibo.pdf'

    return response

@app.route('/<nomeProfissional>/<regProf>/<profissao>/<nome>/<cpfRes>/<nomeRes>/<precoConsulta>/<email>/<enderecoComercial>/<telefone>/<cep>')
def pdf_template2(nomeProfissional, regProf, profissao, nome, cpfRes, nomeRes, precoConsulta, email, enderecoComercial, telefone, cep):
    rendered = render_template('pdf_template18-.html', nomeProfissional = nomeProfissional, regProf = regProf, profissao = profissao, nome = nome, cpfRes = cpfRes, nomeRes = nomeRes, precoConsulta = precoConsulta, email=email, enderecoComercial = enderecoComercial, telefone = telefone, cep = cep)
    pdf = pdfkit.from_string(rendered, False)

    response =  make_response(pdf)
    response.headers['Content-Type'] =  'applocation/pdf'
    response.headers['Content-Disposition'] =   'inline; filename = recibo.pdf'

    return response


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    error = None
    if request.method == "POST":
        if request.form["radio"] == '0':
            nome = request.form["nome"]
            data_de_nascimento = request.form["nascimento"]
            cpf = request.form["cpf"]
            telefone = controler.limpa_telefone(request.form["telefone"])
            email = request.form["email"]
            senha = request.form["senha"]
            cep=request.form["cep"]
            endereco = request.form["endereco"]
            numero = request.form["numero"]
            complemento = request.form["complemento"]
            cidade = request.form["cidade"]
            estado = request.form["estado"]

            if nome=='' or data_de_nascimento=='' or cpf=='' or telefone=='' or email=='' or senha=='' or cep=='' or endereco=='' or numero=='' or cidade=='' or estado=='':
                error = 'Preencha todos os campos!'
            elif cpf == "CPF Inválido":
                error = 'Verifique seu CPF!'
            elif endereco =="CEP não encontrado":
                error = 'Verifique seu CEP!'
            elif controler.verifica_email(email,'clientes'):
                error = 'Ops! Email já cadastrado.'
            else:
                cpf = controler.limpa_cpf(request.form["cpf"])
                if controler.verifica_cpf(cpf, 'clientes'):
                    error = 'Este CPF já está cadastrado!'
                else:
                    hashed_password = generate_password_hash(senha)
                    if controler.verifica_idade(data_de_nascimento)==False:
                        nome_responsavel = '-'
                        cpf_responsavel = '-'
                        controler.cadastra_cliente(nome, data_de_nascimento, cpf, telefone, email, hashed_password, cep, endereco, numero, complemento, cidade, estado, nome_responsavel, cpf_responsavel)
                        return redirect(url_for('login'))
                    else:
                        nome_responsavel = request.form["nomeRes"]
                        cpf_responsavel = request.form["cpfRes"]
                        if nome_responsavel or cpf_responsavel =='':
                            error = 'Preencha todos os campos!'
                        else:
                            controler.cadastra_cliente(nome, data_de_nascimento, cpf, telefone, email, hashed_password, cep, endereco, numero, complemento, cidade, estado, nome_responsavel, cpf_responsavel)
                            return redirect(url_for('login'))

        if request.form["radio"] == '1': #profissional
            nome = request.form["nomePro"]
            cpf = request.form["cpfPro"]
            profissao = request.form["profissaoPro"]
            registro_profissional = request.form["regProf"]
            telefone = controler.limpa_telefone(request.form["telefonePro"])
            data_de_nascimento = request.form["nascimentoPro"]
            email = request.form["emailPro"]
            senha = request.form["senhaPro"]
            cep=request.form["cepPro"]
            endereco = request.form["enderecoPro"]
            numero = request.form["numeroPro"]
            complemento = request.form["complementoPro"]
            cidade = request.form["cidadePro"]
            estado = request.form["estadoPro"]

            if nome=='' or cpf=='' or profissao=='' or registro_profissional=='' or telefone=='' or data_de_nascimento=='' or email=='' or senha=='' or cep=='' or endereco=='' or numero=='' or cidade=='' or estado=='':
                error = 'Preencha todos os campos!'
            elif cpf == "CPF Inválido":
                error = 'Verifique seu CPF!'
            elif endereco =="CEP não encontrado":
                error = 'Verifique seu CEP!'
            elif controler.verifica_email(email,'profissionais'):
                error = 'Ops! Email já cadastrado.'
            else:
                cpf = controler.limpa_cpf(request.form["cpfPro"])
                if controler.verifica_cpf(cpf, 'profissionais'):
                    error = 'Este CPF já está cadastrado!'
                else:
                    hashed_password = generate_password_hash(senha)
                    controler.cadastra_profissional(nome, cpf, profissao, registro_profissional, telefone, data_de_nascimento, email, hashed_password, cep, endereco, numero, complemento, cidade, estado)
                    return redirect(url_for('login'))
    return render_template('create.html', error=error)


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST' and request.form['senha']!='' and request.form['cpf']!='':
        cpf_inserido = controler.limpa_cpf(request.form["cpf"])
        senha_inserida = request.form["senha"]

        if controler.verifica_cpf(cpf_inserido, "clientes") and controler.verifica_cpf(cpf_inserido, "profissionais"): # ta na bd
            """A mudança pra pessoa que tem conta cliente e profissional vai ser aqui. Algo do tipo
            if cpf in clientes and cpf in profissionais: redirect pra uma pagina "logged", intermediária
            nessa página a pessoa decide em qual conta vai entrar"""
            pass

        elif controler.verifica_cpf(cpf_inserido, "clientes"): # ta na bd
            user = Cliente(controler.cpf_id(cpf_inserido, 'clientes'))
            if check_password_hash(user.senha,senha_inserida):
                session['user'] = True
                session['id'] = user.id
                return redirect(url_for('loggedCliente'))

            else:
                error = "Senha incorreta!"

        elif controler.verifica_cpf(cpf_inserido, "profissionais"): # ta na bd
            user = Profissional(controler.cpf_id(cpf_inserido, 'profissionais'))
            if check_password_hash(user.senha,senha_inserida):
                session['user'] = True
                session['id'] = user.id
                return redirect(url_for('loggedProfissional'))
            else:
                error = "Senha incorreta!"
        else:
            error = "Usuário não cadastrado"
    return render_template('login.html', error=error)

@app.before_request
def before_request():
    g.user = None
    if g.user in session:
        g.user = session['user']

@app.route('/loggedCliente', methods = ['GET', 'POST'])
def loggedCliente():
    if 'user' in session:
        user = Cliente(session['id'])
    return render_template("loggedCliente.html", cliente=user.nome)


@app.route('/loggedProfissional')
def loggedProfissional():
    if 'user' in session:
        user = Profissional(session['id'])
        return render_template("loggedProfissional.html", profissional=user.nome)
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('login', None)
        session.pop('id', None)
    return redirect(url_for('login'))


@app.route('/sobreNos', methods=['GET', 'POST'])
def sobreNos():
    error = None
    if request.method =='POST':
        return redirect(url_for('cadastro'))
    return render_template('sobreNos.html', error=error)

#CONFIGURAÇÃO DO EMAIL
app.config['DEBUG']=True
app.config['TESTING']=False
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USE_SSL']=False
#app.config['MAIL_DEBUG']=True
app.config['MAIL_USERNAME']='waat.ufrj@gmail.com'
app.config['MAIL_PASSWORD']='PipocaSalgada!'
app.config['MAIL_DEFAULT_SENDER']=('Equipe WAAT', 'waat.ufrj@gmail.com')
app.config['MAIL_MAX_EMAILS']=3 #NÃO MEXAM AQUI
#app.config['MAIL_SUPRESS_SEND']=False
app.config['MAIL_ASCII_ATTACHMENTS']=True

mail = Mail(app)

@app.route('/email_recuperar_senha/')
def email_recuperacao_senha():
    msg = Message("Recuperação de Senha", recipients=['aadottori@gmail.com', 'anderson.avvd@gmail.com','thiagodias2708@gmail.com', 'wesley.jupter@poli.ufrj.br'])
    msg.html= render_template('RecuperarSenha.html', senha = 'Pega aqui')
    mail.send(msg)
    return 'Senha enviada'

@app.route('/enviaEmail/')
def enviaEmail():
    msg = Message("Recibo", recipients=['aadottori@gmail.com', 'anderson.avvd@gmail.com','thiagodias2708@gmail.com', 'wesley.jupter@poli.ufrj.br'])
    msg.body= "Segue em anexo o recibo referente à sua consulta."

    with app.open_resource("recibo_teste.pdf") as recibo:
        msg.attach("recibo_teste.pdf", "application/pdf", recibo.read())
    mail.send(msg)
    return 'Email enviado'

@app.route('/Recibos', methods=['GET', 'POST'])
def RecibosProfissional():
    return render_template('RecibosProfissional.html')

@app.route('/Cadastrar_atendimentos', methods=['GET', 'POST'])
def CadastrarAtendimentos():
    if request.method == "POST":
        cpfProfissional = Profissional(session['id']).cpf
        cpfCliente = controler.limpa_cpf(request.form["cpfCliente"])
        dataConsulta = request.form["dataConsulta"]
        dataGerado = date.today().strftime("%d/%m/%Y")
        valor = request.form["valor"]
        controler.cadastra_atendimento(cpfProfissional, cpfCliente, dataConsulta, dataGerado, valor)
        redirect(url_for('RecibosProfissional'))

    return render_template('CadastrarAtendimentos.html')

@app.route('/Informaçoes de cadastro do Profissional', methods=['GET', 'POST'])
def Informacoes_cadastroPro():
    telefone = Profissional(session['id']).telefone
    if len(telefone) == 11:
        telefone = '({}) {}-{}'.format(telefone[0:2],telefone[2:7], telefone[7:])
    else:
        telefone = '({}) {}-{}'.format(telefone[0:2],telefone[2:6], telefone[6:])
    return render_template('Informacoes_cadastroPro.html', nome=Profissional(session['id']).nome, cpf=Profissional(session['id']).cpf, profissao=Profissional(session['id']).profissao, registro=Profissional(session['id']).registro_profissional, telefone=telefone, nascimento=Profissional(session['id']).data_de_nascimento, email=Profissional(session['id']).email, cep=Profissional(session['id']).cep, endereco=Profissional(session['id']).endereco, numero=Profissional(session['id']).numero, complemento=Profissional(session['id']).complemento, cidade=Profissional(session['id']).cidade, estado=Profissional(session['id']).estado)

@app.route('/Informaçoes de cadastro do Cliente', methods=['GET', 'POST'])
def Informacoes_cadastroCliente():
    telefone = Cliente(session['id']).telefone
    if len(telefone) == 11:
        telefone = '({}) {}-{}'.format(telefone[0:2],telefone[2:7], telefone[7:])
    else:
        telefone = '({}) {}-{}'.format(telefone[0:2],telefone[2:6], telefone[6:])

    return render_template('Informacoes_cadastroCliente.html', nome=Cliente(session['id']).nome, cpf=Cliente(session['id']).cpf, telefone=telefone, nascimento=Cliente(session['id']).data_de_nascimento, email=Cliente(session['id']).email, cep=Cliente(session['id']).cep, endereco=Cliente(session['id']).endereco, numero=Cliente(session['id']).numero, complemento=Cliente(session['id']).complemento, cidade=Cliente(session['id']).cidade, estado=Cliente(session['id']).estado)

if __name__ == '__main__':
    app.run(debug=True)
