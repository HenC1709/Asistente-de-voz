def select_input(devices, name=None, index=None, api=None):
    """Explicit index overrides name and API; otherwise use the requested backend."""
    inputs = [d for d in devices if d['maxInputChannels'] > 0]
    if index is not None:
        if not any(d['index'] == index for d in inputs):
            raise ValueError('El índice seleccionado no corresponde a un micrófono disponible.')
        return index
    if not name:
        return None
    matches = [d for d in inputs if name.casefold() in d['name'].casefold()]
    if not matches:
        raise ValueError(f'No se encontró el micrófono «{name}». Usa --list-microphones o cambia recognition.microphone_name.')
    if api:
        matches = [d for d in matches if api.casefold() in d['api_name'].casefold()]
        if not matches:
            raise ValueError(f'El micrófono «{name}» no está disponible mediante {api}.')
    return min(matches, key=lambda d: ('wasapi' not in d['api_name'].casefold(), d['index']))['index']


def resolve_input(config):
    import pyaudio
    client = pyaudio.PyAudio()
    try:
        devices = []
        for i in range(client.get_device_count()):
            info = client.get_device_info_by_index(i)
            info['api_name'] = client.get_host_api_info_by_index(info['hostApi'])['name']
            devices.append(info)
        index = select_input(devices, config.get('microphone_name'), config.get('microphone_index'), config.get('microphone_api'))
        info = client.get_default_input_device_info() if index is None else client.get_device_info_by_index(index)
        api = client.get_host_api_info_by_index(info['hostApi'])['name']
        return index, f"{info['name']} · {api} · índice {info['index']}"
    finally:
        client.terminate()
