# Asistente de voz para Windows

Proyecto en Python basado en `Roadmap_Asistente_de_Voz.docx`. Esta entrega implementa los sprints **0, 1, 2 y 3** del MVP 0: escucha, comandos, búsqueda web, voz y personalidad. El MVP 0 completo del roadmap abarca hasta el sprint 5; programas, juegos y gestión de archivos aún no están implementados.

## Arrancar en esta computadora

Abre PowerShell en esta carpeta y ejecuta:

```powershell
.\scripts\start.ps1
```

Espera a que aparezca `Escuchando…` y di **“Jarvis, abre YouTube”**. También puedes decir “Jarvis”, esperar “Te escucho” y dar el comando dentro de 8 segundos. Termina con “Jarvis, salir” o `Ctrl+C`.

Para probar sin micrófono, escribe comandos sin decir Jarvis:

```powershell
.\scripts\start.ps1 -Text
```

Para una demostración sin abrir navegador ni reproducir sonido:

```powershell
.\scripts\start.ps1 -Text -DryRun
```

Si PowerShell bloquea el script, puedes iniciar directamente, sin cambiar políticas del sistema:

```powershell
.\.venv\Scripts\python.exe -m asistente.main
```

## Instalar en otra PC

Requisitos: Windows 10/11, Python **3.11 o 3.12 de 64 bits**, micrófono y salida de audio. Instala Python desde [python.org](https://www.python.org/downloads/windows/), incluyendo pip. Luego, desde la raíz:

```powershell
.\scripts\install.ps1
.\scripts\start.ps1
```

Si `python` abre Microsoft Store o no se encuentra, pasa la ubicación de tu instalación:

```powershell
.\scripts\install.ps1 -Python 'C:\ruta\a\python.exe'
```

El instalador crea `.venv` y registra el paquete local. No requiere activar el entorno ni modificar la política global de PowerShell. No copies `.venv` entre computadoras: recréalo con el script. El entorno preparado durante el desarrollo utiliza Python 3.12 del runtime de Codex; si ese runtime cambia o se elimina, recréalo con tu instalación normal de Python.

Para pruebas y reconocimiento offline:

```powershell
.\scripts\install.ps1 -Dev -Offline
```

## Comandos

En modo voz antepone la palabra de activación configurada (por defecto `jarvis`).

| Comando | Resultado |
| --- | --- |
| abre youtube / abrir youtube | Abre YouTube |
| abre google | Abre Google |
| busca en google café & té | Busca el texto conservando símbolos y tildes |
| busca C++ | Búsqueda breve |
| cuéntame un chiste | Chiste aleatorio del JSON |
| qué hora es | Hora local de Windows |
| tararea | Reproduce una melodía sintética original de 1,4 segundos |
| ayuda | Enumera las opciones |
| salir / adiós | Detiene el asistente |

No interpreta lenguaje libre ni ejecuta instrucciones arbitrarias. Una frase como “abre youtube y borra archivos” no coincide con el comando de abrir YouTube.

## Google y Vosk

El valor inicial `recognition.engine = "google"` usa [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) y necesita internet. No requiere configurar una API de pago, pero su servicio gratuito no garantiza disponibilidad. **Los fragmentos capturados se envían a Google antes de detectar “Jarvis”**: la activación se comprueba sobre la transcripción, no con un detector local de palabra clave. La aplicación no guarda grabaciones del micrófono ni transcripciones en disco.

Para reconocimiento local utiliza [Vosk](https://alphacephei.com/vosk/). Instala su dependencia y descarga el [modelo oficial pequeño en español](https://alphacephei.com/vosk/models), `vosk-model-small-es-0.42` (39 MB, Apache 2.0):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-offline.txt
.\scripts\download_model.ps1
.\scripts\start.ps1 -Engine vosk
```

También puedes cambiar `recognition.engine` a `vosk` en `config.json`. El modelo se descarga una vez y queda en `models/`, ignorado por Git. Con Vosk, el reconocimiento y la voz funcionan sin internet; abrir páginas y hacer búsquedas sigue necesitando conexión. No hay cambio automático de Vosk a Google para evitar enviar audio inesperadamente.

La elección definitiva depende de tu acento y tu micrófono. Repite cinco veces “Jarvis, abre YouTube” y “Jarvis, busca en Google recetas de arepas” con cada motor. Compara aciertos y demora, primero en silencio y luego con ruido. Las pruebas con audio sintético no sustituyen esa comparación.

## Configuración y diagnóstico

`config.json` contiene palabra clave, ventana de activación, idioma, índice del micrófono, tiempos máximos, voz y sitios. `programs`, `games` y `allowed_folder` son reservas para el sprint 4; no tienen acciones asociadas todavía. Las rutas relativas del modelo se resuelven respecto al archivo de configuración. Los recursos de la aplicación se resuelven respecto al proyecto, independientemente del directorio actual.

Puedes copiar la configuración a `config.local.json` (ignorado por Git) y pasar `--config config.local.json`.

```powershell
.\.venv\Scripts\python.exe -m asistente.main --check
.\.venv\Scripts\python.exe -m asistente.main --list-microphones
.\.venv\Scripts\python.exe -m asistente.main --list-voices
.\.venv\Scripts\python.exe -m asistente.main --command 'qué hora es' --mute
```

Si no capta audio, revisa Configuración de Windows > Privacidad y seguridad > Micrófono > Permitir que aplicaciones de escritorio accedan al micrófono. Elige un índice de entrada de `--list-microphones`; algunos índices enumerados corresponden a salidas. Guarda silencio durante la calibración inicial y prueba cerca del micrófono.

La voz usa [pyttsx3](https://pypi.org/project/pyttsx3/) y SAPI de Windows. Se elige una voz española instalada; si falta, se avisa y usa la predeterminada. Puedes instalar español desde Configuración > Hora e idioma > Voz y volver a iniciar. `voice_id` permite fijar un identificador de `--list-voices`. Si falla el motor de voz, se mantiene la respuesta por texto. `--mute` silencia la voz; `--dry-run` también simula la melodía y el navegador.

Los registros están en `logs/asistente.log`, con rotación de 1 MB y tres copias. No se guardan comandos ni consultas, aunque una excepción de terceros podría incluir información de su contexto. Los fallos de red se muestran en consola y la escucha vuelve a intentarlo con una pausa. Si se desconecta el micrófono, la sesión termina con error para que puedas corregirlo y reiniciar.

La escucha corre en un hilo; las acciones y SAPI se ejecutan en el principal. Se pausa la captura durante las respuestas y la melodía para reducir la realimentación. No es un servicio de Windows: mantén abierta la consola. La bandeja y el personaje corresponden a sprints posteriores.

## Estructura y extensión

```text
src/asistente/
  domain/           Entidades y puertos (Protocol), sin dependencias externas
  application/      Normalización, router, activación y casos de uso
  infrastructure/   JSON, logs, micrófono, Google/Vosk, SAPI y navegador
  main.py           Composición, registro de comandos y consola
data/               Frases y chistes editables
assets/sounds/      Melodía original incluida
scripts/            Instalación, arranque, modelo y diagnóstico
tests/              Pruebas sin micrófono ni red
```

Para añadir un comando, crea un caso de uso en `application/use_cases/` que reciba puertos y devuelva `CommandResult`. Regístralo en `build_service()` en `main.py`:

```python
router.register(("saluda", "di hola"), Saludar())
```

Si recibe un argumento, usa `parameterized=True`; el router pasa el resto de la frase sin eliminar sus tildes ni símbolos. Los alias sí se normalizan. Los alias duplicados se rechazan. El dominio y la aplicación no importan librerías de audio, navegador ni adaptadores. Los puertos se agruparon en `domain/ports.py` y los casos de uso afines en módulos cortos; se respeta la dirección de dependencias del roadmap.

## Verificación

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
```

Prueba opcional de hardware y audio sintético (requiere Vosk y modelo):

```powershell
.\.venv\Scripts\python.exe scripts\verify_audio.py
# Además envía solo el WAV sintético de prueba a Google:
.\.venv\Scripts\python.exe scripts\verify_audio.py --google
```

Ese diagnóstico abre brevemente el micrófono y descarta sus muestras; guarda únicamente una frase sintetizada en `logs/synthetic_test.wav`. Comprueba síntesis, transcripción y ciclo de vida del hilo. No certifica que tu voz se reconozca ni que escuches bien los altavoces.

Consulta `docs/estado.md` para los resultados de esta entrega y la prueba manual pendiente. No se ha publicado en GitHub ni creado un ejecutable. La instalación en otra PC y el video de demo siguen siendo tareas del sprint 5.
