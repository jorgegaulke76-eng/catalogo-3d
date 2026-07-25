import streamlit as st
import pandas as pd
import io
import requests
from groq import Groq
from bs4 import BeautifulSoup

# --- CONFIGURAÇÕES ---
# Lembre-se de manter sua chave GROQ_API_KEY configurada no Streamlit Cloud
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- FUNÇÕES ---

def obter_imagem_original(url):
    """Busca a imagem do produto: prioriza link direto ou busca via scraping."""
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

def calcular_preco_individual():
    # Valores padrão internos para cálculo automático
    peso_g_default = 100.0
    tempo_h_default = 2.0
    preco_kg_default = 90.0
    margem_default = 200.0
    custo_hora_default = 1.10
    complexidade_default = 1.0
        
    custo_filamento = (peso_g_default / 1000) * preco_kg_default
    custo_operacional = (custo_hora_default * tempo_h_default) * complexidade_default
    custo_total = custo_filamento + custo_operacional + 1.50
    preco_venda = custo_total * (1 + (margem_default / 100))
    return round(custo_total, 2), round(preco_venda, 2)

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

nome_lote = st.text_input("Nome do Lote:", "Lote Geral")
st.info("💡 Formato obrigatório: **URL | Detalhes**")
links_input = st.text_area("Cole os produtos:", height=250)

if st.button("Gerar Catálogo"):
    if not links_input:
        st.warning("Insira links!")
    else:
        dados = []
        for linha in links_input.split('\n'):
            if not linha.strip(): continue
            # Separa apenas Link e Detalhes
            partes = [p.strip() for p in linha.split('|')]
            link = partes[0]
            desc = partes[1] if len(partes) > 1 else ""
            
            custo, venda = calcular_preco_individual()
            dados.append({
                "Nome_Exibicao": nome_lote,
                "Imagem": obter_imagem_original(link),
                "Descrição": gerar_anuncio_ia(nome_lote, desc),
                "Preço Venda (R$)": venda
            })
        
        df = pd.DataFrame(dados)
        st.success("Catálogo gerado com sucesso!")
        
        c1, c2 = st.columns(2)
        buffer_excel = io.BytesIO()
        df.to_excel(buffer_excel, index=False)
        c1.download_button("📊 Baixar Excel", buffer_excel, "catalogo.xlsx")
        c2.download_button("🖨️ Baixar HTML p/ Impressão", gerar_html_catalogo(df, nome_lote), "catalogo.html", "text/html")
        
        st.divider()
        for _, row in df.iterrows():
            with st.container(border=True):
                cols = st.columns([1, 4])
                cols[0].image(row['Imagem'], use_column_width=True)
                cols[1].subheader(row['Nome_Exibicao'])
                cols[1].write(row['Descrição'])
                cols[1].metric("Preço de Venda", f"R$ {row['Preço Venda (R$)']:.2f}")
                st.text_area("Copie p/ Redes:", value=f"🚀 {row['Nome_Exibicao']}\n\n{row['Descrição']}\n\n💰 R$ {row['Preço Venda (R$)']:.2f}", height=150, key=f"txt_{row['Nome_Exibicao']}")
