# Importa las bibliotecas necesarias.
# 'os' para manejar variables de entorno.
# 'azure.cognitiveservices.speech' para el reconocimiento de voz y la síntesis de voz.
# 'openai' para interactuar con la API de Azure OpenAI.
from openai import AzureOpenAI
import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# --- Configuración de Azure OpenAI ---
# Inicializa el cliente de OpenAI con las credenciales de Azure.
# Las credenciales se obtienen de las variables de entorno.
try:
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2025-01-01-preview"
    )
    # Define el ID del despliegue del modelo (chat) que se usará.
    deployment_id = os.getenv("AZURE_OPENAI_DEPLOYMENT")
except Exception as e:
    print(f"Error al configurar Azure OpenAI: {e}")
    exit()

# --- Configuración de Azure Speech Service ---
# Configura las propiedades del servicio de voz (clave y región).
try:
    speech_config = speechsdk.SpeechConfig(
        subscription=os.getenv("AZURE_SPEECH_KEY"), 
        region=os.getenv("AZURE_REGION")
    )
    # Define el idioma para el reconocimiento de voz.
    speech_config.speech_recognition_language = "es-ES" 
    # Define la voz para la síntesis de voz (ej. en-US-JennyNeural para inglés, es-ES-ElviraNeural para español).
    speech_config.speech_synthesis_voice_name = "es-ES-ElviraNeural"

    # Configura la entrada de audio (micrófono predeterminado) y la salida (altavoz predeterminado).
    audio_config_in = speechsdk.audio.AudioConfig(use_default_microphone=True)
    audio_config_out = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    # Crea el reconocedor de voz.
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, 
        audio_config=audio_config_in
    )
    # Crea el sintetizador de voz.
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, 
        audio_config=audio_config_out
    )

except Exception as e:
    print(f"Error al configurar Azure Speech Service: {e}")
    exit()


def recognize_speech():
    """
    Escucha desde el micrófono y reconoce el habla del usuario.
    Retorna la transcripción si es exitosa, o None en caso de error o no reconocimiento.
    """
    print("📢 Diga algo por favor...")
    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"🗣️ Reconocido: {result.text}")
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("🤷 No se pudo reconocer el habla.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        # Manejo de errores de cancelación.
        cancellation_details = result.cancellation_details
        print(f"❌ Reconocimiento cancelado: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Detalles del error: {cancellation_details.error_details}")
    return None

def ask_azure_openai(prompt):
    """
    Envía una pregunta al chatbot de Azure OpenAI y reproduce la respuesta.
    """
    if not prompt:
        return

    print("🤖 Generando respuesta...")
    try:
        # Llama a la API de Azure OpenAI con el prompt del usuario.
        response = client.chat.completions.create(
            model=deployment_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        # Extrae el texto de la respuesta.
        full_response_text = response.choices[0].message.content
        print(f"✅ Respuesta del chatbot: {full_response_text}")

        # Sintetiza la respuesta para que el usuario la escuche.
        speech_synthesizer.speak_text_async(full_response_text).get()
    
    except Exception as e:
        print(f"Error al interactuar con el chatbot: {e}")

def main():
    """
    Función principal que ejecuta el ciclo de reconocimiento y respuesta.
    """
    # Escucha al usuario y obtiene la transcripción.
    user_text = recognize_speech()

    # Si se reconoció el habla, envía la transcripción al chatbot.
    if user_text:
        ask_azure_openai(user_text)

if __name__ == "__main__":
    main()
