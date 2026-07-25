import streamlit as st
import pandas as pd
import io
import base64
from groq import Groq

# --- CONFIGURAÇÕES ---
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- INICIALIZAÇÃO DE ESTADO ---
if 'produtos_lista' not in st.session_state:
    st.session_state.produtos_lista = []

# --- FUNÇÕES ---

def image_to_base64(uploaded_file):
    """Converte o arquivo de imagem para base64 para embutir no HTML."""
    bytes_data = uploaded_file.getvalue()
    b64 = base64.b64encode(bytes_data).decode()
    return f"data:image/jpeg;base64,{b64}"

def gerar_anuncio_ia(nome_produto, detalhes):
    """Gera descrição focada apenas nos detalhes fornecidos."""
    prompt = f"Produto: {nome_produto}. Detalhes técnicos e tema: {detalhes}. Escreva uma descrição curta, profissional e vendedora, focada em decoração de festas."
    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um especialista de marketing da ALPHAFEST ITATIBA. Escreva anúncios curtos e persuasivos. Use apenas os detalhes fornecidos pelo vendedor. Não invente nada."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content
    except: return f"{nome_produto} de alta qualidade."

def gerar_html_catalogo(df, lote):
    html = f"""<!DOCTYPE html><html><head><style>body{{font-family:sans-serif; padding:30px;}} .card{{display:flex; border-left:8px solid #3498db; padding:20px; margin-bottom:20px; box-shadow:0 2px 5px #ccc;}} img{{width:150px; height:150px; object-fit:cover; margin-right:20px;}}</style></head><body><h1>Lote: {lote}</h1>"""
    for _, row in df.iterrows():
        html += f"""<div class="card"><img src="{row['Imagem_B64']}"><div><h2>{row['Nome_Exibicao']}</h2><p>{row['Descrição']}</p></div></div>"""
    return html + "</body></html>"

# --- INTERFACE ---
st.set_page_config(page_title="Catálogo Alphafest", layout="wide")
st.title("📦 ALPHAFEST ITATIBA - Gerador de Catálogo")

nome_lote = st.text_input("Nome do Lote:", key="lote_input")

st.subheader("Adicionar Produto")
col_upload, col_detalhes = st.columns(2)
foto_file = col_upload.file_uploader("Subir foto do produto", type=['jpg', 'jpeg', 'png'])
detalhes_manual = col_detalhes.text_area("Detalhes do Produto (Tema, características, etc):", height=100)

if st.button("Adicionar ao Lote"):
    if foto_file and detalhes_manual:
        st.session_state.produtos_lista.append({
            "Imagem_B64": image_to_base64(foto_file),
            "Detalhes": detalhes_manual
        })
        st.toast("Produto adicionado!")
    else:
        st.error("Por favor, selecione uma foto e digite os detalhes.")

# Exibição do que foi adicionado
if st.session_state.produtos_lista:
    st.divider()
    st.write(f"Produtos no Lote atual: {len(st.session_state.produtos_lista)}")
    
    if st.button("Gerar Catálogo Final"):
        dados = []
        for p in st.session_state.produtos_lista:
            dados.append({
                "Nome_Exibicao": nome_lote,
                "Imagem_B64": p['Imagem_B64'],
                "Descrição": gerar_anuncio_ia(nome_lote, p['Detalhes'])
            })
        
        df = pd.DataFrame(dados)
        st.success("Catálogo gerado!")
        
        c1, c2 = st.columns(2)
        buffer_excel = io.BytesIO()
        df.to_excel(buffer_excel, index=False)
        c1.download_button("📊 Baixar Excel", buffer_excel, "catalogo.xlsx")
        c2.download_button("🖨️ Baixar HTML p/ Impressão", gerar_html_catalogo(df, nome_lote), "catalogo.html", "text/html")
        
        # Limpar estado após gerar
        if st.button("Limpar Tudo para Novo Lote"):
            st.session_state.produtos_lista = []
            st.rerun()
