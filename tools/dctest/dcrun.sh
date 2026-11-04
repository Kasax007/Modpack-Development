#!/bin/sh
# dcrun.sh NAME [gradle -P args...] : one locked run of the Dreamcraft test client (Xvfb :96 started and stopped here).
# Output: $OUT/NAME.log (gradle + game log), screenshots stay in the run dir and are moved to $OUT/NAME/.
SP=/tmp/claude-0/-home-user/4ca9508b-4f8c-5a8e-91dc-6059d6cc887c/scratchpad
OUT=$SP/v13/run
NAME=$1; shift
export JAVA_HOME=/opt/jdk25/jdk-25.0.5+8
cd /home/user/dctest
RUN=/home/user/dctest/build/run/client
mkdir -p $OUT/$NAME
ls $RUN/screenshots > $OUT/$NAME.before 2>/dev/null
Xvfb :96 -screen 0 1920x1080x24 >/dev/null 2>&1 &
XPID=$!
sleep 2
DISPLAY=:96 SDL_VIDEO_FORCE_EGL=1 timeout ${DC_TIMEOUT:-900} sh ./gradlew --no-daemon -q runPack -Pxmx=5G "$@" > $OUT/$NAME.log 2>&1
echo "exit $?" >> $OUT/$NAME.log
kill $XPID 2>/dev/null
cp $RUN/logs/latest.log $OUT/$NAME.latest.log 2>/dev/null
ls $RUN/screenshots | grep -vxF -f $OUT/$NAME.before | while read f; do mv "$RUN/screenshots/$f" $OUT/$NAME/; done
echo done $NAME
