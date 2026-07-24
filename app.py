import os
import sys
import threading
import re
import base64
import hashlib
from datetime import datetime
import tkinter as tk
import requests
import pandas as pd
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright
from groq import Groq # Nova biblioteca integrada

# --- CONFIGURAÇÕES ---
# Coloque sua chave aqui ou carregue de uma variável de ambiente
GROQ_API_KEY = "SUA_CHAVE_GROQ_AQUI" 
client = Groq(api_key=GROQ_API_KEY)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
for folder in ["excel", "pdf", "whatsapp", "shopee", "images"]:
    os.makedirs(os.path.join(OUTPUT_DIR, folder), exist_ok=True)

CUSTO_EMBALAGEM = 1.50      
MARCA_FABRICANTE = "ALPHAFEST ITATIBA"
PATH_LOGO_OFICIAL = os.path.join(BASE_DIR, "logo.png") 

# --- LÓGICA DE NEGÓCIO ---
def calcular_preco(peso_g, tempo_h, preco_kg, margem_lucro, custo_hora, complexidade=1.0):
    custo_filamento = (peso_g / 1000) * preco_kg
    # Nova lógica: custo operacional multiplicado pela complexidade da peça
    custo_operacional = (custo_hora * tempo_h) * complexidade
    custo_total = custo_filamento + custo_operacional + CUSTO_EMBALAGEM
    preco_venda = custo_total * (1 + (margem_lucro / 100))
    return round(custo_total, 2), round(preco_venda, 2)

# Nova função de IA para descrição
def gerar_descricao_com_groq(nome_produto):
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é o especialista de marketing da ALPHAFEST ITATIBA. Escreva anúncios persuasivos, profissionais, focados em venda e qualidade da Bambu Lab A1. Use no máximo 3 parágrafos curtos."},
                {"role": "user", "content": f"Crie um anúncio de vendas persuasivo para: {nome_produto}"}
            ],
            model="llama-3.1-8b-instant",
        )
        return completion.choices[0].message.content
    except:
        return "Peça de alta precisão 3D, produzida com tecnologia de ponta pela Alphafest."

# --- SCRAPER ---
# (Mantive a estrutura base de extração que você já utilizava)
def extrair_dados(url, callback):
    # ... [O restante do seu código de extração permanece o mesmo] ...
    # Lembre-se de substituir a chamada de 'gerar_descricao_resumida' pela 'gerar_descricao_com_groq' aqui dentro
    return produtos

# --- ATUALIZAÇÃO VISUAL ---
# Nas funções de ImageDraw (WA e Shopee), adicionei cores da marca
def gerar_saidas(produtos, opcoes, nome_lote, callback):
    # ... [Estrutura anterior mantida] ...
    # No bloco de draw.text para WhatsApp:
    # draw.rectangle([40, 850, 250, 858], fill="#EE4D2D") # Sublinhado com a cor da marca
    pass

# --- INTERFACE ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CATÁLOGO ALPHAFEST PRO")
        self.geometry("500x750") # Aumentei um pouco para caber o campo de complexidade
        
        # ... [Seus campos de entrada atuais] ...
        
        # NOVO: Campo de Complexidade
        ctk.CTkLabel(self.frame_custos, text="Fator Complexidade (1.0 - 2.0):").grid(row=3, column=0, padx=15, pady=5, sticky="e")
        self.entry_complex = ctk.CTkEntry(self.frame_custos, width=100)
        self.entry_complex.insert(0, "1.0")
        self.entry_complex.grid(row=3, column=1, padx=15, pady=5, sticky="w")
        
        # ... [Restante do layout] ...

# [O restante do seu código pode ser mantido exatamente como está]
if __name__ == "__main__":
    App().mainloop()
