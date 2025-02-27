import requests
from datetime import datetime
import pywhatkit as kit
import threading
import time
from config import Config
import os

def format_date(date):
    """Formata a data para exibição no formato brasileiro"""
    if isinstance(date, datetime):
        return date.strftime('%d/%m/%Y')
    return date

def format_datetime(dt):
    """Formata a data e hora para exibição no formato brasileiro"""
    if isinstance(dt, datetime):
        return dt.strftime('%d/%m/%Y %H:%M')
    return dt


browser_open = False

def send_whatsapp_message(phone, message):
    """
    Envia mensagem via WhatsApp ou simula o envio em ambientes sem interface gráfica
    Retorna: Tupla (sucesso, mensagem)
    """
    try:
        # Verificar se estamos em ambiente de produção
        import os
        is_production = os.environ.get('RAILWAY_ENVIRONMENT') == 'production'
        
        if is_production:
            # Em produção, apenas simular o envio
            print(f"[SIMULAÇÃO] Enviando WhatsApp para {phone}: {message}")
            return (True, "Mensagem simulada com sucesso (ambiente de produção)")
        
        # Se chegar aqui, estamos em ambiente local
        import pywhatkit as kit
        
        # Limpar número de telefone
        phone = ''.join(filter(str.isdigit, phone))
        
        # Adicionar código do país se não estiver presente
        if len(phone) == 11:  # DDD + número (Brasil)
            phone = "+55" + phone
        
        # Obter hora atual para envio imediato (com 1 minuto de delay)
        from datetime import datetime
        now = datetime.now()
        hour = now.hour
        minute = now.minute + 1
        
        # Ajustar hora se o minuto for >= 60
        if minute >= 60:
            hour += 1
            minute -= 60
        
        # Enviar mensagem
        kit.sendwhatmsg(phone, message, hour, minute, wait_time=15, tab_close=False)
        return (True, "Mensagem enviada com sucesso")
    
    except Exception as e:
        return (False, f"Erro ao enviar mensagem: {str(e)}")

def create_pendencia_message(pendencia, tipo="nova"):
    """Cria mensagem padrão para pendência"""
    if tipo == "nova":
        message = f"🔔 NOVA PENDÊNCIA REGISTRADA 🔔\n\n"
    elif tipo == "lembrete":
        message = f"🔔 LEMBRETE DE TAREFA PENDENTE 🔔\n\n"
    else:
        message = f"📝 INFORMAÇÃO SOBRE PENDÊNCIA 📝\n\n"
    
    message += f"*Pendencias:* {pendencia.descricao}\n"
    
   
    
    message += "\nPor favor, não esqueça de solucionar essas pendências\n\nControladoria Geral, PMPM"
    return message