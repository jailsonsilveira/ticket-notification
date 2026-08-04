import os
import requests

URL = "https://feverup.com/api/4.2/plans/660975/place/33214/availability/?from=2026-09-01&to=2026-09-13"
HEADERS = {"accept": "application/json"}

# URL do Webhook do Discord armazenada no GitHub Secrets
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def enviar_notificacao_discord(mensagem):
    if DISCORD_WEBHOOK_URL:
        payload = {"content": mensagem}
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code in [200, 204]:
            print("Notificação enviada ao Discord com sucesso!")
        else:
            print(f"Erro ao enviar ao Discord: Status {response.status_code}")
    else:
        print("[ERRO] DISCORD_WEBHOOK_URL não configurado.")

def monitorar_dia_cinco():
    data_alvo = "2026-09-05"
    
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            msg_erro = f"⚠️ **[ALERTA DE SISTEMA]** Erro ao consultar a API da FeverUp. Status HTTP: {response.status_code}"
            enviar_notificacao_discord(msg_erro)
            return

        dados = response.json()
        datas = dados.get("dates", {})
        
        if data_alvo in datas:
            info_dia = datas[data_alvo]
            status = info_dia.get("status")
            ingressos = info_dia.get("total_available_tickets", 0)
            preco = info_dia.get("min_ticket_price", "N/A")
            
            print(f"[{data_alvo}] Status atual: '{status}' | Ingressos livres: {ingressos}")
            
            # --- CONDIÇÃO: INGRESSOS DISPONÍVEIS ---
            if status != "sold_out" or ingressos > 0:
                mensagem_disponivel = (
                    f"@everyone\n"  # Chama a atenção de todos no canal
                    f"🚨🚨🚨 **INGRESSOS LIBERADOS PARA O DIA 05/09/2026!** 🚨🚨🚨\n\n"
                    f"🟢 **STATUS:** `{status.upper()}`\n"
                    f"🎟️ **INGRESSOS DISPONÍVEIS:** `{ingressos}`\n"
                    f"💰 **PREÇO MÍNIMO:** `R$ {preco}`\n\n"
                    f"⚡ **CORRA PARA COMPRAR AGORA:**\n"
                    f"https://feverup.com/m/660975?&thm=14390"
                )
                enviar_notificacao_discord(mensagem_disponivel)

            # --- CONDIÇÃO: CONTINUA INDISPONÍVEL ---
            else:
                mensagem_indisponivel = (
                    f"ℹ️ **[Monitor FeverUp - Checagem Horária]**\n"
                    f"📅 **Data:** 05/09/2026\n"
                    f"🔴 **Status:** `Esgotado ({status})` | **Ingressos:** `{ingressos}`\n"
                    f"_Os ingressos permanecem indisponíveis no momento._"
                )
                enviar_notificacao_discord(mensagem_indisponivel)

        else:
            enviar_notificacao_discord(f"⚠️ A data `{data_alvo}` não foi encontrada na resposta da API.")

    except Exception as e:
        print(f"Erro ao executar verificação: {e}")
        enviar_notificacao_discord(f"❌ Erro interno no script de monitoramento: `{e}`")

if __name__ == "__main__":
    monitorar_dia_cinco()