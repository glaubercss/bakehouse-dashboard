# Dashboard Bakehouse - Streamlit App

Dashboard interativo público para análise de dados do Bakehouse (padaria/confeitaria).

## 📋 Pré-requisitos

- Conta no [Streamlit Cloud](https://streamlit.io/cloud)
- Acesso ao Databricks SQL Warehouse
- Personal Access Token do Databricks

## 🚀 Deployment no Streamlit Cloud

### 1. Preparar o Repositório

```bash
# Clone ou crie um novo repositório no GitHub
git init
git add dashboard_bakehouse_streamlit.py requirements.txt
git commit -m "Initial commit - Bakehouse dashboard"
git remote add origin https://github.com/seu-usuario/bakehouse-dashboard.git
git push -u origin main
```

### 2. Configurar Secrets no Streamlit Cloud

Acesse o [Streamlit Cloud](https://share.streamlit.io/) e:

1. Clique em "New app"
2. Conecte seu repositório GitHub
3. Selecione o arquivo `dashboard_bakehouse_streamlit.py`
4. Antes de deploy, clique em "Advanced settings" > "Secrets"
5. Adicione as credenciais do Databricks:

```toml
[databricks]
server_hostname = "sua-workspace.cloud.databricks.com"
http_path = "/sql/1.0/warehouses/seu-warehouse-id"
access_token = "seu-personal-access-token"
```

**Como obter as credenciais:**

- **server_hostname**: URL do seu workspace Databricks (sem https://)
- **http_path**: Vá em SQL > SQL Warehouses > seu warehouse > Connection details
- **access_token**: User Settings > Developer > Access tokens > Generate new token

### 3. Deploy

1. Clique em "Deploy!"
2. Aguarde o build completar (~2-3 minutos)
3. O app estará disponível em uma URL pública: `https://seu-app.streamlit.app`

## 🔒 Segurança

- ⚠️ **Importante**: Nunca commite o arquivo `.streamlit/secrets.toml` no Git
- Use apenas no Streamlit Cloud através da interface de secrets
- O Personal Access Token deve ter permissões de leitura no SQL Warehouse

## 🧪 Testar Localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Criar arquivo de secrets local
mkdir .streamlit
cat > .streamlit/secrets.toml << EOF
[databricks]
server_hostname = "sua-workspace.cloud.databricks.com"
http_path = "/sql/1.0/warehouses/seu-warehouse-id"
access_token = "seu-personal-access-token"
EOF

# Executar app
streamlit run dashboard_bakehouse_streamlit.py
```

## 📊 Funcionalidades

### Análise de Vendas
- Vendas ao longo do tempo (série temporal)
- Top 10 produtos por receita
- Distribuição por método de pagamento
- Receita por país (cliente)
- Receita por franquia

### Análise de Reviews
- Volume de reviews ao longo do tempo
- Top franquias por volume de avaliações
- Distribuição geográfica de reviews

## 📦 Dados

O dashboard utiliza duas Analytical Base Tables (ABTs):
- `workspace.default.abt_transacoes_bakehouse` (3.333 registros)
- `workspace.default.abt_reviews_bakehouse` (204 registros)

## 🛠️ Tecnologias

- **Streamlit**: Framework web Python
- **Plotly**: Visualizações interativas
- **Databricks SQL Connector**: Conexão com warehouse
- **Pandas**: Manipulação de dados

## 📝 Licença

Dataset sintético samples.bakehouse fornecido pela Databricks para fins educacionais.
