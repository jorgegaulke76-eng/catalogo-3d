import streamlit as st
import pandas as pd
import io
import requests
import base64
from groq import Groq
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# --- CONFIGURAÇÕES ---
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- INICIALIZAÇÃO DE ESTADO ---
if "produtos_totais" not in st.session_state: st.session_state.produtos_totais = []

# --- FUNÇÕES ---

def obter_imagem_como_base64(url):
    """Busca a imagem e converte para base64 para contornar bloqueios."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': url # Tenta enganar o site dizendo que o pedido veio dele mesmo
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        # Se for um link de página (não de imagem), tenta achar a imagem principal
        if 'text/html' in response.headers.get('Content-Type', ''):
            soup = BeautifulSoup(response.content, 'html.parser')
            meta = soup.find("meta", property="og:image")
            if meta and meta.get("content"):
                return obter_imagem_como_base64(meta["content"]) # Recursivo
            return "https://i.ibb.co/kV0jyTfK/logo.png"

        # Converte a imagem baixada para base64
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

def gerar_html_catalogo(lista_produtos, lote):
    df = pd.DataFrame(lista_produtos)
    html = f"""<!DOCTYPE html><html><head><style>
        body{{font-family:sans-serif; padding:30px;}} 
        .card{{display:flex; border-left:8px solid #3498db; padding:20px; margin-bottom:20px; box-shadow:0 2px 5px #ccc;}} 
        img{{width:150px; height:150px; object-fit:cover; margin-right:20px;}}
        .categoria-titulo{{color:#2c3e50; border-bottom:2px solid #3498db; margin-top:30px; padding-bottom:10px;}}
    </style></head><body><h1>Catálogo: {lote}</h1>"""
    
    for categoria, group in df.groupby('Categoria'):
        html += f"<h2 class='categoria-titulo'>{categoria}</h2>"
        for _, p in group.iterrows():
            html += f"""<div class="card"><img src="{p['Imagem']}"><div><h2>{p['Nome_Exibicao']}</h2><p>{p['Descrição']}</p></div></div>"""
    return html + "</body></html>"

# --- INTERFACE ---
st.set_page_config(page_title="Catálogo Alphafest", layout="wide")
st.title("📦 ALPHAFEST ITATIBA - Gerador de Catálogo")

nome_lote = st.text_input("Nome do Lote:", "Lote Geral")

c1, c2 = st.columns(2)

with c1:
    st.subheader("🔗 Adicionar via Link")
    cat_link = st.text_input("Categoria (para este link):", "Outros")
    st.info("💡 **DICA:** Se o link direto da imagem falhar, clique com botão direito na imagem original -> 'Copiar endereço da imagem' e cole aqui.")
    links_input = st.text_area("Cole a URL da Imagem:", height=100)
    if st.button("Adicionar Links ao Lote"):
        for linha in links_input.split('\n'):
            if not linha.strip(): continue
            partes = [p.strip() for p in linha.split('|')]
            link, desc = partes[0], (partes[1] if len(partes) > 1 else "")
            # Chama a nova função que baixa a foto
            img_b64 = obter_imagem_como_base64(link)
            st.session_state.produtos_totais.append({
                "Nome_Exibicao": nome_lote, "Imagem": img_b64, 
                "Descrição": gerar_anuncio_ia(nome_lote, desc), "Categoria": cat_link
            })
        st.rerun()

with c2:
    st.subheader("📁 Adicionar via Upload")
    cat_up = st.text_input("Categoria (para este upload):", "Outros")
    foto = st.file_uploader("Subir foto", type=['jpg', 'png', 'jpeg', 'webp'])
    desc_manual = st.text_area("Detalhes do produto:", height=60)
    if st.button("Adicionar Foto ao Lote"):
        if foto:
            st.session_state.produtos_totais.append({
                "Nome_Exibicao": nome_lote, "Imagem": image_to_base64(foto), 
                "Descrição": gerar_anuncio_ia(nome_lote, desc_manual), "Categoria": cat_up
            })
            st.rerun()

st.divider()
col_btn1, col_btn2 = st.columns(2)

if col_btn1.button("Gerar Arquivos Finais (Excel + HTML)"):
    if st.session_state.produtos_totais:
        df = pd.DataFrame(st.session_state.produtos_totais)
        buf_excel = io.BytesIO()
        df.to_excel(buf_excel, index=False)
        st.download_button("📊 Baixar Excel", buf_excel, "catalogo.xlsx")
        st.download_button("🖨️ Baixar HTML Agrupado", gerar_html_catalogo(st.session_state.produtos_totais, nome_lote), "catalogo.html", "text/html")
    else:
        st.warning("Adicione produtos primeiro!")

if col_btn2.button("Limpar Tudo e Recomeçar"):
    st.session_state.produtos_totais = []
    st.rerun()

if st.session_state.produtos_totais:
    st.divider()
    st.subheader(f"Prévia do Catálogo ({len(st.session_state.produtos_totais)} itens)")
    df_preview = pd.DataFrame(st.session_state.produtos_totais)
    for categoria, group in df_preview.groupby('Categoria'):
        st.write(f"### 📂 {categoria}")
        for _, row in group.iterrows():
            with st.container(border=True):
                cols = st.columns([1, 4])
                cols[0].image(row['Imagem'], use_column_width=True)
                cols[1].subheader(row['Nome_Exibicao'])
                cols[1].write(row['Descrição'])
