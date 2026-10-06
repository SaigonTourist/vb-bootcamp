#!/usr/bin/env bash
# Realism pass: tones down the glossy AI grade and adds what a real camera does.
# usage: realism.sh in.mp4 out.mp4
set -e
ffmpeg -loglevel error -y -i "$1" -vf "\
scale=2112:-2,crop=1920:1080:(iw-1920)/2+40*sin(t*1.7)+15*sin(t*4.3):(ih-1080)/2+25*sin(t*1.3)+10*sin(t*3.7),\
eq=saturation=0.82:contrast=0.94:brightness=0.01:gamma=1.03,\
curves=all='0/0.04 0.5/0.5 0.92/0.88 1/0.9',\
colorbalance=rs=0.02:bs=-0.02:rh=-0.02:bh=0.02,\
unsharp=5:5:-0.35,\
noise=alls=9:allf=t+u,\
vignette=PI/6" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy "$2"
