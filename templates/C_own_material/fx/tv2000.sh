#!/usr/bin/env bash
# 2000s sports-broadcast look: 4:3 SD picture, soft and slightly noisy, scanlines, glossy graphics.
# usage: tv2000.sh in.(mp4|png) out.(mp4|png) "LOWER LINE 1" "LOWER LINE 2" [score_from_s] [score_text]
set -e
in=$1; out=$2; l1=$3; l2=$4; sfrom=${5:-999}; score=${6:-}
B=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
R=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
look="crop=ih*4/3:ih,scale=640:480,eq=saturation=1.35:contrast=1.08:gamma=0.97,noise=alls=7:allf=t,gblur=sigma=0.7,scale=1440:1080:flags=neighbor,drawgrid=w=0:h=4:t=1:c=black@0.18,vignette=PI/5,pad=1920:1080:240:0:black"
gfx="drawbox=x=300:y=60:w=110:h=44:color=0xCC0000@1:t=fill,drawtext=fontfile=$B:text='LIVE':fontcolor=white:fontsize=30:x=318:y=67,\
drawbox=x=1430:y=56:w=170:h=52:color=0x10204A@0.85:t=fill,drawbox=x=1430:y=56:w=170:h=6:color=0xF0A000@1:t=fill,drawtext=fontfile=$B:text='BIG AIR':fontcolor=white:fontsize=26:x=1448:y=70,\
drawbox=x=300:y=860:w=1100:h=64:color=0x10204A@0.9:t=fill,drawbox=x=300:y=860:w=12:h=124:color=0xF0A000@1:t=fill,drawtext=fontfile=$B:text='$l1':fontcolor=white:fontsize=40:x=332:y=872,\
drawbox=x=300:y=924:w=1100:h=60:color=0xE8E8E8@0.92:t=fill,drawtext=fontfile=$R:text='$l2':fontcolor=0x10204A:fontsize=32:x=332:y=938"
if [ -n "$score" ]; then gfx="$gfx,drawbox=x=1200:y=760:w=400:h=84:color=0xF0A000@1:t=fill:enable='gte(t,$sfrom)',drawtext=fontfile=$B:text='$score':fontcolor=0x10204A:fontsize=44:x=1228:y=780:enable='gte(t,$sfrom)'"; fi
case "$out" in
  *.png) ffmpeg -loglevel error -y -i "$in" -vf "$look,$gfx" -frames:v 1 "$out" ;;
  *) ffmpeg -loglevel error -y -i "$in" -vf "$look,$gfx" -af "highpass=f=120,lowpass=f=9000,acompressor=threshold=-18dB:ratio=3" -r 25 -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac "$out" ;;
esac
