import sys
import time
import mido

portname = "K-Mix Control Surface"

#
# Handle incoming midi messages
#
def on_midi_message(message):
    print('Received {}'.format(message))

#
# Keep trying to connect to kmix and pass messages to listener
#
def midi_loop_kmix():
    try:        
        with mido.open_input(portname) as port:
            print('Using {}'.format(port))
            while True:
                for message in port.iter_pending():
                    on_midi_message(message)

                # print('Doing something else for a while...')
                # time.sleep(0.5)
    except OSError:
        print("Couldnt find K-Mix. Retrying.")
        time.sleep(1)

#
# Main execution routine
#
try:
    while True:
        midi_loop_kmix()

except KeyboardInterrupt:
    pass