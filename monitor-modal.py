import os
import modal
from modal import App, Image, Period

# Substitua pela URL exata do evento na FeverUp
URL_EVENTO = "https://feverup.com/m/660975"

# Data alvo no formato aria-label da página (dia-mês-ano)
DATA_ALVO_LABEL = "5-9-2026"

# Imagem com Playwright + Chromium instalados (modal gerencia na nuvem)
image = (
    Image.debian_slim()
    .pip_install("playwright", "httpx")
    .run_commands("playwright install --with-deps chromium")
)

app = App("ticket-notification")


async def notificar_discord(discord_webhook_url, mensagem):
    import httpx

    await httpx.AsyncClient().post(discord_webhook_url, json={"content": mensagem})


@app.function(
    image=image,
    schedule=Period(hours=1),
    secrets=[modal.Secret.from_name("discord-secret")],
)
async def monitorar():
    from playwright.async_api import async_playwright

    discord_webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

    async with async_playwright() as p:
        # Abre o Chromium sem interface gráfica
        browser = await p.chromium.launch(headless=True)

        # Configura um contexto de usuário real
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            locale="pt-BR",
        )

        page = await context.new_page()
        print(f"Acessando: {URL_EVENTO}")

        # Navega e aguarda o calendário carregar (espera o JS rodar)
        await page.goto(URL_EVENTO, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_selector(
            f'[aria-label="{DATA_ALVO_LABEL}"] .calendar__date', timeout=30000
        )

        print(f"Página carregada com sucesso! Título: {await page.title()}")

        # Localiza o dia alvo no calendário
        dia_alvo = page.locator(f'[aria-label="{DATA_ALVO_LABEL}"] .calendar__date')
        classe = await dia_alvo.get_attribute("class")

        if "calendar__date--soldout" not in classe:
            print("Ingressos disponíveis para o dia 05/09!")
            await notificar_discord(
                discord_webhook_url,
                "@everyone\n"
                "🚨🚨🚨 **INGRESSOS LIBERADOS PARA O DIA 05/09/2026!** 🚨🚨🚨\n\n"
                "🟢 **STATUS:** `DISPONÍVEL`\n"
                f"⚡ **CORRA PARA COMPRAR AGORA:**\n{URL_EVENTO}",
            )
        else:
            print("Ingresso para o dia 5 ainda não disponível, aguarde mais um pouco")
            await notificar_discord(
                discord_webhook_url,
                "ℹ️ **[Monitor FeverUp - Checagem Horária]**\n"
                "📅 **Data:** 05/09/2026\n"
                "🔴 **Status:** `Esgotado`\n"
                "_Os ingressos permanecem indisponíveis no momento._",
            )

        await browser.close()
