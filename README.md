# LAUGHTER BACK RECORDER

Back records a 15 second video when laughter is detected to keep a record of the banal yet precious moments of stuff happening in your room.

The laugh detector is created by [IDEO](https://www.ideo.com)'s [genius data scientists](https://labs.ideo.com/2018/06/15/how-to-build-your-own-laugh-detector/). The laugh detection code itself is open source [here](https://github.com/ideo/LaughDetection).
I tweaked
```
live_inference.py
```
so that it would constantly save 30 seconds of audio temporarily, and created another Processing file to constantly save 30 seconds of image frames temporarily.
Whenever laughter is detected the Processing file would play a gong sound, and the python file would concatenate audio and frames to create a 15 second long back recorded video.

An example of the output video
[![EXAMPLE VIDEO](https://img.youtube.com/vi/LwZKfXWDZ-0/0.jpg)](https://www.youtube.com/watch?v=LwZKfXWDZ-0)

~~**There is a bug in the code that makes the audio of the output video about 1 second faster than the image. Will be fixed (soon) (probably).**~~
**Fine tuned so that it more or less matches (2020/02/27)**

### HOW TO USE
1. run BackRecordLaughter.pde on Processing (I use version 3.5.3)
2. open terminal, cd to this directory and run `sh start.sh`
3. Laugh!
