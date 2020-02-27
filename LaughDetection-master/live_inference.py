import tensorflow as tf
import keras
from datetime import datetime
import numpy as np
import tempfile
from scipy.io import wavfile
import socket
import time
import os
import subprocess
from playsound import playsound

from audioset import vggish_embeddings
from laugh_detector.microphone_stream import MicrophoneStream
#from laugh_detector.camera_stream import CameraStream

flags = tf.app.flags

flags.DEFINE_string(
    'keras_model', 'Models/LSTM_SingleLayer_100Epochs.h5',
    'Path to trained keras model that will be used to run inference.')

flags.DEFINE_float(
    'sample_length', 3.0,
    'Length of audio sample to process in each chunk'
)

flags.DEFINE_string(
    'save_file', None,
    'Filename to save inference output to as csv. Leave empty to not save'
)

flags.DEFINE_bool(
    'print_output', True,
    'Whether to print inference output to the terminal'
)

flags.DEFINE_string(
    'recording_directory', None,
    'Directory where recorded samples will be saved'
    'If None, samples will not be saved'
)

flags.DEFINE_bool(
    'hue_lights', False,
    'Map output to Hue bulbs'
)

flags.DEFINE_string(
    'hue_IP', None,
    'IP address for the Hue Bridge'
)

flags.DEFINE_integer(
    'avg_window', 10,
    'Size of window for running mean on output'
)

flags.DEFINE_bool(
    'back_record', True,
    'Back record laugh moment as video'
)

FLAGS = flags.FLAGS

RATE = 16000
CHUNK = int(RATE * FLAGS.sample_length)  # 3 sec chunks

PATH_TO_ROOTDIR = "xxxxxxx"
BACKRECORD_THRESH = 0.25
IP = "127.0.0.1"
PORT = 10001

def set_light(lights, b_score, c_score):
    for l in lights[:2]:
        l.brightness = int(map_range(b_score, 0, 255))
        l.xy = list(map_range(c_score, np.array(blue_xy), np.array(white_xy)))


def map_range(x, s, e):
    d = e-s
    return s+d*x


if __name__ == '__main__':
    os.system("rm recording/*.wav") #clean recording folder
    model = keras.models.load_model(FLAGS.keras_model)
    audio_embed = vggish_embeddings.VGGishEmbedder()

    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_client.connect((IP, PORT))

    if FLAGS.save_file:
        writer = open(FLAGS.save_file, 'w')

    if FLAGS.hue_lights:
        from phue import Bridge

        b = Bridge(FLAGS.hue_IP)
        lights = b.lights[:2]

        blue_xy = [0.1691, 0.0441]
        white_xy = [0.4051, 0.3906]

    window = [0.5]*FLAGS.avg_window

    #with CameraStream() as cam_stream:
    #    cam_stream.start()

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        for chunk in audio_generator:
            try:
                ts = int(time.time())

                arr = np.frombuffer(chunk, dtype=np.int16)
                vol = np.sqrt(np.mean(arr**2))
                embeddings = audio_embed.convert_waveform_to_embedding(arr, RATE)
                p = model.predict(np.expand_dims(embeddings, axis=0))
                window.pop(0)
                window.append(p[0, 0])

                if FLAGS.hue_lights:
                    set_light(lights, 0.6, sum(window)/len(window))

                if FLAGS.recording_directory:
                    #delete wav files older than 12 seconds ago
                    delete_name = FLAGS.recording_directory + '/' + str(ts - 12) + '.wav'
                    if os.path.exists(delete_name):
                        os.remove(delete_name)
                    #save wav files in current time stamp
                    save_name = FLAGS.recording_directory + '/' + str(ts) + '.wav'
                    #f = tempfile.NamedTemporaryFile(delete=False, suffix='.wav', dir=FLAGS.recording_directory)
                    wavfile.write(save_name, RATE, arr)

                if FLAGS.print_output:
                    print(str(datetime.now()) + ' - Laugh Score: {0:0.6f} - vol:{1}'.format(p[0, 0], vol))

                if FLAGS.save_file:
                    if FLAGS.recording_directory:
                        writer.write(str(datetime.now()) + ',{},{},{}\n'.format(f.name, p[0, 0], vol))
                    else:
                        writer.write(str(datetime.now()) + ',{},{}\n'.format(p[0, 0], vol))

                if FLAGS.back_record:
                    if float(p[0, 0]) >= BACKRECORD_THRESH:
                        #laugh is detected, send UDP to Processing program
                        print('Laugh Detected, back recording moment from ' + str(ts))
                        socket_client.send("LAUGH")
                        #use ffmpeg to concatenate currently saved wav files into one file
                        os.system("sh recording/concat.sh")
                        #use ffmpeg to concatenate audio with jpeg frames from Processing
                        ffmpeg = "ffmpeg -r 10 -start_number " + str((ts - 12) % 10000000) + "1 -i " + PATH_TO_ROOTDIR + "BackRecordLaughter/data/" + str((ts - 12) / 10000000) + "%8d.jpg -i " + PATH_TO_ROOTDIR + "BackRecordLaughter/LaughDetection-master/recording/output/output.wav -vcodec libx264 -pix_fmt yuv420p -r 30 " + PATH_TO_ROOTDIR + "BackRecordLaughter/data/output/" + str(ts - 12) + ".mp4"
                        os.system(ffmpeg)


            except (KeyboardInterrupt, SystemExit):
                print('Shutting Down -- closing file')
                writer.close()
