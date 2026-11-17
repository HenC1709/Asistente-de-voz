# Acciones y portabilidad

Esta entrega añade el código del sprint 4 y la preparación del sprint 5. La aceptación del MVP sigue pendiente de reconocimiento con la voz del usuario, otra PC y grabación de la demo.

## Comandos nuevos

En voz, anteponer Jarvis también a la confirmación:

- `abre programa editor` o `abre juego mi juego`
- `crea archivo prueba.txt` (archivo vacío, nunca sobrescribe)
- `busca archivo prueba` (hasta 20 resultados en la carpeta autorizada)
- `borra archivo prueba.txt`
- `confirmar borrado prueba.txt` (20 segundos, un solo uso)
- `cancelar borrado`

La carpeta predeterminada es `personal/archivos`, relativa al archivo de configuración. Solo se administran sus archivos directos. No hay borrado de carpetas ni búsquedas fuera de esa ubicación. Se rechazan enlaces, junctions, rutas, dispositivos de Windows y nombres con flujos alternativos. Si cambia el archivo entre solicitud y confirmación, hay que volver a solicitarla. La carpeta debe ser privada y no modificada concurrentemente por otros programas durante el borrado.

Programas y juegos se registran como nombre y ruta a un `.exe` en `programs` y `games` de `config.json`. Admite variables como `%WINDIR%` y rutas relativas al JSON. Ejemplo:

```json
"programs": {"editor": "%WINDIR%/System32/notepad.exe"}
```

No admite comandos de shell ni argumentos. Las coincidencias aproximadas solo sugieren un programa; nunca lo abren automáticamente. La búsqueda de archivos también ofrece coincidencias aproximadas. Se usa `difflib` de Python sin añadir rapidfuzz.

`--dry-run` simula las escrituras, papelera y lanzamiento; las lecturas y validaciones usan los archivos reales. Por ello un archivo creado en simulación no existe para un borrado posterior.

## Instalación en una PC nueva

1. Copiar o clonar el proyecto sin `.venv`, modelos ni datos personales. Instalar Python 3.11/3.12 x64 con pip.
2. Ejecutar `scripts/install.ps1 -Dev`; con Vosk añadir `-Offline`.
3. Ejecutar `.venv/Scripts/python.exe -m pytest -q` y `-m pip check`.
4. Iniciar `scripts/start.ps1 -Text` y probar chiste y YouTube.
5. Iniciar `scripts/start.ps1 -DebugVoice` y verificar el micrófono y la activación. No se ha resuelto todavía el reporte del usuario de reconocimiento de voz; este modo muestra dónde falla.
6. Cronometrar desde la instalación hasta abrir YouTube y contar un chiste: objetivo menor a 15 minutos. Registrar Windows, Python, motor, micrófono, duración y errores.

## Guion de demo de un minuto

- 0–10 s: mostrar arranque y decir Jarvis, abre YouTube.
- 10–20 s: buscar recetas de arepas.
- 20–30 s: pedir un chiste y la hora.
- 30–45 s: crear prueba.txt, buscarlo y solicitar borrado.
- 45–55 s: confirmar borrado, mostrar la papelera.
- 55–60 s: despedida.

Grabar con la herramienta de captura de Windows una vez validado el micrófono. Conservar un video de respaldo para la presentación. No se incluye un video ficticio ni se afirma haber probado otra computadora.
