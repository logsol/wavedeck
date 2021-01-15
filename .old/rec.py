
import pyaudio
import wave
import time

stream = None
pa = pyaudio.PyAudio()
wavefile = None
channels = 2

def select_soundcard():
    #device_name = "Built-in Microphone"
    device_name = "Soundflower (64ch)"
    for i in range(pa.get_device_count()):
        print pa.get_device_info_by_index(i)['name']

    return

    for i in range(pa.get_device_count()):
        if device_name in pa.get_device_info_by_index(i)['name']:
            return i
    else:
        print "Device '" + device_name + "' not found, exiting."
        exit()

def audio_callback(in_data, frame_count, time_info, status):
    global wavefile
    wavefile.writeframes(in_data)
    return in_data, pyaudio.paContinue

def start_recording(device_index):
    global channels
    # Use a stream with a callback in non-blocking mode
    stream = pa.open(format=pyaudio.paInt16, channels=channels, rate=44100, input=True, frames_per_buffer=16384, stream_callback=audio_callback, input_device_index=device_index)
    stream.start_stream()

def stop_recording():
    stream.stop_stream()

def close():
    stream.close()
    pa.terminate()
    wavefile.close()

def prepare_file(fname):
    global channels
    wavefile = wave.open(fname, 'wb')
    wavefile.setnchannels(channels)
    wavefile.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
    wavefile.setframerate(44100)
    return wavefile

def main():
    global wavefile
    device_index = select_soundcard()
    #wavefile = prepare_file('outputski.wav')

    #start_recording(device_index)
    #time.sleep(50.0)
    #stop_recording()

main()