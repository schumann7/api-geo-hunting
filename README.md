# API Geo Hunting

API Flask para gerenciamento de dados do aplicativo GeoHunting da disciplina de desenvolvimento para dispositivos móveis com PostgreSQL.

## Configuração

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto:
```env
DATABASE_URL=postgresql://[user]:[password]@[neon_hostname]/[dbname]?sslmode=require&channel_binding=require
```

## Executando a API

```bash
python app.py
```

A API estará disponível em `http://localhost:5000`

## Endpoints

### GET /
Verificar se a API está rodando e se ela se conectou com o banco

### GET /dados
Retorna todos os dados da tabela `salas`

### POST /criar_sala
É necessário enviar a requisição junto de um arquivo json, gera um id aleatório e registra os dados no banco de dados.

## Estrutura do Projeto

- `app.py` - Aplicação principal Flask
- `requirements.txt` - Dependências do projeto
- `.env` - Variáveis de ambiente (não versionado)