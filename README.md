# How to install on Raspberry Pi 3 and above?

Run installation script:
`sh install.sh`

Take care of alsa warnings

# How to install on chip

Fore reference visit https://medium.com/@0x1231/nextthingco-pocket-c-h-i-p-flashing-guide-3445492639e

Copy these sources into `/etc/apt/sources.list`

`sudo apt-get install software-properties-common`

Then install pythoon3
`sudo apt install python3-pip`

Run installation script:
`sh install.sh`

Note that I could not really get this to work on CHIP, which
is why I decided to move to Raspberry Pi instead.

# How to take care of alsa warnings?

To get rid of alsa warnings, use nano to edit this config file:
`sudo nano /usr/share/alsa/alsa.conf`

Comment out these sections as such:

```
#
#  PCM interface
#

# redirect to load-on-demand extended pcm definitions
pcm.cards cards.pcm

pcm.default cards.pcm.default
pcm.sysdefault cards.pcm.default
#pcm.front cards.pcm.front
#pcm.rear cards.pcm.rear
#pcm.center_lfe cards.pcm.center_lfe
#pcm.side cards.pcm.side
#pcm.surround21 cards.pcm.surround21
#pcm.surround40 cards.pcm.surround40
#pcm.surround41 cards.pcm.surround41
#pcm.surround50 cards.pcm.surround50
#pcm.surround51 cards.pcm.surround51
#pcm.surround71 cards.pcm.surround71
#pcm.iec958 cards.pcm.iec958
#pcm.spdif iec958
#pcm.hdmi cards.pcm.hdmi
pcm.dmix cards.pcm.dmix
#pcm.dsnoop cards.pcm.dsnoop
#pcm.modem cards.pcm.modem
#pcm.phoneline cards.pcm.phoneline
```