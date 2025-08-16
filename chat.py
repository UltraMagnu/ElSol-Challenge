# Importa la biblioteca 'os' para interactuar con el sistema operativo,
# lo que nos permite acceder a las variables de entorno.
import os
# Importa la biblioteca de Azure Cognitive Services Speech SDK para
# realizar operaciones de voz, como el reconocimiento.
import azure.cognitiveservices.speech as speechsdk

def recognize_from_microphone():
    """
    Función que inicializa el servicio de reconocimiento de voz
    y transcribe el audio de una sola frase desde el micrófono.
    """
    # 1. Configuración del servicio de voz:
    # Obtiene la clave de suscripción y la región de Azure desde las variables de entorno.
    # Es una buena práctica usar variables de entorno para las credenciales,
    # ya que evita exponer información sensible en el código.
    speech_config = speechsdk.SpeechConfig(
        subscription=os.getenv("AZURE_SPEECH_KEY"), 
        region=os.getenv("AZURE_REGION")
    )
    
    # 2. Configuración de entrada de audio:
    # Crea una configuración de audio que especifica que la entrada
    # provendrá del micrófono predeterminado del sistema.
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    
    # 3. Creación del reconocedor de voz:
    # Instancia un objeto 'SpeechRecognizer' que se encargará de escuchar
    # y procesar el audio. Combina las configuraciones de voz y audio.
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, 
        audio_config=audio_config
    )

    print("📢 Por favor, diga algo...")
    
    # 4. Reconocimiento de una sola frase:
    # Llama al método 'recognize_once()', que escucha hasta que se detecta
    # un silencio prolongado o un final de frase, y luego devuelve el resultado.
    result = recognizer.recognize_once()

    # 5. Manejo de resultados:
    # Evalúa el resultado del reconocimiento para determinar si fue exitoso,
    # si no se detectó habla, o si hubo un error.
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        # Si el habla fue reconocida, imprime el texto transcrito.
        print(f"✅ Reconocido: {result.text}")
    elif result.reason == speechsdk.ResultReason.NoMatch:
        # Si no se pudo encontrar una coincidencia para el audio,
        # significa que no se reconoció el habla.
        print("🤷 No se pudo reconocer el habla.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        # Si el reconocimiento fue cancelado, por ejemplo, por un error en la conexión.
        # Aquí se corrige el error de sintaxis: 'cancellation_details' se obtiene directamente del 'result'.
        cancellation_details = result.cancellation_details
        print(f"❌ Reconocimiento cancelado: {cancellation_details.reason}")
        
        # Si la cancelación se debió a un error, se imprimen los detalles.
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Detalles del error: {cancellation_details.error_details}")
            print("¿Configuró correctamente su clave de recursos de voz y los valores de la región?")

# Ejecución de la función principal.
# Llama a la función que inicia todo el proceso de reconocimiento.
recognize_from_microphone()