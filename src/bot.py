
import openai
import requests
import time
import os
from dotenv import load_dotenv
from logger import logger  


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
telegram_token = os.getenv("TELEGRAM_TOKEN")

def get_updates(offset):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        params = {"timeout": 100, "offset": offset}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.json().get("result", [])
        else:
            logger.error(f"Error en Telegram API: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logger.error(f"Error obteniendo actualizaciones: {e}")
        return []

def send_messages(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        params = {"chat_id": chat_id, "text": text}
        response = requests.post(url, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error al enviar mensaje: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error enviando mensaje: {e}")
        return None

def get_openai_response(prompt):
    try:
        model_engine = "gpt-3.5-turbo"
        response = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=150,  
            n=1,
            stop=None,  
            temperature=0.7 
        )

        if response and response.choices:
            return response.choices[0].text.strip()
        else:
            return "Lo siento, no entendí tu pregunta."
    except openai.error.OpenAIError as e:
        logger.error(f"Error en OpenAI: {e}")
        return "Lo siento, hubo un error procesando tu mensaje."

def main():
    logger.info("Bot iniciado correctamente.")
    offset = 0

    while True:
        try:
            updates = get_updates(offset)
            if updates:
                for update in updates:
                    
                    if "message" in update and "text" in update["message"]:
                        offset = update["update_id"] + 1
                        chat_id = update["message"]["chat"]['id']
                        user_message = update["message"]["text"]

                        logger.info(f"Mensaje recibido: {user_message}")

                        
                        if user_message == '/start':
                            send_messages(chat_id, "¡Hola! ¿En qué puedo ayudarte?")
                        elif user_message == '/help':
                            send_messages(chat_id, "Puedes preguntarme cualquier cosa y te responderé.")
                        else:
                            GPT = get_openai_response(user_message)
                            send_messages(chat_id, GPT)
            else:
                time.sleep(1)
        except Exception as e:
            logger.error(f"Error en el bucle principal: {e}")
            time.sleep(1)

if __name__ == '__main__':
    main()
