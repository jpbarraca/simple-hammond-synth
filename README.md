# Simple PyHammond

A Simple Music Synthesizer inspired by the operation of the [Hammond Organ](https://en.wikipedia.org/wiki/Hammond_organ) and using music scores in the [Ring Tone Transfer Language](https://en.wikipedia.org/wiki/Ring_Tone_Transfer_Language).

This is a strange combination, and the synthesizer is very simple, but this served its purpose as an example implementation for laboratory project of a CS course.

The implementation is simple and can be used to demonstrate some basic music generation using python. In its current form it is fully functional and can generate a wave file from a music score in the RTFL format.

The file `songs.py` already contains a few songs. More songs can be added as long as the identifier (song name) is unique.

## Usage is:

```
python generateMusic.py drawbar music_name
```

The `drawbar` is composed by 9 values, from 0 to 8, specifying the intensity of each generator. An typical value could be: 288200000. For more details please check [this](http://www.hammond-organ.com/product_support/drawbars.htm).

The `music_name` is a name existing in the file `songs.py`

An example execution would be:
```
python generate_music.py 288200000 TakeOnMe
```

A file named `TakeOnMe-28820000.wav` would be generated in the current folder.

## Caveats

The code has almost no documentation or error handling. This is a simple application developed for educational purposes.