def shutdown():
    print("Exit.")
    midiin.close_port()
    del midiin

def main:
    is_connected = False
    while True:
        update_audio_devices()
        update_midi_devices()
        time.sleep(1)

try:
    main()
except KeyboardInterrupt:
    print('')
finally:
    shutdown()


def midi_callback(note):
    if (note == 21):
        ps_start_record()
        ps_send_midi_on(21);

    if (note == 22):
        ps_stop_record()
        ps_send_midi_off(21);



def main():
    ps_connect_audio_device()
    ps_connect_midi_device(midi_callback)
    
    while (1):
        ps_check_that_midi_is_still_connected()
        ps_check_that_audio_is_still_connected()