 # encoding=utf-8

# Simple music generator from the RTFL Ringtone format
# Author: João Paulo Barraca <jpbarraca@ua.pt>

from struct import pack
from math import sin, pi, cos, log
import wave
import parse
import sys
from songs import songs

# Constants
attack = 3
attack_decay = 1

envelope = []


for i in range(1, 20):
    envelope.append(log(int(i)) * attack)

top = envelope[-1]
for i in range(1, 40):
    envelope.append(top - log(i) * attack_decay)

for i in range(1, 100):
    envelope.append(envelope[-1])


while envelope[-1] > 0.1:
    envelope.append(envelope[-1]*0.9)

notes_map = {
    'c': 0,
    'd': 2,
    'e': 4,
    'f': 5,
    'g': 7,
    'a': 9,
    'b': 11,
    'p': -1
}

notes = []

for n in range(-33, 58, 1):
     notes.append(int(440*pow(pow(2, 1/12.0),n)))

RATE = 44100.0

# Some example effects

def echo(data, sample_rate, duration, amount):
    samples_delay = int(amount * sample_rate)
    output = list(data)+[0]*(samples_delay)
    for index, value in enumerate(data):
        output[index + samples_delay] += value * amount

    return output


def overdrive(data, boost=8):
    output = []
    for index, value in enumerate(data):
        value = value / 32767.0
        value = value * boost

        if value > 0.6:
            value = 1
        elif value < -0.6:
            value = -1
        elif value > 0.3:
            value = (3-pow(2-3*value, 2))/3
        elif value < -0.3:
            value = -(3-pow(2-3*abs(value), 2))/3
        else:
            value *= 2

        output.append(value * 32767)

    return output


def normalize(data):
    m = 0
    output = []
    for index, value in enumerate(data):
        m = max(abs(value), m)

    amplify = 65534.0 / m /2.0

    for index, value in enumerate(data):
        output.append(int(value*amplify))

    return output


def tremolo(data, freq, amplitude):
    for i, v in enumerate(data):
        data[i] += int(v*amplitude*sin(2*pi*freq*i/RATE))
    return data

# Main generation
def generateSong(songname, song, drawbar, ):
    wv = wave.open(songname + '-' + drawbar + '.wav', 'w')
    wv.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
    songmeta = parse.parse('d={},o={},b={}:{}', song)

    default_duration = int(songmeta[0])
    base_octave = int(songmeta[1])

    bpm = float(songmeta[2])
    wholenote = (60 * 1000 / bpm) * 4
    songdata = songmeta[3]

    data = []
    registrations = [0.5, 0.66, 1, 2, 3, 4, 5, 6, 8]

    duration = wholenote / default_duration
    interpreted_notes = []
    prev_note = None
    prev_note_data = []

    for x in range(0, 1):
        for s in songdata.split(','):
            duration = wholenote / default_duration
            num = 0
            note = None
            scale = base_octave
            for c in s:
                if c.isdigit() and note is None:
                    num = num * 10 + int(c)
                    duration = wholenote / num
                elif c in notes_map:
                    note = notes_map[c]
                elif c == '#':
                    note += 1
                elif c == '.':
                    duration += duration / 2.0
                elif c.isdigit() and note is not None:
                    scale = int(c)

            freq = 0

            if note != -1:
                freq = notes[(scale - 4 + 2) * 12 + note]

            data_note = []

            nsamples = int(RATE * duration / 1000.0)
            interpreted_notes.append((duration/1000.0, int(freq)))

            factor = 1.5
            factor_decay = 1 / (0.4 * nsamples)
            
            for i in range(0, int(nsamples)):
                x = 0


                # Sum all generators
                for h in range(0, 9):
                    x += int(drawbar[h])*sin(2*pi*i*freq*registrations[h]/RATE)

                    # Add another at a slightly different frequency with decay
                    if factor > 0:
                        x += factor * int(drawbar[h]) * sin((2 * pi * i * freq * registrations[h] + 15 )/RATE)
                
                factor -= factor_decay

                data_note.append(x)

            # Apply envelope to notes
            l = len(data_note)/float(len(envelope))

            data.extend(data_note)

    # Apply some effects
    data = normalize(data)
    #data = tremolo(data, 100, 0.15)
    #data = overdrive(data, 1.6)

    data = echo(data, RATE, 0.1, 0.35)
    data = echo(data, RATE, 0.2, 0.25)
    data = echo(data, RATE, 0.3, 0.15)

    data = normalize(data)

    wvData = []
    for v in data:
        wvData += pack('h', int(v))

    wv.writeframes(bytearray(wvData))
    wv.close()

if len(sys.argv) > 2 and sys.argv[2] in list(songs.keys()):
    if len(sys.argv[1]) != 9:
        print("Drawbar must have 9 values")
        sys.exit(-1)

    for c in sys.argv[1]:
        if not  c.isdigit():
            print("Drawbar can only have digits")
            sys.exit(-1)

    print("Generating song: %s" % (sys.argv[2], ))
    print("Drawbar: %s " % (sys.argv[1], ))

    generateSong(sys.argv[2], songs[sys.argv[2]], sys.argv[1],)
    print("Done")
else:
    print("Usage: python %s drawbar songname" % (sys.argv[0], ))
    print("   Drawbar is composed by 9 integers within 0-8. Ex: 288820000")
    print("Available song names are:")
    print(list(songs.keys()))



