#!/usr/bin/env python3
import os
import sys
import time
import datetime
import numpy as np
import cv2
import sounddevice as sd
import soundfile as sf
import tempfile
import openai
from pynput import keyboard

# ───── CONFIG ─────
VIDEO_DEVICE_INDEX = 0      
AUDIO_DEVICE_INDEX = None   

drop_dir = os.path.expanduser('~/Problems')
os.makedirs(drop_dir, exist_ok=True)

# Hotkeys
HOTKEY_SCREEN = '<ctrl>+<shift>+s'
HOTKEY_AUDIO  = '<ctrl>+<shift>+r'
HOTKEY_EXIT   = '<ctrl>+<shift>+q'
HOTKEY_LIST_DEVICES = '<ctrl>+<shift>+d'  # New hotkey to list audio devices

# Whisper / OpenAI setup
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    print("❌ ERROR: OpenAI API key not found. Please set the environment variable OPENAI_API_KEY and retry.")
    sys.exit(1)
WHISPER_MODEL  = 'whisper-1'
AUDIO_SR       = 48000
AUDIO_CH       = 2
# ──────────────────

def find_audio_device():
    """Find the NZXT HD60 audio device in sounddevice's device list"""
    devices = sd.query_devices()
    print("\n🔍 Available audio devices:")
    for i, device in enumerate(devices):
        print(f"[{i}] {device['name']} - {device['max_input_channels']} input channels")
        if 'NZXT' in device['name'] or 'HD60' in device['name']:
            if device['max_input_channels'] > 0:
                print(f"    ⭐ Found NZXT device at index {i}")
                return i
    return None

# Find the correct audio device
AUDIO_DEVICE_INDEX = find_audio_device()
if AUDIO_DEVICE_INDEX is None:
    print("❌ Could not find NZXT HD60 audio device. Please check connection.")
    print("Use Ctrl+Shift+D to list all devices once the script is running.")

# --- Video capture setup ---
cap = cv2.VideoCapture(VIDEO_DEVICE_INDEX, cv2.CAP_AVFOUNDATION)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# State
recording     = False
buffer_chunks = []
stream        = None
listener      = None

# --- Functions ---
def list_audio_devices():
    """List all available audio devices"""
    print("\n🔍 All audio devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        marker = " ⭐" if i == AUDIO_DEVICE_INDEX else ""
        print(f"[{i}] {device['name']} - {device['max_input_channels']} input ch, {device['max_output_channels']} output ch{marker}")
    print()

def take_screenshot():
    time.sleep(0.1)
    if not cap.isOpened():
        print("❌ Video device not opened.")
        return
    ret, frame = cap.read()
    if not ret or frame is None:
        print("❌ Failed to grab frame.")
        return

    ts   = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    path = os.path.join(drop_dir, f'screenshot_{ts}.png')
    cv2.imwrite(path, frame)
    print(f"✅ Screenshot → {path}")

def audio_callback(indata, frames, time_info, status):
    if status:
        print(f"⚠️ Audio status: {status}")
    buffer_chunks.append(indata.copy())

def start_recording():
    global recording, buffer_chunks, stream
    if recording:
        return
    
    if AUDIO_DEVICE_INDEX is None:
        print("❌ No audio device selected. Use Ctrl+Shift+D to list devices.")
        return
        
    buffer_chunks = []
    try:
        # Get device info for debugging
        device_info = sd.query_devices(AUDIO_DEVICE_INDEX)
        print(f"🎤 Using device: {device_info['name']}")
        print(f"   Sample rate: {device_info['default_samplerate']}")
        print(f"   Input channels: {device_info['max_input_channels']}")
        
        stream = sd.InputStream(
            samplerate=AUDIO_SR,
            channels=min(AUDIO_CH, device_info['max_input_channels']),  # Use available channels
            device=AUDIO_DEVICE_INDEX,
            callback=audio_callback,
            dtype='float32'  # Ensure consistent data type
        )
        stream.start()
        recording = True
        print("🔴 Audio recording started.")
    except Exception as e:
        print(f"❌ Could not start audio: {e}")

def stop_and_transcribe():
    global recording, stream
    if not recording:
        return
    stream.stop()
    stream.close()
    recording = False

    if not buffer_chunks:
        print("❌ No audio data recorded.")
        return

    # Combine audio data
    data = np.concatenate(buffer_chunks, axis=0)
    print(f"📊 Audio data shape: {data.shape}, dtype: {data.dtype}")
    print(f"📊 Audio level check - min: {data.min():.4f}, max: {data.max():.4f}, RMS: {np.sqrt(np.mean(data**2)):.4f}")
    
    # Check if audio is too quiet
    rms_level = np.sqrt(np.mean(data**2))
    if rms_level < 0.001:
        print("⚠️ WARNING: Audio level very low. Check your audio source.")

    # Write to temporary WAV file
    ts = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        wavfile = tmp.name
        sf.write(wavfile, data, AUDIO_SR)

    print(f"🟢 Recorded audio → {wavfile}")
    
    # Also save a permanent copy for debugging
    debug_wavfile = os.path.join(drop_dir, f'debug_audio_{ts}.wav')
    sf.write(debug_wavfile, data, AUDIO_SR)
    print(f"🐛 Debug audio copy → {debug_wavfile}")

    # Transcribe via OpenAI
    print("⏳ Transcribing…")
    try:
        with open(wavfile, 'rb') as af:
            res = openai.audio.transcriptions.create(
                file=af,
                model=WHISPER_MODEL,
                response_format="text",
                language="en"  # Specify language if known
            )
        transcript = res
        print(f"📝 Raw transcript: '{transcript}'")
        
        txtfile = os.path.join(drop_dir, f'transcript_{ts}.txt')
        with open(txtfile, 'w', encoding='utf-8') as tf:
            tf.write(transcript)
        print(f"✍️ Transcript → {txtfile}")
        
        if len(transcript.strip()) < 10:
            print("⚠️ WARNING: Transcript is very short. This might indicate an audio capture issue.")
            
    except Exception as e:
        print(f"❌ Transcription failed: {e}")
    finally:
        # Remove the temporary WAV
        try:
            os.remove(wavfile)
        except Exception:
            pass

def toggle_audio():
    if recording:
        stop_and_transcribe()
    else:
        start_recording()

def exit_program():
    if recording:
        stop_and_transcribe()
    if cap.isOpened():
        cap.release()
    if listener:
        listener.stop()
    print("👋 Exiting.")
    sys.exit(0)

# --- Hotkey bindings ---
hotkeys = {
    HOTKEY_SCREEN: take_screenshot,
    HOTKEY_AUDIO:  toggle_audio,
    HOTKEY_EXIT:   exit_program,
    HOTKEY_LIST_DEVICES: list_audio_devices
}

listener = keyboard.GlobalHotKeys(hotkeys)
print(f"▶ Hotkeys:")
print(f"  {HOTKEY_SCREEN} - Screenshot")
print(f"  {HOTKEY_AUDIO} - Toggle audio recording")
print(f"  {HOTKEY_LIST_DEVICES} - List audio devices")
print(f"  {HOTKEY_EXIT} - Exit")

if AUDIO_DEVICE_INDEX is not None:
    print(f"🎤 Audio device: {sd.query_devices(AUDIO_DEVICE_INDEX)['name']}")
else:
    print("⚠️ No audio device found automatically. Use Ctrl+Shift+D to list devices.")

listener.start()
listener.join()
