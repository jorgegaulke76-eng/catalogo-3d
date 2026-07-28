import streamlit as st
import pandas as pd
import json
import os
import base64

# Configurações do App
st.set_page_config(page_title="Gestor Alphafest Master", layout="wide")

# MUDANÇA: Nome do arquivo alterado para forçar a limpeza do banco corrompido
DB_FILE = "catalogo_v3.json"
UPLOAD_DIR = "uploads"
LOGO_FILE = "logo.png"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# --- FUNÇÕES ---
def carregar_catalogo():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def salvar_catalogo(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4)

def get_image_base64(path):
    if not path or not os.path.exists(path): return ""
    try:
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            ext = os.path.splitext(path)[1].replace('.', '')
            return f"data:image/{ext};base64,{encoded}"
    except:
        return ""

# Inicialização
if "produtos_totais" not in st.session_state: st.session_state.produtos_totais = carregar_catalogo()
if "edit_index" not in st.session_state: st.session_state.edit_index = None

# --- GERADOR DE HTML ---
def gerar_html_master(lista, logo_path):
    df = pd.DataFrame(lista)
    categorias = df['Categoria'].unique() if not df.empty else []
    final_logo_src = get_image_base64(logo_path) if os.path.exists(logo_path) else ""
    
    html = f"<html><body><h1>Catálogo Alphafest</h1>"
    if not df.empty:
        for cat in categorias:
            html += f"<h2>{cat}</h2>"
            for _, p in df[df['Categoria'] == cat].iterrows():
                html += f"<div><h3>{p.get('Nome')}</h3><p>R$ {p.get('Preco')}</p></div>"
    html += "</body></html>"
    return html

# --- INTERFACE ---
c_left, c_main, c_right = st.columns([1, 6, 1])
with c_main:
    st.title("Gestor Alphafest Master")
    
    with st.expander("➕ Adicionar Produto"):
        cat = st.text_input("Categoria")
        nome = st.text_input("Nome do Produto")
        preco = st.text_input("Preço")
        upload = st.file_uploader("Upload Foto", type=['jpg', 'png', 'jpeg'])
        
        if st.button("✅ Salvar"):
            lista_imgs = []
            if upload:
                caminho = os.path.join(UPLOAD_DIR, upload.name)
                with open(caminho, "wb") as f: f.write(upload.getbuffer())
                lista_imgs.append(caminho)
            
            st.session_state.produtos_totais.append({"Nome": nome, "Categoria": cat, "Imagens": lista_imgs, "Preco": preco})
            salvar_catalogo(st.session_state.produtos_totais)
            st.rerun()

    st.divider()
    
    # LISTAGEM COM PROTEÇÃO TOTAL CONTRA O ERRO
    st.subheader("📦 Produtos Cadastrados")
    for i, p in enumerate(st.session_state.produtos_totais):
        with st.container(border=True):
            cols = st.columns([1, 4])
            
            # --- PROTEÇÃO CONTRA O ERRO DE IMAGEM ---
            img_path = p.get('Imagens', [])
            if img_path and len(img_path) > 0:
                if os.path.exists(img_path[0]):
                    try:
                        cols[0].image(img_path[0], width=80)
                    except:
                        cols[0].write("Erro foto")
                else:
                    cols[0].write("Foto não encontrada")
            else:
                cols[0].write("Sem foto")
            # ----------------------------------------
            
            cols[1].write(f"**{p.get('Nome')}** - R$ {p.get('Preco')}")
            
            if cols[1].button("🗑️ Excluir", key=f"d{i}"): 
                st.session_state.produtos_totais.pop(i)
                salvar_catalogo(st.session_state.produtos_totais)
                st.rerun()
