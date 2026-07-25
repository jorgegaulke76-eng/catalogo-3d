import streamlit as st
import pandas as pd
import io
import requests
import re
from groq import Groq

# --- CONFIGURAÇÕES ---
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Rodapé fixo para padronizar todos os anúncios
RODAPE_PADRAO = "\n\n--- 📦 ALPHAFEST ITATIBA ---\n✅ Entrega rápida e gratuita para o interior do Brasil.\n✅ Assistência técnica completa.\n✅ Condições especiais para pedidos acima de R$ 1.999,99."

# --- FUNÇÕES ---

def obter_imagem_original(url):
    """Busca a foto oficial ou retorna o logo como reserva se falhar."""
    try:
        api_url = f"https://api.microlink.io?url={url}"
        response = requests.get(api_url, timeout=10)
        data = response.json()
        if 'data' in data and 'image' in data['data'] and data['data']['image']['url']:
            return data['data']['image']['url']
    except:
        pass
    
    # Se falhar, retorna o link do seu logo como reserva (fallback)
    return "https://i.ibb.co/kV0jyTfK/logo.png"

def extrair_nome_do_link(link):
    parte_final = link.split('/')[-1].split('?')[0]
    nome = re.sub(r'^\d+-', '', parte_final)
    return nome.replace('-', ' ').title()

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
                {"role": "system", "content": "Você é o especialista de marketing da ALPHAFEST ITATIBA. Escreva anúncios persuasivos para peças 3D. Foque apenas nas características da peça, no uso e no desejo de compra. Não fale de frete, preços ou garantias."},
                {"role": "user", "content": f"Crie um anúncio de vendas persuasivo para a peça: {nome_produto}"}
            ],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content
    except:
        return f"{nome_produto} de alta precisão. Qualidade e acabamento premium Alphafest."

def gerar_html_catalogo(df, lote):
    logo_url = "https://i.ibb.co/kV0jyTfK/logo.png" 
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Roboto, sans-serif; background-color: #eef2f3; padding: 30px; }}
            .catalog-page {{ max-width: 850px; margin: auto; background: #fff; padding: 40px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; margin-bottom: 40px; border-bottom: 3px solid #34495e; padding-bottom: 20px; }}
            .logo {{ max-width: 200px; margin-bottom: 15px; }}
            .header h1 {{ margin: 0; color: #2c3e50; font-size: 2.2em; text-transform: uppercase; }}
            .header p {{ color: #7f8c8d; font-size: 1.1em; }}
            .card {{ display: flex; align-items: flex-start; background: #fff; border-left: 8px solid #3498db; padding: 25px; margin-bottom: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            .card img {{ width: 220px; height: 220px; object-fit: cover; border-radius: 8px; margin-right: 30px; border: 1px solid #ddd; }}
            .content {{ flex: 1; }}
            .content h2 {{ margin: 0 0 15px 0; color: #2c3e50; font-size: 1.6em; }}
            .content p {{ font-size: 1em; color: #555; line-height: 1.6; margin-bottom: 15px; white-space: pre-line; }}
            .price-tag {{ display: inline-block; background: #27ae60; color: white; padding: 8px 20px; border-radius: 5px; font-weight: bold; font-size: 1.2em; }}
            @media print {{ body {{ background: white; }} .catalog-page {{ box-shadow: none; }} .card {{ break-inside: avoid; border: 1px solid #ddd; }} }}
        </style>
    </head>
    <body>
        <div class="catalog-page">
            <div class="header">
                <img src="{logo_url}" class="logo" alt="Logo Alphafest">
                <h1>Catálogo Alphafest</h1>
                <p>Lote: {lote}</p>
            </div>
    """
    for _, row in df.iterrows():
        descricao_completa = row['Descrição'] + RODAPE_PADRAO
        html += f"""
        <div class="card">
            <img src="{row['Imagem']}" alt="Produto">
            <div class="content">
                <h2>{row['Nome_Exibicao']}</h2>
                <p>{descricao_completa}</p>
                <div class="price-tag">R$ {row['Preço Venda (R$)']:.2f}</div>
            </div>
        </div>
        """
    html += "</div></body></html>"
    return html

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
links_input = st.text_area("Cole os links (um por linha):")

if st.button("Gerar Catálogo"):
    if not links_input:
        st.warning("Insira links!")
    else:
        linhas = links_input.split('\n')
        dados_catalogo = []
        with st.spinner("Processando..."):
            for item in linhas:
                if not item.strip(): continue
                link = item.strip()
                nome = extrair_nome_do_link(link)
                custo, venda = calcular_preco(100.0, 2.0, preco_kg, margem, custo_hora, complexidade)
                dados_catalogo.append({
                    "Nome_Exibicao": nome,
                    "Imagem": obter_imagem_original(link),
                    "Descrição": gerar_anuncio_ia(nome),
                    "Custo (R$)": custo,
                    "Preço Venda (R$)": venda
                })

            df = pd.DataFrame(dados_catalogo)
            
            # Botões
            c1, c2 = st.columns(2)
            buffer_excel = io.BytesIO()
            df.to_excel(buffer_excel, index=False)
            c1.download_button("📊 Baixar Excel", buffer_excel, "catalogo.xlsx")
            c2.download_button("🖨️ Baixar HTML p/ Impressão", gerar_html_catalogo(df, nome_lote), "catalogo.html", "text/html")
            
            st.divider()
            st.subheader("Prévia do Catálogo")
            for _, row in df.iterrows():
                # A prévia mostra apenas a descrição da IA
                descricao_limpa = row['Descrição']
                texto_para_redes = row['Descrição'] + RODAPE_PADRAO
                
                with st.container(border=True):
                    cols = st.columns([1, 3])
                    cols[0].markdown(f'<img src="{row["Imagem"]}" style="width: 100%; border-radius: 8px;">', unsafe_allow_html=True)
                    cols[1].write(f"### {row['Nome_Exibicao']}")
                    cols[1].write(descricao_limpa)
                    cols[1].metric("Preço de Venda", f"R$ {row['Preço Venda (R$)']:.2f}")
                    st.text_area("Copie p/ Redes:", value=f"🚀 {row['Nome_Exibicao']}\n\n{texto_para_redes}\n\n💰 R$ {row['Preço Venda (R$)']:.2f}", height=150, key=f"txt_{row['Nome_Exibicao']}")
