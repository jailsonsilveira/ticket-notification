import os
import requests

URL = "https://feverup.com/api/4.2/plans/660975/place/33214/availability/?from=2026-09-01&to=2026-09-13"
HEADERS = {"accept": "application/json"}

# Pega o Webhook (Discord/Telegram/etc) gravado no GitHub Secrets
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def enviar_notificacao(mensagem):
    if DISCORD_WEBHOOK_URL:
        payload = {"content": mensagem}
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    print(f"[NOTIFICAÇÃO ENVIADA] {mensagem}")

def monitorar_dia_cinco():
    data_alvo = "2026-09-05"
    
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            print(f"Erro na requisição. Status: {response.status_code}")
            return

        dados = response.json()
        datas = dados.get("dates", {})
        
        if data_alvo in datas:
            info_dia = datas[data_alvo]
            status = info_dia.get("status")
            ingressos = info_dia.get("total_available_tickets", 0)
            
            print(f"[{data_alvo}] Status atual: '{status}' | Ingressos disponíveis: {ingressos}")
            
            # Dispara se status for diferente de 'sold_out' OU se ingressos > 0
            if status != "sold_out" or ingressos > 0:
                preco = info_dia.get("min_ticket_price", "N/A")
                
                mensagem = (
                    f"🚨 **INGRESSOS DISPONÍVEIS PARA O DIA 05/09/2026!** 🚨\n\n"
                    f"• **Status:** {status}\n"
                    f"• **Ingressos livres:** {ingressos}\n"
                    f"• **Preço mínimo:** R$ {preco}\n\n"
                    f"👉 Corre para comprar: https://feverup.com/m/660975?&thm=14390"
                )
                enviar_notificacao(mensagem)
            else:
                print("Continuam esgotados. Nenhuma notificação enviada.")
        else:
            print(f"A data {data_alvo} não foi retornada pela API.")

    except Exception as e:
        print(f"Erro ao executar verificação: {e}")

if __name__ == "__main__":
    monitorar_dia_cinco()