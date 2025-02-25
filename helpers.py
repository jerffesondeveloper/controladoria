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
    Envia mensagem via WhatsApp usando pywhatkit
    Mantém o navegador aberto para envios consecutivos
    Retorna: Tupla (sucesso, mensagem)
    """
    global browser_open
    
    if not Config.WHATSAPP_ENABLED:
        return (False, "Envio de WhatsApp desativado nas configurações")
    
    try:
        # Limpar número de telefone
        phone = ''.join(filter(str.isdigit, phone))
        
        # Adicionar código do país se não estiver presente
        if len(phone) == 11:  # DDD + número (Brasil)
            phone = "+55" + phone
        
        # Obter hora atual para envio imediato (com pequeno delay)
        now = datetime.now()
        hour = now.hour
        minute = now.minute + 1
        
        # Ajustar hora se o minuto for >= 60
        if minute >= 60:
            hour += 1
            minute -= 60
        
        # Configurar pywhatkit para não fechar o navegador
        kit.sendwhatmsg_instantly(
            phone, 
            message,
            wait_time=15,  # Tempo de espera para carregar o WhatsApp Web
            tab_close=False,  # Não fechar a aba
            close_time=3    # Tempo para manter a janela ativa após enviar
        )
        
        browser_open = True
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