printf "file '%s'\n" ./recording/*.wav > concat.txt
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy recording/output/output.wav
