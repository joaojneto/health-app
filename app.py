from flask import Flask, render_template, request, jsonify, session
from elasticsearch import Elasticsearch
import base64
import os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Variáveis globais para configuração do Elasticsearch
es_client = None

def get_es_client():
    """Retorna o cliente Elasticsearch configurado"""
    if 'es_url' in session and 'es_api_key' in session:
        try:
            return Elasticsearch(
                session['es_url'],
                api_key=session['es_api_key']
            )
        except:
            return None
    return None

@app.route('/')
def index():
    """Página inicial - redireciona para cadastro"""
    return render_template('index.html')

@app.route('/admin')
def admin():
    """Página de administração"""
    return render_template('admin.html')

@app.route('/api/save-config', methods=['POST'])
def save_config():
    """Salva configurações do Elasticsearch e logo"""
    try:
        data = request.json
        session['es_url'] = data.get('es_url')
        session['es_api_key'] = data.get('es_api_key')
        session['company_name'] = data.get('company_name', 'Plano de Saúde')
        
        #session['logo'] = data.get('logo')
        
        logo_base64 = data.get('logo')
        if logo_base64.startswith("data:image"):
            logo_base64 = logo_base64.split(",")[1]  # Remove o prefixo se tiver

        # Converte base64 para bytes
        logo_bytes = base64.b64decode(logo_base64)

        # Define o caminho para salvar
        caminho_pasta = "static/images"
        os.makedirs(caminho_pasta, exist_ok=True)
        caminho_arquivo = os.path.join(caminho_pasta, "logo.jpeg")

        # Salva a imagem no disco
        with open(caminho_arquivo, "wb") as f:
            f.write(logo_bytes)

        # Agora salva apenas o caminho na sessão
        session["logo"] = "/static/images/logo.jpeg"
        
        
        # Testa conexão
        es = Elasticsearch(session['es_url'], api_key=session['es_api_key'])
        es.ping()
        
        return jsonify({'success': True, 'message': 'Configurações salvas com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao salvar configurações: {str(e)}'}), 400

@app.route('/api/get-config', methods=['GET'])
def get_config():
    """Retorna configurações salvas"""
    return jsonify({
        'logo': session.get('logo', ''),
        'company_name': session.get('company_name', 'Plano de Saúde'),
        'es_configured': 'es_url' in session and 'es_api_key' in session
    })

@app.route('/cadastro')
def cadastro():
    """Página de cadastro de exames"""
    return render_template('cadastro.html')

@app.route('/api/cadastrar-exame', methods=['POST'])
def cadastrar_exame():
    """Cadastra um novo pedido de exame"""
    try:
        es = get_es_client()
        if not es:
            return jsonify({'success': False, 'message': 'Elasticsearch não configurado'}), 400
        
        # Recebe dados do formulário
        nome_paciente = request.form.get('nome_paciente')
        cpf = request.form.get('cpf')
        sexo = request.form.get('tipo_sexo')
        data_nascimento = request.form.get('data_nascimento')
        tipo_exame = request.form.get('tipo_exame')
        observacoes = request.form.get('observacoes', '')
        
        # Processa imagem
        imagem_base64 = None
        if 'pedido_medico' in request.files:
            file = request.files['pedido_medico']
            if file.filename:
                imagem_base64 = base64.b64encode(file.read()).decode('utf-8')
        
        # Cria documento
        documento = {
            'nome_paciente': nome_paciente,
            'cpf': cpf,
            'sexo': sexo,
            'data_nascimento': data_nascimento,
            'tipo_exame': tipo_exame,
            'observacoes': observacoes,
            'status': 'pendente',
            'descricao_status': '',
            'pedido_medico_base64': imagem_base64,
            'data_cadastro': datetime.now().isoformat(),
            'timestamp': datetime.now().timestamp()
        }
        
        success = False
        
        while success != True:
            try:
                # Indexa no Elasticsearch
                result = es.index(index='pedidos_medicos', document=documento, pipeline="health-inference")
                success = True
            except Exception as e:
                print(f"Erro ao indexar documento: {str(e)}")
                success = False
        
        return jsonify({
            'success': True, 
            'message': 'Exame cadastrado com sucesso!',
            'id': result['_id']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao cadastrar exame: {str(e)}'}), 500

@app.route('/auditoria')
def auditoria():
    """Página de auditoria de exames"""
    return render_template('auditoria.html')

@app.route('/api/listar-exames', methods=['GET'])
def listar_exames():
    """Lista todos os pedidos de exame com filtros"""
    try:
        es = get_es_client()
        if not es:
            return jsonify({'success': False, 'message': 'Elasticsearch não configurado'}), 400
        
        status_filter = request.args.get('status', 'todos')
        
        # Monta query
        query = {
            "match_all": {}
        }
        
        if status_filter != 'todos':
            query = {
                "term": {
                    "status.keyword": status_filter
                }
            }
        
        # Busca documentos ordenados por data (mais recentes primeiro)
        result = es.search(
            index='pedidos_medicos',
            query=query,
            sort=[{"timestamp": {"order": "desc"}}],
            size=1000
        )
        
        # Formata resposta
        exames = []
        for hit in result['hits']['hits']:
            exame = hit['_source']
            exame['id'] = hit['_id']
            exames.append(exame)
        
        return jsonify({'success': True, 'exames': exames})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao listar exames: {str(e)}'}), 500

@app.route('/api/atualizar-exame/<exame_id>', methods=['PUT'])
def atualizar_exame(exame_id):
    """Atualiza status e descrição de um exame"""
    try:
        es = get_es_client()
        if not es:
            return jsonify({'success': False, 'message': 'Elasticsearch não configurado'}), 400
        
        data = request.json
        
        # Atualiza documento
        es.update(
            index='pedidos_medicos',
            id=exame_id,
            doc={
                'status': data.get('status'),
                'descricao_status': data.get('descricao_status', ''),
                'data_atualizacao': datetime.now().isoformat()
            }
        )
        
        return jsonify({'success': True, 'message': 'Exame atualizado com sucesso!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao atualizar exame: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)