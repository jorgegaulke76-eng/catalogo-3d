import streamlit as st
import pandas as pd
import os
import base64
from PIL import Image, ImageDraw, ImageFont
from groq import Groq
from datetime import datetime
import io

# --- CONFIGURAÇÕES ---
# Coloque sua chave no painel "Secrets" do Streamlit como: GROQ_API_KEY
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MARCA_FABRICANTE = "ALPHAFEST ITATIBA"
CUSTO_EMBALAGEM = 1.50

# --- FUNÇÕES DE LÓGICA ---
def calcular_preco(peso_g, tempo_h, preco_kg, margem_lucro, custo_hora, complexidade):
    custo_filamento = (peso_g / 1000) * preco_kg
    custo_operacional = (custo_hora * tempo_h) * complexidade
    custo_total = custo_filamento + custo_operacional + CUSTO_EMBALAGEM
    preco_venda = custo_total * (1 + (margem_lucro / 100))
    return round(custo_total, 2), round(preco_venda, 2)

def gerar_anuncio_ia(nome_produto):
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é o especialista de marketing da ALPHAFEST ITATIBA. Escreva anúncios persuasivos para peças impressas em 3D. Foque na qualidade e no design. Máximo de 3 parágrafos."},
                {"role": "user", "content": f"Crie um anúncio de vendas para: {nome_produto}"}
            ],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content
    except:
        return "Peça 3D de alta qualidade, fabricada com precisão pela Alphafest."

# --- INTERFACE ---
st.set_page_config(page_title="Catálogo Alphafest", layout="wide")
st.title(f"📦 {MARCA_FABRICANTE} - Gerador de Catálogo")

with st.sidebar:
    st.header("Configurações")
    preco_kg = st.number_input("Preço Kg Filamento (R$)", value=90.00)
    margem = st.number_input("Margem Lucro (%)", value=200.0)
    custo_hora = st.number_input("Custo Máquina/Hora (R$)", value=1.10)
    complexidade = st.slider("Fator Complexidade", 1.0, 2.0, 1.0)
    
nome_lote = st.text_input("Nome do Lote (Ex: Natal, Pais):", "Lote Geral")
links_input = st.text_area("Cole os nomes ou links dos produtos (um por linha):")

if st.button("Gerar Catálogo"):
    if not links_input:
        st.warning("Insira ao menos um produto!")
    else:
        linhas = links_input.split('\n')
        dados_catalogo = []
        
        progress = st.progress(0)
        for i, item in enumerate(linhas):
            if not item.strip(): continue
            
            # Simulação de extração de dados (pode substituir pela sua lógica de scraping)
            nome = item.strip()
            # Valores fictícios para exemplo (no seu script original eram calculados do site)
            peso, tempo = 100.0, 2.0 
            
            custo_total, preco_venda = calcular_preco(peso, tempo, preco_kg, margem, custo_hora, complexidade)
            descricao = gerar_anuncio_ia(nome)
            
            dados_catalogo.append({
                "Codigo": f"MW{i+1:03d}",
                "Produto": nome,
                "Descrição": descricao,
                "Custo (R$)": custo_total,
                "Preço Venda (R$)": preco_venda
            })
            progress.progress((i + 1) / len(linhas))

        # --- EXPORTAÇÃO ---
        df = pd.DataFrame(dados_catalogo)
       # 1. Adicionamos a coluna de imagem ao DataFrame
        df['Imagem'] = [gerar_url_imagem(nome) for nome in df['Produto']]
        
        # 2. Excel (Download)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        st.download_button("📥 Baixar Excel", buffer, f"catalogo_{nome_lote}.xlsx", "application/vnd.ms-excel")
        
        # 3. Exibição da Tabela com Imagens
        st.subheader("Catálogo Gerado")
        st.dataframe(
            df,
            column_config={
                "Imagem": st.column_config.ImageColumn(
                    "Prévia", help="Imagem gerada pela IA", width="medium"
                ),
                "Custo (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
                "Preço Venda (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
            },
            hide_index=True,
            use_container_width=True
        )
        st.success("Catálogo gerado com sucesso!")
