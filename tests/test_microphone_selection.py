import pytest
from asistente.infrastructure.voice.microphone_selection import select_input


DEVICES = [
    dict(index=1, name='Microphone Array (AMD)', api_name='MME', maxInputChannels=2),
    dict(index=9, name='Microphone Array (AMD)', api_name='Windows WASAPI', maxInputChannels=2),
    dict(index=12, name='Headset', api_name='Windows WASAPI', maxInputChannels=1),
    dict(index=13, name='Speaker', api_name='Windows WASAPI', maxInputChannels=0),
]


def test_named_input_prefers_wasapi_over_headset():
    assert select_input(DEVICES, 'microphone array') == 9


def test_requested_mme_and_missing_backend():
    assert select_input(DEVICES, 'microphone array', api='MME') == 1
    assert select_input(DEVICES, 'microphone array', index=9, api='MME') == 9
    with pytest.raises(ValueError):
        select_input(DEVICES, 'microphone array', api='DirectSound')


def test_index_override():
    assert select_input(DEVICES, 'microphone array', 12) == 12


def test_missing_does_not_silently_switch():
    with pytest.raises(ValueError):
        select_input(DEVICES, 'missing')


def test_output_is_rejected():
    with pytest.raises(ValueError):
        select_input(DEVICES, index=13)


def test_default_and_changed_indices():
    assert select_input(DEVICES) is None
    moved = [dict(d, index=d['index'] + 20) for d in DEVICES]
    assert select_input(moved, 'Microphone Array') == 29
