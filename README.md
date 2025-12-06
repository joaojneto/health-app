# 🏥 health-app --- Plataforma de Curadoria Médica com IA + Elasticsearch

O **health-app** é uma aplicação moderna que realiza **curadoria
automatizada de pedidos médicos** utilizando **Inteligência
Artificial**, integrada diretamente com **Elasticsearch** para
indexação, busca e execução de pipelines inteligentes via **Ingest +
OpenAI Completion Inference**.

------------------------------------------------------------------------

# ✨ Visão Geral

Este projeto permite:

-   Cadastro de pedidos médicos
-   Avaliação automática via IA (aprovado/recusado + justificativa)
-   Indexação inteligente no Elasticsearch
-   Pipeline de ingest que transforma o pedido em *decision-making
    estruturado*
-   Armazenamento de documentos ricos (incluindo pedidos médicos em
    Base64)
-   Prontidão para ser consumido por dashboards, apps mobile, APIs ou
    front-ends

------------------------------------------------------------------------

# 🚀 Stack Tecnológica

  -----------------------------------------------------------------------
  Componente                                Função
  ----------------------------------------- -----------------------------
  **Python 3.10+**                          Aplicação principal

  **Elasticsearch 8.x**                     Base de busca e
                                            enriquecimento

  **Ingest Pipelines**                      Automação da curadoria via IA

  **OpenAI Completion Inference API**       Modelo de ML usado no
                                            pipeline

  **Flask / FastAPI**                       Backend da aplicação
                                            (dependendo da versão usada)
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# ⚙️ Arquitetura Técnica

               Pedido Médico
                     │
                     ▼
                health-app
                     │
                     ▼
         Elasticsearch Ingest Pipeline
                     │
            (script → prompt → inference)
                     │
                     ▼
           OpenAI Completion Inference API
                     │
               JSON estruturado
                     ▼
             Documento final indexado

------------------------------------------------------------------------

# 📦 Instalação

## 1️⃣ Clonar o repositório

``` bash
git clone https://github.com/joaojneto/health-app.git
cd health-app
```

## 2️⃣ Criar ambiente virtual

``` bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

## 3️⃣ Instalar dependências

``` bash
pip install -r requirements.txt
```

## 4️⃣ Configurar variáveis de ambiente

``` bash
export ES_ENDPOINT="https://seu-endpoint.es.amazonaws.com"
export ES_API_KEY="SUA_API_KEY"
```

------------------------------------------------------------------------

# 🧩 Integração com Elasticsearch

Abaixo estão **TODAS as configurações essenciais**, já formatadas para
produção.

------------------------------------------------------------------------

# 📁 Mapeamento do Índice

**Index:** `pedidos_medicos`

``` json
{
  "pedidos_medicos": {
    "aliases": {},
    "mappings": {
      "properties": {
        "cpf": { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
        "curadoria_ia": { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
        "data_atualizacao": { "type": "date" },
        "data_cadastro": { "type": "date" },
        "data_nascimento": { "type": "date" },
        "descricacao_status": { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
        "descricao_status": { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
        "nome_paciente": { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
        "observacoes": { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
        "pedido_medico_base64": { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
        "sexo": { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
        "status": { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
        "timestamp": { "type": "float" },
        "tipo_exame": { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } }
      }
    },
    "settings": {
      "index": {
        "routing": { "allocation": { "include": { "_tier_preference": "data_content" } } },
        "number_of_shards": "1",
        "auto_expand_replicas": "false",
        "number_of_replicas": "0"
      }
    }
  }
}
```

------------------------------------------------------------------------

# 🤖 Configuração da Completion Inference API

``` json
PUT _inference/completion/completion_openai
{
  "service": "openai",
  "service_settings": {
    "api_key": "SUA_API_KEY_AQUI",
    "model_id": "gpt-4o-mini"
  }
}
```

------------------------------------------------------------------------

# 🧠 Pipeline: `health-inference`

Este pipeline:

1.  Gera um **prompt médico** automaticamente.
2.  Envia para o **modelo da OpenAI** via Inference API.
3.  Recebe um JSON contendo:
    -   `status`
    -   `descricao_status`
4.  Insere isso no documento final.

------------------------------------------------------------------------

## Pipeline Completo

``` json
{
  "health-inference": {
    "description": "Pipeline para ajudar na auditoria prévia gerada por IA",
    "processors": [
      {
        "script": {
          "source": "ctx.prompt = 'Você é uma profissional de saúde e precisa auditar um pedido de exame para saber se o mesmo pode ser aprovado ou não. Analisando o nome:' + ctx.nome_paciente + ' e sexo: ' + ctx.sexo + ' para o exame: ' + ctx.tipo_exame + '. defina se o exame poderá ser aprovado ou recusado, juntamente com uma descrição. Você deverá exibir essa resposta APENAS COM O JSON iniciando com { e terminando com } . Dentro do JSON tera um campo chamado status e outro campo com o nome descricao_status, ambos com seus respectivos valores'"
        }
      },
      {
        "inference": {
          "input_output": {
            "input_field": "prompt",
            "output_field": "curadoria_ia"
          },
          "model_id": "completion_openai"
        }
      },
      {
        "json": {
          "field": "curadoria_ia",
          "add_to_root": true
        }
      },
      {
        "remove": {
          "field": [
            "prompt",
            "model_id"
          ]
        }
      }
    ]
  }
}
```

------------------------------------------------------------------------

# 🧪 Testes

``` bash
pytest
```

------------------------------------------------------------------------

# 🤝 Contribuição

Pull requests são bem-vindos!\
Sugestões podem ser abertas via *Issues*.

------------------------------------------------------------------------

# 📄 Licença

MIT License.

------------------------------------------------------------------------

# 📬 Contato

Abra uma issue no GitHub se precisar de ajuda.
