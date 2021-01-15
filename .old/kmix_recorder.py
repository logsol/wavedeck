import sys
import time
import mido
import pyaudio
import wave

midi_portname = "K-Mix Control Surface"
pa = pyaudio.PyAudio()
stream = None
wavefile = None
channels = 8
is_recording = False

NOTE_REC_BUTTON = 26

def update_rec_led(outport):
    # build midi message to send to switch rec LED
    message = mido.Message('note_on')
    message.velocity = 127

    if not is_recording:
        message = mido.Message('note_off')
        message.velocity = 0

    message.note = NOTE_REC_BUTTON

    # send rec LED midi message
    outport.send(message)

#
# When record button was pressed
#
def on_rec_pressed(outport):
    global is_recording, wavefile

    # toggle rec state
    is_recording = not is_recording

    # print rec state
    print("Rec " + ("On" if is_recording else "Off"))

    # update LED
    update_rec_led(outport)

    if is_recording:
        # prepare wave file
        wavefile = prepare_file()

        # set device name
        #device_name = "Soundflower (64ch)"
        device_name = "K-Mix"

        # grab soundcard and start recording
        device_index = select_soundcard(device_name)
    
        # abort if device not found
        if (device_name == -1):
            print("Device '" + device_name + "' not found.")

            # wait a second and switch LED back off
            time.sleep(1)
            is_recording = False
            update_rec_led(outport)
            return

        # start to record if found
        start_recording(device_index)

    else:
        stop_recording()
    

#
# handle incoming midi messages
#
def on_midi_message(message, outport):
    
    # print all midi messages
    print("Received {}".format(message))

    # filter out cc messages n stuff
    if message.type != "note_on" and message.type != "note_off":
        return

    # identify rec button presses
    if message.note == NOTE_REC_BUTTON:

        # execute record switching on press down
        if message.type == "note_on":
            on_rec_pressed(outport)

        # just update LED again because not off will disable it on the device
        if message.type == "note_off":
            update_rec_led(outport)

    # letting you know in case you forgot to press shift-record ;-)
    if message.note == 95:
        print("Gotta move to midi mode!")

#
# keep trying to connect to kmix and pass messages to listener
#
def midi_loop_kmix():
    try:
        # setup output midi port
        outport = mido.open_output(midi_portname)

        # using 'with' will execute 'close' on the automatically
        with mido.open_input(midi_portname) as port:
            print("Using {}".format(port))
            while True:
                for message in port.iter_pending():
                    on_midi_message(message, outport)

                # print('Doing something else for a while...')
                time.sleep(0.5)
    except OSError:
        print("Couldnt find K-Mix. Retrying..")
        time.sleep(1)



def select_soundcard(device_name):
    
    # print all soundcards
    for i in range(pa.get_device_count()):
        print(pa.get_device_info_by_index(i)['name'])

    for i in range(pa.get_device_count()):
        if device_name in pa.get_device_info_by_index(i)['name']:
            return i
    else:
        return -1

def audio_callback(in_data, frame_count, time_info, status):
    global wavefile

    wavefile.writeframes(in_data)
    return in_data, pyaudio.paContinue

def start_recording(device_index):
    global channels, stream
    # Use a stream with a callback in non-blocking mode
    stream = pa.open(format=pyaudio.paInt16, channels=channels, rate=44100, input=True, frames_per_buffer=1024, stream_callback=audio_callback, input_device_index=device_index)
    stream.start_stream()

def stop_recording():
    global stream
    stream.stop_stream()

def prepare_file():
    global channels

    fname = 'multi-out.wav'
    wavefile = wave.open(fname, 'wb')
    wavefile.setnchannels(channels)
    wavefile.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
    wavefile.setframerate(44100)
    return wavefile

#
# software shutdown routine
#
def shutdown():
    is_recording = False
    if stream:
        stream.close()
    if pa:
        pa.terminate()
    if wavefile:
        wavefile.close()
    print("\nGoodbye <3")

#
# main execution routine
#
try:
    # create_pulsar_folder()
    while True:
        midi_loop_kmix()

except KeyboardInterrupt:
    pass

finally:
    shutdown()