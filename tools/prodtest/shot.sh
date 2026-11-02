#!/bin/sh
# shot.sh OUT.png : grabs the whole Xvfb screen
ffmpeg -v error -y -f x11grab -video_size 1920x1080 -i :98 -frames:v 1 "$1"
