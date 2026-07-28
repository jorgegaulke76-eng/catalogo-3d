import streamlit as st
import pandas as pd
import json
import os
import base64

# Configurações do App
st.set_page_config(page_title="Gestor Alphafest Master", layout="wide")
DB_FILE = "catalogo_db.json"
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

# Inicialização
if "produtos_totais" not in st.session_state: st.session_state.produtos_totais = carregar_catalogo()

# --- INTERFACE ---
c_left, c_main, c_right = st.columns([1, 6, 1])
with c_main:
    st.title("Gestor Alphafest Master")
    
    # 3. Listagem com Proteção Extrema
    st.subheader("📦 Produtos Cadastrados")
    
    for i, p in enumerate(st.session_state.produtos_totais):
        with st.container(border=True):
            c_row1, c_row2, c_row3 = st.columns([1, 5, 2])
            imgs = p.get('Imagens', [])
            
            # --- PROTEÇÃO ABSOLUTA ---
            # Aqui não usamos st.image diretamente na variável 'imgs[0]'
            # Verificamos primeiro se é uma string válida e se o arquivo existe
            caminho_imagem = imgs[0] if (imgs and len(imgs) > 0) else None
            
            if caminho_imagem and (caminho_imagem.startswith("http") or os.path.exists(caminho_imagem)):
                try:
                    c_row1.image(caminho_imagem, width=80)
                except Exception:
                    c_row1.write("Erro na imagem")
            else:
                c_row1.write("Sem imagem")
            # --------------------------
            
            c_row2.write(f"### {p.get('Nome')}")
            c_row2.write(f"**Preço:** R$ {p.get('Preco')}")
            
            if c_row3.button("🗑️ Excluir", key=f"d{i}"): 
                st.session_state.produtos_totais.pop(i)
                salvar_catalogo(st.session_state.produtos_totais)
                st.rerun()
