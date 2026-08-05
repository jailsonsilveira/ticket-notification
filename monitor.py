import os
import requests
from playwright.sync_api import sync_playwright

# Substitua pela URL exata do evento na FeverUp
URL_EVENTO = "https://feverup.com/m/660975"

# Data alvo no formato aria-label da página (dia-mês-ano)
DATA_ALVO_LABEL = "5-9-2026"
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def notificar_discord(mensagem):
    if not DISCORD_WEBHOOK_URL:
        print("AVISO: DISCORD_WEBHOOK_URL não encontrada nas variáveis de ambiente.")
        return
    requests.post(DISCORD_WEBHOOK_URL, json={"content": mensagem})

def monitorar():
    with sync_playwright() as p:
        # Abre o Chromium sem interface gráfica
        browser = p.chromium.launch(headless=True)
        
        # Configura um contexto de usuário real
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            locale="pt-BR"
        )
        
        page = context.new_page()
        print(f"Acessando: {URL_EVENTO}")
        
        # Navega e aguarda o calendário carregar (espera o JS rodar)
        page.goto(URL_EVENTO, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector(f'[aria-label="{DATA_ALVO_LABEL}"] .calendar__date', timeout=30000)
        
        print(f"Página carregada com sucesso! Título: {page.title()}")
        
        # Localiza o dia alvo no calendário
        dia_alvo = page.locator(f'[aria-label="{DATA_ALVO_LABEL}"] .calendar__date')
        classe = dia_alvo.get_attribute("class")
        
        if "calendar__date--soldout" not in classe:
            print("Ingressos disponíveis para o dia 05/09!")
            notificar_discord(f"🚨 **INGRESSOS DISPONÍVEIS!**\nCorra para garantir o seu: {URL_EVENTO}")
        else:
            print("Ingresso para o dia 5 ainda não disponível, aguarde mais um pouco")
            
        browser.close()

if __name__ == "__main__":
    monitorar()