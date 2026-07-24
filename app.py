import streamlit as st
import pandas as pd
import io
import urllib.parse
from groq import Groq

# --- CONFIGURAÇÕES ---
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- FUNÇÕES ---
def gerar_url_imagem(nome_produto):
    nome_limpo = nome_produto.split('/')[-1].replace('-', ' ').split('?')[0]
    prompt = f"{nome_limpo} 3d printed object"
    return f"https://pollinations.ai/p/{urllib.parse.quote(prompt)}?nologo=true"

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
links_input = st.text_area("Cole os nomes ou links (um por linha):")

if st.button("Gerar Catálogo"):
    if not links_input:
        st.warning("Insira ao menos um produto!")
    else:
        linhas = links_input.split('\n')
        dados_catalogo = []
        
        with st.spinner("Gerando dados e imagens..."):
            for i, item in enumerate(linhas):
                if not item.strip(): continue
                nome = item.strip()
                peso, tempo = 100.0, 2.0 
                custo_total, preco_venda = calcular_preco(peso, tempo, preco_kg, margem, custo_hora, complexidade)
                
                dados_catalogo.append({
                    "Produto": nome,
                    "Imagem": gerar_url_imagem(nome),
                    "Descrição": gerar_anuncio_ia(nome),
                    "Custo (R$)": custo_total,
                    "Preço Venda (R$)": preco_venda
                })

            df = pd.DataFrame(dados_catalogo)
            
            # Botão Excel
            buffer = io.BytesIO()
            df.to_excel(buffer, index=False)
            st.download_button("📥 Baixar Excel", buffer, f"catalogo_{nome_lote}.xlsx", "application/vnd.ms-excel")
            
            # Layout em Cartões
            # Layout em Cartões com renderização via HTML (mais robusta)
            st.subheader("Catálogo Gerado")
            for _, row in df.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 2, 1])
                    with c1:
                        # Usamos markdown com HTML para forçar o carregamento da imagem
                        st.markdown(
                            f'<img src="{row["Imagem"]}" style="width: 100%; border-radius: 10px;">', 
                            unsafe_allow_html=True
                        )
                    with c2:
                        st.write(f"### {row['Produto']}")
                        st.write(row['Descrição'])
                    with c3:
                        st.metric("Custo", f"R$ {row['Custo (R$)']:.2f}")
                        st.metric("Venda", f"R$ {row['Preço Venda (R$)']:.2f}")
            
            st.success("Catálogo gerado com sucesso!")
