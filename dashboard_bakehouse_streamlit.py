"""
Dashboard Bakehouse - Análise de Vendas e Reviews
Aplicação Streamlit para visualização pública dos dados do Bakehouse

DEPLOYMENT INSTRUCTIONS:
1. Install dependencies: pip install streamlit plotly databricks-sql-connector pandas
2. Create .streamlit/secrets.toml with Databricks credentials:
   [databricks]
   server_hostname = "your-workspace.cloud.databricks.com"
   http_path = "/sql/1.0/warehouses/your-warehouse-id"
   access_token = "your-personal-access-token"
3. Run locally: streamlit run dashboard_bakehouse_streamlit.py
4. Deploy to Streamlit Cloud:
   - Push to GitHub
   - Connect repository on streamlit.io
   - Add secrets in Streamlit Cloud dashboard
   - Deploy and share public URL
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from databricks import sql
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Dashboard Bakehouse",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Database connection with caching
@st.cache_resource
def get_db_connection():
    """Establish connection to Databricks SQL warehouse"""
    try:
        connection = sql.connect(
            server_hostname=st.secrets["databricks"]["server_hostname"],
            http_path=st.secrets["databricks"]["http_path"],
            access_token=st.secrets["databricks"]["access_token"]
        )
        return connection
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        return None

# Data loading functions with caching
@st.cache_data(ttl=3600)
def load_transactions_data():
    """Load transactions ABT data"""
    connection = get_db_connection()
    if connection is None:
        return None
    
    query = "SELECT * FROM workspace.default.abt_transacoes_bakehouse"
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            df = cursor.fetchall_arrow().to_pandas()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados de transações: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def load_reviews_data():
    """Load reviews ABT data"""
    connection = get_db_connection()
    if connection is None:
        return None
    
    query = "SELECT * FROM workspace.default.abt_reviews_bakehouse"
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            df = cursor.fetchall_arrow().to_pandas()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados de reviews: {str(e)}")
        return None

# Helper function to format numbers
def format_number(num):
    """Format numbers with K/M abbreviations"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return f"{num:.0f}"

