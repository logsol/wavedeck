import sys
import time
import mido
import pyaudio
import wave
import os
from pathlib import Path

#
# initialize midi
#
midi_portname = "IAC"
#midi_portname = "K-Mix Control Surface"

note_rec_button = 84
#note_rec_button = 26

#
# initialize soundcard 
#
#soundcard_name = "USB Advanced Audio Device"
soundcard_name = "Soundflower (64ch)"
#soundcard_name = "K-Mix"

channels = 8
#channels = 2

#
# initialize folder variables
#
rec_path = "recordings/"
sess_path = ""
session_id = 1
rec_counter = 1

#
# initialize audio stream variables
#
pa = pyaudio.PyAudio()
stream = None
wavefile = None

#
# initialize state variables
#
is_recording = False
midi_monitor = False



#
# Make sure recordings/ folder exists
#
def ensure_recordings_folder():
    Path(rec_path).mkdir(parents=True, exist_ok=True)

#
# Create recordings/001 ... folder every time the script is started,
# reuse last folder if it is still empty
#
def create_session_folder():
    global sess_path, rec_path, session_id

    # read only directories (sessions folders)
    sessions = next(os.walk(rec_path))[1]

    # filter out hidden directories
    sessions = filter(lambda x: not x.startswith("."), sessions)

    # sort directories
    sessions = sorted(sessions)

    # initialize 
    last_session = 1
    last_session_contents = []

    # grab last session and contents
    if(len(sessions) > 0):
        last_session = int(sessions[-1])

        # retrieve contents to check for emptyness
        last_session_contents = os.listdir(rec_path + sessions[-1])


    # reuse last session folder if it was empty
    session_id = last_session

    # if not empty increase by 1
    if (len(last_session_contents) > 0):
        session_id += 1

    # turn into zero padded string of 3 digits
    session_id = f'{session_id:03}'

    # save session path
    sess_path = rec_path + session_id + "/"

    print ("Current session directory: ")
    print ("- " + sess_path + "\n")

#
# Switch rec light on K-Mix
#
def update_rec_led(outport):
    return
    # build midi message to send to switch rec LED
    message = mido.Message('note_on')
    message.velocity = 127

    if not is_recording:
        message = mido.Message('note_off')
        message.velocity = 0

    message.note = note_rec_button

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

        # grab soundcard and start recording
        device_index = select_soundcard(soundcard_name)
    
        # abort if device not found
        if (device_index == -1):
            print("Device '" + soundcard_name + "' not found.")

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
    
    # mido monitor mode - print all midi messages
    if (midi_monitor):
        print("Received {}".format(message))

    # filter out cc messages n stuff
    if message.type != "note_on" and message.type != "note_off":
        return

    # identify rec button presses
    if message.note == note_rec_button:

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
# print all midi devices
#
def print_midi_devices():
    print("Midi devices:")
    devices = mido.get_output_names()
    for device in devices:
        print("- " + device)

    print("")

#
# keep trying to connect to midi device and pass messages to listener
#
def midi_loop():
    global midi_portname
    try:
        port_names = mido.get_output_names()

        # iterate midi ports
        for port_name in port_names:
            # if port name contains string that was configured, use it
            if midi_portname in port_name:
                midi_portname = port_name

        # setup output midi port
        outport = mido.open_output(midi_portname)

        # using 'with' will execute 'close' on the automatically
        with mido.open_input(midi_portname) as inport:
            print("Using {}".format(inport))
            while True:
                for message in inport.iter_pending():
                    on_midi_message(message, outport)

                # print('Doing something else for a while...')
                time.sleep(0.5)
    except OSError:
        print("Couldnt find MIDI device (" + midi_portname + "). Retrying..")
        time.sleep(2)

#
# print all soundcards  
#
def print_soundcards():
    print("Soundcards:")
    for i in range(pa.get_device_count()):
        print("- " + pa.get_device_info_by_index(i)['name'])

    print("")

#
# return index of given sound card name
#
def select_soundcard(device_name):

    for i in range(pa.get_device_count()):
        if device_name in pa.get_device_info_by_index(i)['name']:
            return i
    else:
        return -1

#
# audio stream callback function when recording
#
def audio_callback(in_data, frame_count, time_info, status):
    global wavefile

    wavefile.writeframes(in_data)
    return in_data, pyaudio.paContinue

#
# Start stream for recording
#
def start_recording(device_index):
    global channels, stream

    # possible formats paFloat32,paInt32,paInt16,paInt24,paInt8,paUInt8

    # Use a stream with a callback in non-blocking mode
    stream = pa.open(format=pyaudio.paInt16, channels=channels, rate=44100, input=True, frames_per_buffer=4096, stream_callback=audio_callback, input_device_index=device_index)
    stream.start_stream()

#
# Stop recording stream
#
def stop_recording():
    global stream
    stream.stop_stream()
    stream.close()

#
# Prepare a new multiwave file for recording
#
def prepare_file():
    global channels, rec_counter, session_id, sess_path

    # ensure session directory
    Path(sess_path).mkdir(parents=True, exist_ok=True)
    
    fname = "wavedeck-" + session_id + "-" + f'{rec_counter:03}' + ".wav"
    wavefile = wave.open(sess_path + fname, 'wb')
    wavefile.setnchannels(channels)
    wavefile.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
    wavefile.setframerate(44100)
    rec_counter += 1
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
    print("Welcome to wavedeck recorder! \n")

    print_midi_devices()
    print_soundcards()
    ensure_recordings_folder()
    create_session_folder()

    while True:
        midi_loop()

except KeyboardInterrupt:
    pass

finally:
    shutdown()