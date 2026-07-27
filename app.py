import streamlit as st
import pandas as pd
import io
import requests
import base64
from groq import Groq
from bs4 import BeautifulSoup

# --- CONFIGURAÇÕES ---
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- INICIALIZAÇÃO DE ESTADO ---
if "produtos_totais" not in st.session_state: st.session_state.produtos_totais = []

# --- FUNÇÕES ---

def obter_imagem_original(url):
    if url.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')): return url
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

def image_to_base64(uploaded_file):
    return f"data:image/jpeg;base64,{base64.b64encode(uploaded_file.getvalue()).decode()}"

def gerar_anuncio_ia(nome_produto, contexto_manual=""):
    prompt = f"Produto: {nome_produto}. Detalhes: {contexto_manual}. Escreva uma descrição curta, profissional e vendedora."
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "system", "content": "Você é um especialista de marketing da ALPHAFEST ITATIBA. Seja direto, profissional e vendedor. Use apenas os detalhes fornecidos."},
                      {"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content
    except: return f"{nome_produto} de alta qualidade."

def gerar_html_catalogo(lista_produtos, lote):
    html = f"""<!DOCTYPE html><html><head><style>body{{font-family:sans-serif; padding:30px;}} .card{{display:flex; border-left:8px solid #3498db; padding:20px; margin-bottom:20px; box-shadow:0 2px 5px #ccc;}} img{{width:150px; height:150px; object-fit:cover; margin-right:20px;}}</style></head><body><h1>Lote: {lote}</h1>"""
    for p in lista_produtos:
        html += f"""<div class="card"><img src="{p['Imagem']}"><div><h2>{p['Nome_Exibicao']}</h2><p>{p['Descrição']}</p></div></div>"""
    return html + "</body></html>"

# --- INTERFACE ---
st.set_page_config(page_title="Catálogo Alphafest", layout="wide")
st.title("📦 ALPHAFEST ITATIBA - Gerador de Catálogo")

nome_lote = st.text_input("Nome do Lote:", "Lote Geral")

# 1. Seção de Adição (Links ou Upload)
c1, c2 = st.columns(2)
with c1:
    st.subheader("🔗 Adicionar via Link")
    links_input = st.text_area("Cole os produtos (URL | Detalhes):", height=150)
    if st.button("Adicionar Links ao Lote"):
        for linha in links_input.split('\n'):
            if not linha.strip(): continue
            partes = [p.strip() for p in linha.split('|')]
            link, desc = partes[0], (partes[1] if len(partes) > 1 else "")
            st.session_state.produtos_totais.append({"Nome_Exibicao": nome_lote, "Imagem": obter_imagem_original(link), "Descrição": gerar_anuncio_ia(nome_lote, desc)})
        st.rerun()

with c2:
    st.subheader("📁 Adicionar via Upload")
    foto = st.file_uploader("Subir foto", type=['jpg', 'png', 'jpeg'])
    desc_manual = st.text_area("Detalhes do produto:", height=90)
    if st.button("Adicionar Foto ao Lote"):
        if foto:
            st.session_state.produtos_totais.append({"Nome_Exibicao": nome_lote, "Imagem": image_to_base64(foto), "Descrição": gerar_anuncio_ia(nome_lote, desc_manual)})
            st.rerun()

# 2. Prévia dos Produtos (Onde você vê a lista)
if st.session_state.produtos_totais:
    st.divider()
    st.subheader(f"Prévia do Catálogo ({len(st.session_state.produtos_totais)} itens)")
    
    for i, row in enumerate(st.session_state.produtos_totais):
        with st.container(border=True):
            cols = st.columns([1, 4])
            cols[0].image(row['Imagem'], use_column_width=True)
            cols[1].subheader(row['Nome_Exibicao'])
            cols[1].write(row['Descrição'])
            st.text_area("Copie p/ Redes:", value=f"🚀 {row['Nome_Exibicao']}\n\n{row['Descrição']}", height=120, key=f"txt_{i}")

    # 3. Geração Final
    st.divider()
    if st.button("Gerar Arquivos Finais (Excel + HTML)"):
        df = pd.DataFrame(st.session_state.produtos_totais)
        
        # Botões de Download que aparecem no final
        buf_excel = io.BytesIO()
        df.to_excel(buf_excel, index=False)
        st.download_button("📊 Baixar Excel", buf_excel, "catalogo.xlsx")
        st.download_button("🖨️ Baixar HTML", gerar_html_catalogo(st.session_state.produtos_totais, nome_lote), "catalogo.html", "text/html")
        
        st.success("Arquivos gerados!")

    if st.button("Limpar Tudo e Recomeçar"):
        st.session_state.produtos_totais = []
        st.rerun()
