import streamlit as st
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import plotly.express as px  # Adicione esta linha
import os

# Configurações de conexão com o banco de dados
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT")

# Funções de banco de dados (sem alterações)
def criar_conexao():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        engine = create_engine(f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
        return conn, engine
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        return None, None

def criar_tabela(conn):
    with conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS dados_bibliometricos (
                id SERIAL PRIMARY KEY,
                "Authors" TEXT,
                "Author full names" TEXT,
                "Author(s) ID" TEXT,
                "Title" TEXT,
                "Year" TEXT,
                "Source title" TEXT,
                "Volume" TEXT,
                "Issue" TEXT,
                "Art. No." TEXT,
                "Page start" TEXT,
                "Page end" TEXT,
                "Page count" TEXT,
                "Cited by" TEXT,
                "DOI" TEXT,
                "Link" TEXT,
                "Affiliations" TEXT,
                "Authors with affiliations" TEXT,
                "Abstract" TEXT,
                "Author Keywords" TEXT,
                "Index Keywords" TEXT,
                "Molecular Sequence Numbers" TEXT,
                "Chemicals/CAS" TEXT,
                "Tradenames" TEXT,
                "Manufacturers" TEXT,
                "Funding Details" TEXT,
                "Funding Texts" TEXT,
                "References" TEXT,
                "Correspondence Address" TEXT,
                "Editors" TEXT,
                "Publisher" TEXT,
                "Sponsors" TEXT,
                "Conference name" TEXT,
                "Conference date" TEXT,
                "Conference location" TEXT,
                "Conference code" TEXT,
                "ISSN" TEXT,
                "ISBN" TEXT,
                "CODEN" TEXT,
                "PubMed ID" TEXT,
                "Language of Original Document" TEXT,
                "Abbreviated Source Title" TEXT,
                "Document Type" TEXT,
                "Publication Stage" TEXT,
                "Open Access" TEXT,
                "Source" TEXT,
                "EID" TEXT
            )
        ''')
    conn.commit()

def inserir_dados(engine, df):
    df.to_sql('dados_bibliometricos', engine, if_exists='replace', index=False)
    st.success(f"Inseridos {len(df)} registros na tabela dados_bibliometricos")

def recuperar_dados(conn):
    query = """
    SELECT "Authors", "Title", "DOI", "Year", "Source title" 
    FROM dados_bibliometricos
    """
    return pd.read_sql_query(query, conn)

# Funções para gerar gráficos
def publicacoes_por_ano(df):
    contagem_por_ano = df['Year'].value_counts().sort_index()
    fig = px.bar(x=contagem_por_ano.index, y=contagem_por_ano.values,
                 labels={'x': 'Ano', 'y': 'Número de Publicações'},
                 title='Publicações por Ano')
    st.plotly_chart(fig)

def autores_mais_publicados(df):
    autores = df['Authors'].str.split(', ', expand=True).stack()
    contagem_autores = autores.value_counts().head(10)
    fig = px.bar(x=contagem_autores.index, y=contagem_autores.values,
                 labels={'x': 'Autor', 'y': 'Número de Publicações'},
                 title='Top 10 Autores Mais Publicados')
    st.plotly_chart(fig)

def fontes_mais_comuns(df):
    contagem_fontes = df['Source title'].value_counts().head(10)
    fig = px.pie(values=contagem_fontes.values, names=contagem_fontes.index,
                 title='Top 10 Fontes Mais Comuns')
    st.plotly_chart(fig)

def main():
    st.title("Análise Bibliométrica")
    
    conn, engine = criar_conexao()
    if conn is None or engine is None:
        return
    
    criar_tabela(conn)
    
    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")
    
    if uploaded_file is not None:
        try:
            df_completo = pd.read_csv(uploaded_file)
            inserir_dados(engine, df_completo)
            
            df = recuperar_dados(conn)
            
            st.sidebar.title("Opções de Visualização")
            
            # Menu de opções no sidebar
            opcao = st.sidebar.radio(
                "Escolha uma visualização:",
                ("Dados Brutos", "Gráficos")
            )
            
            if opcao == "Dados Brutos":
                st.write("Dados recuperados do PostgreSQL:")
                st.write(df)
                st.write(f"Total de registros: {len(df)}")
                st.write(f"Colunas disponíveis: {', '.join(df.columns)}")
            
            elif opcao == "Gráficos":
                tipo_grafico = st.sidebar.selectbox(
                    "Escolha um tipo de gráfico:",
                    ("Publicações por Ano", "Autores Mais Publicados", "Fontes Mais Comuns")
                )
                
                if tipo_grafico == "Publicações por Ano":
                    publicacoes_por_ano(df)
                elif tipo_grafico == "Autores Mais Publicados":
                    autores_mais_publicados(df)
                elif tipo_grafico == "Fontes Mais Comuns":
                    fontes_mais_comuns(df)
            
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {str(e)}")
    
    conn.close()

if __name__ == "__main__":
    main()