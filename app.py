import streamlit as st
import pandas as pd
import io
import requests
import re
from groq import Groq
from bs4 import BeautifulSoup

# --- CONFIGURAÇÕES ---
# Lembre-se de manter sua chave GROQ_API_KEY configurada no Streamlit Cloud
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Rodapé removido conforme solicitado
RODAPE_PADRAO = ""

# --- FUNÇÕES ---

def obter_imagem_original(url):
    """Busca a imagem do produto: prioriza link direto ou busca via scraping."""
    # 1. Verifica se o link já é uma imagem (termina com .jpg, .png, etc)
    if url.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
        return url

    # 2. Se não for, tenta buscar no site (Scraping)
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        meta_image = soup.find("meta", property="og:image")
        if meta_image and meta_image.get("content"):
            return meta_image["content"]
            
        first_img = soup.find("img")
        if first_img and first_img.get("src"):
            return first_img["src"]
    except:
        pass
    
    # Fallback: retorna o logo se tudo falhar
    return "https://i.ibb.co/kV0jyTfK/logo.png"

def calcular_preco(peso_g, tempo_h, preco_kg, margem_lucro, custo_hora, complexidade):
    custo_filamento = (peso_g / 1000) * preco_kg
    custo_operacional = (custo_hora * tempo_h) * complexidade
    custo_total = custo_filamento + custo_operacional + 1.50
    preco_venda = custo_total * (1 + (margem_lucro / 100))
    return round(custo_total, 2), round(preco_venda, 2)

def gerar_anuncio_ia(nome_produto, contexto_manual=""):
    """Gera anúncio. Se o usuário fornecer um contexto manual, a IA o prioriza."""
    prompt_base = f"Crie um anúncio de vendas persuasivo para a peça: {nome_produto}."
    if contexto_manual:
        prompt_base += f"\n\nUse estas informações adicionais fornecidas pelo vendedor: {contexto_manual}"
    
    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é o especialista de marketing da ALPHAFEST ITATIBA. Escreva anúncios persuasivos, focando em benefícios, uso e desejo de compra. Não mencione frete, preços ou garantias."},
                {"role": "user", "content": prompt_base}
            ],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content
    except:
        return f"{nome_produto} de alta qualidade. Qualidade Alphafest."

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
st.info("💡 Dica: Você pode colar apenas o link, ou Link | Detalhes do produto.")
links_input = st.text_area("Cole os links (formato: URL | detalhes manuais):")

if st.button("Gerar Catálogo"):
    if not links_input:
        st.warning("Insira links!")
    else:
        linhas = links_input.split('\n')
        dados_catalogo = []
        with st.spinner("Processando..."):
            for item in linhas:
                if not item.strip(): continue
                
                # Separa o link do contexto manual se o "|" existir
                partes = item.split('|')
                link = partes[0].strip()
                contexto_manual = partes[1].strip() if len(partes) > 1 else ""
                
                # Usando nome_lote como título principal
                nome = nome_lote
                
                custo, venda = calcular_preco(100.0, 2.0, preco_kg, margem, custo_hora, complexidade)
                dados_catalogo.append({
                    "Nome_Exibicao": nome,
                    "Imagem": obter_imagem_original(link),
                    "Descrição": gerar_anuncio_ia(nome, contexto_manual),
                    "Custo (R$)": custo,
                    "Preço Venda (R$)": venda
                })

            df = pd.DataFrame(dados_catalogo)
            
            c1, c2 = st.columns(2)
            buffer_excel = io.BytesIO()
            df.to_excel(buffer_excel, index=False)
            c1.download_button("📊 Baixar Excel", buffer_excel, "catalogo.xlsx")
            c2.download_button("🖨️ Baixar HTML p/ Impressão", gerar_html_catalogo(df, nome_lote), "catalogo.html", "text/html")
            
            st.divider()
            st.subheader("Prévia do Catálogo")
            for _, row in df.iterrows():
                # Descrição limpa (sem rodapé)
                descricao_limpa = row['Descrição']
                texto_para_redes = row['Descrição'] + RODAPE_PADRAO
                
                with st.container(border=True):
                    cols = st.columns([1, 3])
                    cols[0].markdown(f'<img src="{row["Imagem"]}" style="width: 100%; border-radius: 8px;">', unsafe_allow_html=True)
                    cols[1].write(f"### {row['Nome_Exibicao']}")
                    cols[1].write(descricao_limpa)
                    cols[1].metric("Preço de Venda", f"R$ {row['Preço Venda (R$)']:.2f}")
                    st.text_area("Copie p/ Redes:", value=f"🚀 {row['Nome_Exibicao']}\n\n{texto_para_redes}\n\n💰 R$ {row['Preço Venda (R$)']:.2f}", height=150, key=f"txt_{row['Nome_Exibicao']}")
