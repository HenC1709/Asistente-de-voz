# Actualización de sprints 4 y 5

Se implementaron las acciones locales y la preparación de portabilidad. Pasan 44 pruebas. Consulta [estado y aceptación actual](sprints-4-5.md). El contenido siguiente conserva la evidencia histórica de la entrega anterior.

# Estado de la entrega

Fecha: 16 de noviembre de 2026. Alcance: sprints 0 a 3 del roadmap, versión de desarrollo `0.1.0.dev3`.

## Implementado

| Sprint | Entrega |
| --- | --- |
| 0 | Repositorio Git local, entorno virtual, dependencias, estructura por capas, configuración validada y logs rotativos |
| 1 | Captura en hilo, calibración, activación por palabra completa, ventana de segundo comando, Google y adaptador opcional Vosk |
| 2 | Registro por diccionario, alias normalizados, argumentos preservados, sitios configurables, búsqueda con URL codificada y pruebas con fakes |
| 3 | Voz offline por SAPI/pyttsx3, selección de español, fallback a texto, frases JSON, chistes, hora y melodía original |

Se añadieron instrucciones y scripts básicos de instalación para poder ejecutar esta entrega. Esto no implica completar el sprint 5: falta probar en otra PC, preparar el video y validar el criterio de instalación en menos de 15 minutos. No se realizaron commits ni publicación remota.

## Evidencia local

- Python 3.12.14; dependencias instaladas dentro de `.venv`.
- 30 pruebas automatizadas pasaron inicialmente, sin depender de micrófono ni internet.
- `pip check`: sin incompatibilidades de dependencias.
- Compilación de módulos mediante `compileall`: correcta.
- Enumeración de dispositivos: micrófono AMD Audio Device y salida Realtek presentes.
- Voz de Windows: Microsoft Sabina Desktop, español de México; generación de WAV sintético correcta.
- Captura breve del micrófono: devolvió muestras, descartadas sin guardar ni enviar.
- Hilo real de captura: inicio, pausa, reanudación y cierre correctos.
- Sesión de consola con ayuda, YouTube, búsqueda de C++, chiste, hora, tarareo y salida: completada en modo de simulación.
- Comandos reales de hora hablada y reproducción de la melodía: terminaron sin errores; la calidad audible queda por confirmar por el usuario.
- Google transcribió el WAV sintético como `jarvis Abre YouTube`.
- Vosk cargó el modelo español y devolvió `y hardy sabrá youtube` para el mismo WAV. Por tanto **no pasó el comando completo con “Jarvis”**. Está instalado como alternativa para comparación, pero Google sigue como motor inicial.

Los diagnósticos de SAPI y las instalaciones requirieron ejecución fuera del aislamiento de Codex por restricciones de acceso de Windows. El arranque normal se realiza desde PowerShell del usuario.

## Aceptación manual pendiente

1. Iniciar `scripts/start.ps1`, guardar silencio durante la calibración y decir “Jarvis, abre YouTube”. Confirmar que se abre en el navegador predeterminado.
2. Decir “Jarvis, busca en Google recetas de arepas” y comprobar la búsqueda.
3. Probar chiste, hora, tarareo y salida, verificando el sonido de los altavoces y que no se active con su propia voz.
4. Comparar cinco repeticiones por motor con la voz del usuario. Para Vosk, probar una palabra española como `asistente` en `wake_word` si “Jarvis” falla; esto aún requiere validación de acento.
5. Probar desconexión de internet, micrófono ausente, ruido y una sesión prolongada.

Las pruebas automáticas y el audio sintético no sustituyen esta aceptación. La gestión de archivos y apertura de programas/juegos (sprint 4), prueba en otra computadora (sprint 5), personaje e instalador siguen fuera de esta entrega.
