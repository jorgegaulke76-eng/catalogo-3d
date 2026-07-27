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

def obter_imagem_como_base64(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': url
        }
        response = requests.get(url, headers=headers, timeout=10)
        if 'text/html' in response.headers.get('Content-Type', ''):
            soup = BeautifulSoup(response.content, 'html.parser')
            meta = soup.find("meta", property="og:image")
            if meta and meta.get("content"): return obter_imagem_como_base64(meta["content"])
            return "https://i.ibb.co/kV0jyTfK/logo.png"
        b64 = base64.b64encode(response.content).decode()
        return f"data:image/jpeg;base64,{b64}"
    except: return "https://i.ibb.co/kV0jyTfK/logo.png"

def gerar_html_catalogo(lista_produtos):
    df = pd.DataFrame(lista_produtos)
    capa_links = "".join([f"<li><a href='#{c.replace(' ', '_')}'>{c}</a></li>" for c in df['Categoria'].unique()])
    
    html = f"""<!DOCTYPE html><html><head><style>
        body{{font-family: sans-serif; padding: 20px; background-color: #f9f9f9;}} 
        .capa{{background: white; padding: 20px; border-radius: 10px; margin-bottom: 30px; text-align: center;}}
        .categoria-section{{page-break-before: always; margin-top: 40px;}}
        .card{{display: flex; align-items: center; background: white; padding: 15px; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}} 
        img{{width: 100px; height: 100px; object-fit: cover; cursor: pointer;}}
    </style></head><body>
    <h1>CATÁLOGO MASTER - ALPHAFEST</h1>
    <div class="capa"><h3>Menu:</h3><ul>{capa_links}</ul></div>"""
    
    for categoria, group in df.groupby('Categoria'):
        html += f"<div id='{categoria.replace(' ', '_')}' class='categoria-section'><h2>📂 {categoria}</h2>"
        for _, p in group.iterrows():
            html += f"""<div class="card"><img src="{p['Imagem']}"><div><h3>{p['Nome_Exibicao']}</h3><p>{p['Descrição']}</p></div></div>"""
        html += "</div>"
    return html + "</body></html>"

# --- INTERFACE ---
st.set_page_config(page_title="Catálogo Master", layout="wide")
st.title("📦 ALPHAFEST - Gestor de Catálogo Master")

# Gestão de Arquivos (Salvar/Carregar)
col_gestao = st.columns(3)
with col_gestao[0]:
    arquivo_carregado = st.file_uploader("Carregar catálogo anterior (.xlsx)", type=['xlsx'])
    if arquivo_carregado:
        st.session_state.produtos_totais = pd.read_excel(arquivo_carregado).to_dict('records')
        st.success("Catálogo carregado!")

# Adição de Produtos
c1, c2 = st.columns(2)
with c1:
    cat_link = st.text_input("Categoria:", "Outros")
    link = st.text_area("Cole o link da imagem:")
    if st.button("Adicionar Link"):
        st.session_state.produtos_totais.append({"Nome_Exibicao": "Produto 3D", "Imagem": obter_imagem_como_base64(link), "Descrição": "Descrição gerada...", "Categoria": cat_link})
        st.rerun()

with c2:
    st.file_uploader("Upload foto", type=['jpg', 'png'], key="up")
    if st.button("Adicionar Foto"): st.rerun() # Adicionar lógica similar

# Ação Master
st.divider()
if st.button("GERAR CATÁLOGO MASTER FINAL"):
    st.download_button("🖨️ Baixar HTML Master", gerar_html_catalogo(st.session_state.produtos_totais), "catalogo_master.html", "text/html")

# Tabela de Controle
st.subheader("Itens no Catálogo Master")
st.dataframe(pd.DataFrame(st.session_state.produtos_totais))
