import streamlit as st
import pandas as pd
import io
import requests
import base64
from groq import Groq
from bs4 import BeautifulSoup

# --- CONFIGURAÇÕES ---
# Lembre-se de manter sua chave GROQ_API_KEY no Streamlit Cloud
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- INICIALIZAÇÃO DE ESTADO ---
if "produtos_totais" not in st.session_state: st.session_state.produtos_totais = []

# --- FUNÇÕES ---

def obter_imagem_como_base64(url):
    """Busca a imagem e converte para base64 para contornar bloqueios."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': url
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if 'text/html' in response.headers.get('Content-Type', ''):
            soup = BeautifulSoup(response.content, 'html.parser')
            meta = soup.find("meta", property="og:image")
            if meta and meta.get("content"):
                return obter_imagem_como_base64(meta["content"])
            return "https://i.ibb.co/kV0jyTfK/logo.png"

        b64 = base64.b64encode(response.content).decode()
        return f"data:image/jpeg;base64,{b64}"
    except:
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

def gerar_html_catalogo(lista_produtos):
    df = pd.DataFrame(lista_produtos)
    categorias = df['Categoria'].unique()
    
    capa_links = ""
    for cat in categorias:
        id_cat = cat.replace(" ", "_")
        capa_links += f"<li><a href='#{id_cat}'>{cat}</a></li>"

    html = f"""<!DOCTYPE html><html><head><style>
        body{{font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; background-color: #f9f9f9;}} 
        h1{{text-align: center; color: #2c3e50; margin-bottom: 20px; border-bottom: 3px solid #3498db; padding-bottom: 10px;}}
        
        /* Ajuste do Menu Vertical */
        .capa{{background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 30px; text-align: left;}}
        .capa h3{{margin-top: 0; color: #34495e; border-bottom: 1px solid #ddd; padding-bottom: 10px;}}
        .capa ul{{list-style: none; padding: 0;}}
        .capa li{{margin: 8px 0;}}
        .capa a{{display: block; font-size: 16px; color: #2980b9; text-decoration: none; font-weight: bold; padding: 5px; border-radius: 4px; transition: background 0.2s;}}
        .capa a:hover{{background: #f0f0f0;}}
        
        .categoria-section{{page-break-before: always; margin-top: 30px;}}
        .categoria-titulo{{color: #34495e; padding: 10px; background: #e8f6f3; border-left: 8px solid #1abc9c; margin-bottom: 20px;}}
        
        /* Cards Centralizados */
        .card-container{{display: flex; flex-direction: column; align-items: center;}}
        .card{{display: flex; align-items: center; background: white; padding: 15px; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); width: 80%;}} 
        img{{width: 100px; height: 100px; object-fit: cover; border-radius: 5px; margin-right: 15px; cursor: pointer; transition: transform 0.2s;}}
        img:hover{{transform: scale(1.05);}}
        h2{{margin-top: 0; color: #2980b9; font-size: 1.2rem;}}
        
        .lightbox {{ display: none; position: fixed; z-index: 1000; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); }}
        .lightbox-img {{ max-width: 90%; max-height: 80%; margin: auto; display: block; position: relative; top: 10%; border: 2px solid white; }}
        .close-btn {{ position: absolute; top: 20px; right: 30px; color: white; font-size: 40px; cursor: pointer; }}
    </style>
    <script>
        function openLightbox(src) {{ document.getElementById('full-img').src = src; document.getElementById('lightbox').style.display = 'block'; }}
        function closeLightbox() {{ document.getElementById('lightbox').style.display = 'none'; }}
    </script>
    </head><body>
    <h1>CATÁLOGO MASTER - ALPHAFEST ITATIBA</h1>
    <div class="capa">
        <h3>Menu de Categorias:</h3>
        <ul>{capa_links}</ul>
    </div>
    <div id="lightbox" class="lightbox" onclick="closeLightbox()">
        <span class="close-btn">&times;</span>
        <img id="full-img" class="lightbox-img">
    </div>
    """
    
    for i, (categoria, group) in enumerate(df.groupby('Categoria')):
        id_cat = categoria.replace(" ", "_")
        html += f"<div id='{id_cat}' class='categoria-section'><h2 class='categoria-titulo'>📂 {categoria}</h2><div class='card-container'>"
        for _, p in group.iterrows():
            html += f"""<div class="card"><img src="{p['Imagem']}" onclick="openLightbox('{p['Imagem']}')"><div><h2>{p['Nome_Exibicao']}</h2><p>{p['Descrição']}</p></div></div>"""
        html += "</div></div>"
        
    return html + "</body></html>"

# --- INTERFACE ---
st.set_page_config(page_title="Catálogo Master", layout="wide")
st.title("📦 ALPHAFEST - Gestor de Catálogo Master")

# 1. Painel de Adição
c1, c2 = st.columns(2)

with c1:
    st.subheader("🔗 Adicionar via Link")
    # CAMPO DE CATEGORIA PARA LINKS
    cat_link = st.text_input("Qual a Categoria deste Link?", "Outros")
    link = st.text_area("Cole a URL da Imagem:", height=100)
    nome_prod_link = st.text_input("Nome do Produto (Link):", "Produto 3D")
    if st.button("Adicionar Link"):
        if link:
            img_b64 = obter_imagem_como_base64(link)
            st.session_state.produtos_totais.append({
                "Nome_Exibicao": nome_prod_link, 
                "Imagem": img_b64, 
                "Descrição": gerar_anuncio_ia(nome_prod_link), 
                "Categoria": cat_link
            })
            st.rerun()

with c2:
    st.subheader("📁 Adicionar via Upload")
    # CAMPO DE CATEGORIA PARA UPLOAD
    cat_up = st.text_input("Qual a Categoria deste Upload?", "Outros")
    foto = st.file_uploader("Subir foto", type=['jpg', 'png', 'jpeg', 'webp'], key="up")
    nome_prod_up = st.text_input("Nome do Produto (Upload):", "Produto Personalizado")
    if st.button("Adicionar Foto"):
        if foto:
            st.session_state.produtos_totais.append({
                "Nome_Exibicao": nome_prod_up, 
                "Imagem": image_to_base64(foto), 
                "Descrição": gerar_anuncio_ia(nome_prod_up), 
                "Categoria": cat_up
            })
            st.rerun()

# 2. Ações do Catálogo
st.divider()
if st.button("GERAR CATÁLOGO MASTER FINAL"):
    if st.session_state.produtos_totais:
        st.download_button("🖨️ Baixar HTML Master", gerar_html_catalogo(st.session_state.produtos_totais), "catalogo_master.html", "text/html")
    else:
        st.warning("Adicione produtos primeiro!")

if st.button("Limpar Tudo e Recomeçar"):
    st.session_state.produtos_totais = []
    st.rerun()

# 3. Tabela de Controle (Visão do que já foi adicionado)
if st.session_state.produtos_totais:
    st.divider()
    st.subheader("Itens Adicionados (Prévia)")
    df = pd.DataFrame(st.session_state.produtos_totais)
    st.dataframe(df[['Categoria', 'Nome_Exibicao']])
