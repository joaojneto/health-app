# health-app




# Elasticsearch

Index = pedidos_medicos

```json
{
  "pedidos_medicos": {
    "aliases": {},
    "mappings": {
      "properties": {
        "cpf": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "curadoria_ia": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "data_atualizacao": {
          "type": "date"
        },
        "data_cadastro": {
          "type": "date"
        },
        "data_nascimento": {
          "type": "date"
        },
        "descricacao_status": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "descricao_status": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "nome_paciente": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "observacoes": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "pedido_medico_base64": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "sexo": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "status": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "timestamp": {
          "type": "float"
        },
        "tipo_exame": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        }
      }
    },
    "settings": {
      "index": {
        "routing": {
          "allocation": {
            "include": {
              "_tier_preference": "data_content"
            }
          }
        },
        "number_of_shards": "1",
        "auto_expand_replicas": "false",
        "number_of_replicas": "0"
      }
    }
  }
}
```

Completion Inference API

```json
PUT _inference/completion/completion_openai
{
  "service": "openai",
  "service_settings": {
    "api_key": "SUA_API_KEY_AQUI",
    "model_id": "gpt-4o-mini"
  }
}
```


Pipeline = health-inference


```json
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