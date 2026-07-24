import streamlit as st
import pandas as pd
import io
import requests
import re  # Nova importação necessária
from groq import Groq

# --- CONFIGURAÇÕES ---
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- FUNÇÕES ---

def obter_imagem_original(url):
    try:
        api_url = f"https://api.microlink.io?url={url}"
        response = requests.get(api_url)
        data = response.json()
        if 'data' in data and 'image' in data['data']:
            return data['data']['image']['url']
        return None
    except:
        return None

def extrair_nome_do_link(link):
    """Extrai o nome do produto, removendo o ID numérico inicial."""
    parte_final = link.split('/')[-1].split('?')[0]
    # Remove a sequência de números no início seguida de hífen (ex: "2894633-")
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
                {"role": "system", "content": "Você é o especialista de marketing da ALPHAFEST ITATIBA. Escreva anúncios persuasivos para peças 3D. Máximo 2 parágrafos."},
                {"role": "user", "content": f"Crie um anúncio de vendas para: {nome_produto}"}
            ],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content
    except:
        return "Peça 3D Alphafest de alta precisão."

def gerar_html_catalogo(df, lote):
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
            .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; }}
            .card {{ border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 10px; display: flex; align-items: center; }}
            .card img {{ width: 200px; height: 200px; object-fit: cover; border-radius: 10px; margin-right: 20px; }}
            .info {{ flex: 1; }}
            .price {{ font-weight: bold; color: #d32f2f; font-size: 1.2em; }}
        </style>
    </head>
    <body>
        <div class="header"><h1>Catálogo Alphafest: {lote}</h1></div>
    """
    for _, row in df.iterrows():
        html += f"""
        <div class="card">
            <img src="{row['Imagem']}">
            <div class="info">
                <h2>{row['Nome_Exibicao']}</h2>
                <p>{row['Descrição']}</p>
                <p class="price">Preço: R$ {row['Preço Venda (R$)']:.2f}</p>
            </div>
        </div>
        """
    html += "</body></html>"
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
links_input = st.text_area("Cole os links dos produtos (um por linha):")

if st.button("Gerar Catálogo"):
    if not links_input:
        st.warning("Insira ao menos um link!")
    else:
        linhas = links_input.split('\n')
        dados_catalogo = []
        
        with st.spinner("Gerando catálogo profissional..."):
            for item in linhas:
                if not item.strip(): continue
                link = item.strip()
                nome_exibicao = extrair_nome_do_link(link)
                foto_url = obter_imagem_original(link)
                custo_total, preco_venda = calcular_preco(100.0, 2.0, preco_kg, margem, custo_hora, complexidade)
                
                dados_catalogo.append({
                    "Nome_Exibicao": nome_exibicao,
                    "Imagem": foto_url,
                    "Descrição": gerar_anuncio_ia(nome_exibicao),
                    "Custo (R$)": custo_total,
                    "Preço Venda (R$)": preco_venda
                })

            df = pd.DataFrame(dados_catalogo)
            
            # --- BOTÕES DE DOWNLOAD ---
            col1, col2 = st.columns(2)
            buffer_excel = io.BytesIO()
            df.to_excel(buffer_excel, index=False)
            col1.download_button("📊 Baixar Excel", buffer_excel, f"catalogo_{nome_lote}.xlsx")
            
            html_content = gerar_html_catalogo(df, nome_lote)
            col2.download_button("🖨️ Baixar Catálogo para Impressão (HTML)", html_content, f"catalogo_{nome_lote}.html", "text/html")
            
            # Exibição
            for _, row in df.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 2, 1])
                    with c1:
                        if row["Imagem"]: st.markdown(f'<img src="{row["Imagem"]}" style="width: 100%; border-radius: 10px;">', unsafe_allow_html=True)
                    with c2:
                        st.write(f"### {row['Nome_Exibicao']}")
                        st.write(row['Descrição'])
                    with c3:
                        st.metric("Venda", f"R$ {row['Preço Venda (R$)']:.2f}")
                    
                    st.divider()
                    texto_social = f"🚀 {row['Nome_Exibicao']} - Alphafest Itatiba\n\n{row['Descrição']}\n\n💰 Apenas R$ {row['Preço Venda (R$)']:.2f}\n📦 Encomende a sua agora!"
                    st.text_area("Copie p/ Redes:", value=texto_social, height=100, key=f"text_{row['Nome_Exibicao']}")
            
            st.success("Catálogo gerado com sucesso!")