# Main application
def main():
    # Header
    st.markdown('<div class="main-header">🥐 Dashboard Bakehouse - Análise de Vendas e Reviews</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Versão pública do dashboard analítico | Dados sintéticos para demonstração</div>', unsafe_allow_html=True)
    
    # Context section (expandable)
    with st.expander("📚 Sobre o Dataset e Análises", expanded=False):
        st.markdown("""
        ### Sobre o Dataset
        
        O **samples.bakehouse** é um dataset sintético que simula o negócio de uma franquia de padaria/confeitaria. 
        O dataset contém 5 tabelas principais:
        
        - **sales_transactions**: Transações de vendas com produtos, quantidades, preços e métodos de pagamento
        - **sales_customers**: Informações demográficas e geográficas dos clientes
        - **sales_franchises**: Dados das franquias incluindo localização, tamanho e coordenadas geográficas
        - **media_customer_reviews**: Avaliações textuais de clientes sobre as franquias
        - **media_gold_reviews_chunked**: Reviews processados e segmentados para análise de texto
        
        ### Tabelas Analíticas Base (ABTs)
        
        Para facilitar as análises, foram criadas duas **Analytical Base Tables**:
        
        **1. ABT de Transações** (`abt_transacoes_bakehouse`)
        - **Grain**: Uma linha por transação individual
        - **Registros**: 3.333 transações
        - **Conteúdo**: Combina dados de vendas com dimensões de clientes e franquias
        - **Métricas**: quantidade, preços unitários, preços totais, produtos, métodos de pagamento
        - **Dimensões**: dados demográficos e geográficos de clientes, atributos de franquias
        
        **2. ABT de Reviews** (`abt_reviews_bakehouse`)
        - **Grain**: Uma linha por review (avaliação de cliente)
        - **Registros**: 204 reviews
        - **Conteúdo**: Combina avaliações de clientes com dados das franquias avaliadas
        - **Campos**: texto completo do review, data, identificadores
        - **Dimensões**: localização e atributos das franquias
        
        ### Análises Realizadas
        
        Este dashboard apresenta 8 visualizações interativas divididas em duas seções:
        
        **Análise de Vendas (5 visualizações):**
        1. Tendências de vendas ao longo do tempo
        2. Top 10 produtos por receita
        3. Distribuição por método de pagamento
        4. Receita por país (localização do cliente)
        5. Receita por franquia
        
        **Análise de Reviews (3 visualizações):**
        6. Volume de reviews ao longo do tempo
        7. Top franquias por volume de avaliações
        8. Distribuição geográfica de reviews
        """)
    
    # Summary of EDA
    with st.expander("📊 Resumo da Análise Exploratória de Dados", expanded=True):
        st.markdown("""
        ### Principais Descobertas
        
        **Período e Volume:**
        - **Período de vendas**: 1 a 17 de maio de 2024
        - **Período de reviews**: 20 a 31 de maio de 2024
        - **Receita total**: ~66.000 unidades monetárias
        - **Total de transações**: 3.333
        - **Total de reviews**: 204
        
        **Performance de Produtos:**
        - **Top 3 produtos** (por receita):
          1. Golden Gate Ginger (~12K)
          2. Outback Oatmeal (~11K)
          3. Austin Almond Biscotti (~11K)
        - Distribuição relativamente equilibrada entre os principais produtos
        
        **Métodos de Pagamento:**
        - Distribuição quase perfeitamente equilibrada:
          - Mastercard: 34.32%
          - Amex: 33.18%
          - Visa: 32.49%
        - Indica boa aceitação de múltiplas formas de pagamento
        
        **Análise Geográfica:**
        - **Receita por país** (clientes):
          - Austrália lidera com ~25K (38% do total)
          - USA: ~21K (32%)
          - Japão: ~20K (30%)
        - **Reviews por país** (franquias):
          - Japão domina com ~80 reviews (39%)
          - USA: ~65 reviews (32%)
          - Austrália: ~35 reviews (17%)
        
        **Performance de Franquias:**
        - **Baked Bliss** é a franquia com maior receita
        - Distribuição relativamente uniforme entre franquias nos reviews
        - **Sweet Temptations** e **Butter Babies** lideram em volume de avaliações
        
        **Tendências Temporais:**
        - Vendas diárias variam entre 1.9K e 4.5K
        - Picos de vendas observados nos dias 6, 9, 12 e 13 de maio
        - Reviews mostram crescimento constante de 96 para 108 (maio 20-31)
        - Crescimento de ~12.5% no volume de reviews no período
        
        **Insights Estratégicos:**
        - Oportunidade de análise de sentimento nos 204 reviews coletados
        - Potencial para correlacionar satisfação (reviews) com vendas por franquia
        - Base geográfica diversificada permite análises regionais
        - Período limitado sugere necessidade de dados históricos mais extensos
        """)
    
    # Load data
    df_transactions = load_transactions_data()
    df_reviews = load_reviews_data()
    
    if df_transactions is None or df_reviews is None:
        st.error("❌ Não foi possível carregar os dados. Verifique a conexão com o banco de dados.")
        st.stop()
    
    # Convert date columns to datetime
    df_transactions['data_hora_transacao'] = pd.to_datetime(df_transactions['data_hora_transacao'])
    df_reviews['data_review'] = pd.to_datetime(df_reviews['data_review'])
    
    # Key metrics at the top
    st.markdown("### 📈 Métricas Principais")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_revenue = df_transactions['preco_total'].sum()
        st.metric("Receita Total", format_number(total_revenue))
    
    with col2:
        total_transactions = len(df_transactions)
        st.metric("Transações", format_number(total_transactions))
    
    with col3:
        avg_ticket = df_transactions['preco_total'].mean()
        st.metric("Ticket Médio", format_number(avg_ticket))
    
    with col4:
        total_reviews = len(df_reviews)
        st.metric("Total de Reviews", format_number(total_reviews))
    
    with col5:
        unique_franchises = df_transactions['nome_franquia'].nunique()
        st.metric("Franquias Ativas", unique_franchises)
    
    st.markdown("---")
    
    # Section 1: Sales Analysis
    st.markdown("## 💰 Análise de Vendas")
    
    # Chart 1: Sales over time
    st.markdown("### Vendas ao Longo do Tempo")
    df_sales_time = df_transactions.groupby(df_transactions['data_hora_transacao'].dt.date)['preco_total'].sum().reset_index()
    df_sales_time.columns = ['Data', 'Receita Total']
    
    fig1 = px.line(
        df_sales_time, 
        x='Data', 
        y='Receita Total',
        title='Evolução Diária da Receita',
        labels={'Receita Total': 'Receita', 'Data': 'Data'}
    )
    fig1.update_traces(line_color='#17BECF', line_width=3)
    fig1.update_layout(
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Charts 2 & 3: Top Products and Payment Methods (side by side)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Top 10 Produtos por Receita")
        df_products = df_transactions.groupby('produto')['preco_total'].sum().sort_values(ascending=True).tail(10).reset_index()
        
        fig2 = px.bar(
            df_products,
            x='preco_total',
            y='produto',
            orientation='h',
            title='Produtos Mais Vendidos',
            labels={'preco_total': 'Receita', 'produto': 'Produto'}
        )
        fig2.update_traces(marker_color='#17BECF')
        fig2.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        st.markdown("### Distribuição por Método de Pagamento")
        df_payment = df_transactions['metodo_pagamento'].value_counts().reset_index()
        df_payment.columns = ['Método', 'Transações']
        
        fig3 = px.pie(
            df_payment,
            values='Transações',
            names='Método',
            title='Métodos de Pagamento',
            color_discrete_sequence=['#17BECF', '#FFA500', '#2ECC71']
        )
        fig3.update_traces(textposition='inside', textinfo='percent+label')
        fig3.update_layout(
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    # Charts 4 & 5: Revenue by Country and Franchise (side by side)
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### Receita por País (Cliente)")
        df_country = df_transactions.groupby('pais_cliente')['preco_total'].sum().sort_values(ascending=False).head(10).reset_index()
        
        fig4 = px.bar(
            df_country,
            x='pais_cliente',
            y='preco_total',
            title='Top 10 Países por Receita',
            labels={'preco_total': 'Receita', 'pais_cliente': 'País'}
        )
        fig4.update_traces(marker_color='#17BECF')
        fig4.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    with col4:
        st.markdown("### Receita por Franquia")
        df_franchise = df_transactions.groupby('nome_franquia')['preco_total'].sum().sort_values(ascending=False).head(10).reset_index()
        
        fig5 = px.bar(
            df_franchise,
            x='nome_franquia',
            y='preco_total',
            title='Top 10 Franquias por Receita',
            labels={'preco_total': 'Receita', 'nome_franquia': 'Franquia'}
        )
        fig5.update_traces(marker_color='#17BECF')
        fig5.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig5, use_container_width=True)
    
    st.markdown("---")
    
    # Section 2: Reviews Analysis
    st.markdown("## ⭐ Análise de Reviews")
    
    # Chart 6: Reviews over time
    st.markdown("### Volume de Reviews ao Longo do Tempo")
    df_reviews_time = df_reviews.groupby(df_reviews['data_review'].dt.date).size().reset_index()
    df_reviews_time.columns = ['Data', 'Número de Reviews']
    df_reviews_time['Acumulado'] = df_reviews_time['Número de Reviews'].cumsum()
    
    fig6 = px.line(
        df_reviews_time,
        x='Data',
        y='Acumulado',
        title='Crescimento Acumulado de Reviews',
        labels={'Acumulado': 'Número de Reviews', 'Data': 'Data'}
    )
    fig6.update_traces(line_color='#17BECF', line_width=3)
    fig6.update_layout(
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig6, use_container_width=True)
    
    # Charts 7 & 8: Top Franchises and Reviews by Country (side by side)
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("### Top Franquias por Volume de Reviews")
        df_franchise_reviews = df_reviews['nome_franquia'].value_counts().head(10).reset_index()
        df_franchise_reviews.columns = ['Franquia', 'Número de Reviews']
        
        fig7 = px.bar(
            df_franchise_reviews,
            x='Número de Reviews',
            y='Franquia',
            orientation='h',
            title='Franquias Mais Avaliadas',
            labels={'Número de Reviews': 'Reviews', 'Franquia': 'Franquia'}
        )
        fig7.update_traces(marker_color='#17BECF')
        fig7.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig7, use_container_width=True)
    
    with col6:
        st.markdown("### Reviews por País")
        df_country_reviews = df_reviews['pais_franquia'].value_counts().reset_index()
        df_country_reviews.columns = ['País', 'Número de Reviews']
        
        fig8 = px.bar(
            df_country_reviews,
            x='País',
            y='Número de Reviews',
            title='Distribuição Geográfica de Reviews',
            labels={'Número de Reviews': 'Reviews', 'País': 'País'}
        )
        fig8.update_traces(marker_color='#17BECF')
        fig8.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig8, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p>📊 Dashboard criado com Streamlit | 🥐 Dados: samples.bakehouse (Databricks)</p>
        <p>Última atualização: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
