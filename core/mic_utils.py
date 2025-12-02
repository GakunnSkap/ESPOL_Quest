# core/mic_utils.py
def list_microphones(verbose: bool = True):
    result = {"sounddevice": [], "speech_recognition": []}

    if verbose:
        print("=== Dispositivos de audio (sounddevice) ===")
    try:
        import sounddevice as sd
        for i, dev in enumerate(sd.query_devices()):
            in_ch = dev.get("max_input_channels", 0)
            if in_ch > 0:
                sr = dev.get("default_samplerate", None)
                result["sounddevice"].append((i, dev.get("name", f"Device {i}"), in_ch, sr))
                if verbose:
                    print(f"[{i}] {dev.get('name')}  (in={in_ch}, sr={sr})")
    except Exception as e:
        if verbose:
            print("(sounddevice) No disponible:", e)

    if verbose:
        print("\n=== Micrófonos (SpeechRecognition / PyAudio) ===")
    try:
        import speech_recognition as sr
        names = sr.Microphone.list_microphone_names()
        for i, name in enumerate(names):
            result["speech_recognition"].append((i, name))
            if verbose:
                print(f"[{i}] {name}")
    except Exception as e:
        if verbose:
            print("(SpeechRecognition) No disponible:", e)

    return result
