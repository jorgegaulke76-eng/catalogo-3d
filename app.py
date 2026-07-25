import streamlit as st
import pandas as pd
import io
import requests
from groq import Groq
from bs4 import BeautifulSoup

# --- CONFIGURAÇÕES ---
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- FUNÇÕES ---

def obter_imagem_original(url):
    if url.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
        return url
    if "makerworld.com" in url:
        try:
            api_url = f"https://api.microlink.io?url={url}"
            response = requests.get(api_url, timeout=10)
            data = response.json()
            if 'data' in data and 'image' in data['data']: return data['data']['image']['url']
        except: pass
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        meta = soup.find("meta", property="og:image")
        if meta and meta.get("content"): return meta["content"]
    except: pass
    return "https://i.ibb.co/kV0jyTfK/logo.png"

def calcular_preco_individual(peso_g, tempo_h, preco_kg, margem_lucro, custo_hora, complexidade):
    custo_filamento = (float(peso_g) / 1000) * preco_kg
    custo_operacional = (custo_hora * float(tempo_h)) * complexidade
    custo_total = custo_filamento + custo_operacional + 1.50
    preco_venda = custo_total * (1 + (margem_lucro / 100))
    return round(preco_total := custo_total, 2), round(preco_venda, 2)

def gerar_anuncio_ia(nome_produto, contexto_manual=""):
    prompt = f"Crie um anúncio de vendas persuasivo para: {nome_produto}. {f'Detalhes: {contexto_manual}' if contexto_manual else ''}"
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "system", "content": "Seja um especialista de marketing. Escreva anúncios curtos e persuasivos focando em benefícios. Não mencione frete/garantias."},
                      {"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content
    except: return f"{nome_produto} de alta qualidade."

def gerar_html_catalogo(df, lote):
    html = f"""<!DOCTYPE html><html><head><style>body{{font-family:sans-serif; padding:30px;}} .card{{display:flex; border-left:8px solid #3498db; padding:20px; margin-bottom:20px; box-shadow:0 2px 5px #ccc;}} img{{width:150px; height:150px; object-fit:cover; margin-right:20px;}}</style></head><body><h1>Lote: {lote}</h1>"""
    for _, row in df.iterrows():
        html += f"""<div class="card"><img src="{row['Imagem']}"><div><h2>{row['Nome_Exibicao']}</h2><p>{row['Descrição']}</p><b>R$ {row['Preço Venda (R$)']:.2f}</b></div></div>"""
    return html + "</body></html>"

# --- INTERFACE ---
st.set_page_config(page_title="Catálogo Alphafest", layout="wide")
st.title("📦 ALPHAFEST ITATIBA - Gerador de Catálogo")

with st.sidebar:
    st.header("Configurações Globais")
    preco_kg = st.number_input("Preço Kg Filamento (R$)", value=90.00)
    margem = st.number_input("Margem Lucro (%)", value=200.0)
    custo_hora = st.number_input("Custo Máquina/Hora (R$)", value=1.10)
    complexidade = st.slider("Fator Complexidade", 1.0, 2.0, 1.0)

nome_lote = st.text_input("Nome do Lote:", "Lote Geral")
st.info("💡 Formato: **URL | Detalhes | Peso(g) | Tempo(h)**")
links_input = st.text_area("Cole os produtos:", height=200)

if st.button("Gerar Catálogo"):
    dados = []
    for linha in links_input.split('\n'):
        if not linha.strip(): continue
        partes = [p.strip() for p in linha.split('|')]
        # Extrai os dados: link, detalhes, peso, tempo
        link, desc, peso, tempo = (partes + ["", "100", "2"])[:4]
        
        custo, venda = calcular_preco_individual(peso, tempo, preco_kg, margem, custo_hora, complexidade)
        dados.append({
            "Nome_Exibicao": nome_lote,
            "Imagem": obter_imagem_original(link),
            "Descrição": gerar_anuncio_ia(nome_lote, desc),
            "Preço Venda (R$)": venda
        })
    
    df = pd.DataFrame(dados)
    st.success("Catálogo gerado!")
    
    for _, row in df.iterrows():
        with st.container(border=True):
            cols = st.columns([1, 4])
            cols[0].image(row['Imagem'], use_column_width=True)
            cols[1].subheader(row['Nome_Exibicao'])
            cols[1].write(row['Descrição'])
            cols[1].metric("Preço", f"R$ {row['Preço Venda (R$)']:.2f}")
