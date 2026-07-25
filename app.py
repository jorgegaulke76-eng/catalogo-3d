import streamlit as st
import pandas as pd
import io
import requests
import re
from groq import Groq

# --- CONFIGURAÇÕES ---
# Certifique-se de que GROQ_API_KEY está configurada no Streamlit Cloud
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- FUNÇÕES ---

def obter_imagem_original(url):
    """Busca a foto oficial usando a API do Microlink."""
    try:
        api_url = f"https://api.microlink.io?url={url}"
        response = requests.get(api_url, timeout=10)
        data = response.json()
        if 'data' in data and 'image' in data['data']:
            return data['data']['image']['url']
        return None
    except:
        return None

def extrair_nome_do_link(link):
    """Remove IDs numéricos e formata o título."""
    parte_final = link.split('/')[-1].split('?')[0]
    # Remove números no início seguidos de traço
    nome = re.sub(r'^\d+-', '', parte_final)
    return nome.replace('-', ' ').title()

def calcular_preco(peso_g, tempo_h, preco_kg, margem_lucro, custo_hora, complexidade):
    custo_filamento = (peso_g / 1000) * preco_kg
    custo_operacional = (custo_hora * tempo_h) * complexidade
    custo_total = custo_filamento + custo_operacional + 1.50
    preco_venda = custo_total * (1 + (margem_lucro / 100))
    return round(custo_total, 2), round(preco_venda, 2)

def gerar_anuncio_ia(nome_produto):
    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é o especialista de marketing da ALPHAFEST ITATIBA. Escreva anúncios persuasivos para peças 3D. Máximo 2 parágrafos."},
                {"role": "user", "content": f"Crie um anúncio de vendas para: {nome_produto}"}
            ],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content
    except:
        return "Peça 3D Alphafest de alta precisão."

def gerar_html_catalogo(df, lote):
    """Gera um HTML otimizado para impressão profissional."""
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; margin: 40px; color: #333; background: #fff; }}
            .header {{ text-align: center; margin-bottom: 50px; border-bottom: 2px solid #333; padding-bottom: 20px; }}
            .card {{ display: flex; border: 1px solid #ccc; padding: 20px; margin-bottom: 20px; border-radius: 8px; page-break-inside: avoid; }}
            .card img {{ width: 150px; height: 150px; object-fit: cover; margin-right: 20px; border-radius: 5px; }}
            .info h2 {{ margin: 0 0 10px 0; color: #000; }}
            .price {{ font-weight: bold; font-size: 1.5em; color: #2e7d32; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="header"><h1>Catálogo Alphafest: {lote}</h1></div>
    """
    for _, row in df.iterrows():
        html_template += f"""
        <div class="card">
            <img src="{row['Imagem']}" alt="Produto">
            <div class="info">
                <h2>{row['Nome_Exibicao']}</h2>
                <p>{row['Descrição']}</p>
                <div class="price">R$ {row['Preço Venda (R$)']:.2f}</div>
            </div>
        </div>
        """
    html_template += "</body></html>"
    return html_template

# --- INTERFACE ---
st.set_page_config(page_title="Catálogo Alphafest", layout="wide")
st.title("📦 ALPHAFEST ITATIBA - Gerador de Catálogo")

with st.sidebar:
    st.header("Configurações")
    preco_kg = st.number_input("Preço Kg Filamento (R$)", value=90.00)
    margem = st.number_input("Margem Lucro (%)", value=200.0)
    custo_hora = st.number_input("Custo Máquina/Hora (R$)", value=1.10)
    complexidade = st.slider("Fator Complexidade", 1.0, 2.0, 1.0)

nome_lote = st.text_input("Nome do Lote:", "Lote Geral")
links_input = st.text_area("Cole os links (um por linha):")

if st.button("Gerar Catálogo"):
    if not links_input:
        st.warning("Insira links!")
    else:
        linhas = links_input.split('\n')
        dados_catalogo = []
        with st.spinner("Processando..."):
            for item in linhas:
                if not item.strip(): continue
                link = item.strip()
                nome = extrair_nome_do_link(link)
                custo, venda = calcular_preco(100.0, 2.0, preco_kg, margem, custo_hora, complexidade)
                dados_catalogo.append({
                    "Nome_Exibicao": nome,
                    "Imagem": obter_imagem_original(link),
                    "Descrição": gerar_anuncio_ia(nome),
                    "Custo (R$)": custo,
                    "Preço Venda (R$)": venda
                })

            df = pd.DataFrame(dados_catalogo)
            
            # Botões
            c1, c2 = st.columns(2)
            buffer_excel = io.BytesIO()
            df.to_excel(buffer_excel, index=False)
            c1.download_button("📊 Baixar Excel", buffer_excel, "catalogo.xlsx")
            c2.download_button("🖨️ Baixar HTML p/ Impressão", gerar_html_catalogo(df, nome_lote), "catalogo.html", "text/html")
            
            # Exibição
            for _, row in df.iterrows():
                with st.container(border=True):
                    cols = st.columns([1, 3])
                    cols[0].markdown(f'<img src="{row["Imagem"]}" style="width: 100%; border-radius: 8px;">', unsafe_allow_html=True)
                    cols[1].write(f"### {row['Nome_Exibicao']}")
                    cols[1].write(row['Descrição'])
                    cols[1].metric("Preço de Venda", f"R$ {row['Preço Venda (R$)']:.2f}")
                    st.text_area("Copie p/ Redes:", value=f"🚀 {row['Nome_Exibicao']}\n\n{row['Descrição']}\n\n💰 R$ {row['Preço Venda (R$)']:.2f}", height=100, key=f"txt_{row['Nome_Exibicao']}")
