#!/bin/sh
# srv.sh start|stop|cmd "<command>"  -- the test dedicated server in $SP/srv (PID kept in srv/java.pid)
SP=/tmp/claude-0/-home-user/4ca9508b-4f8c-5a8e-91dc-6059d6cc887c/scratchpad
cd $SP/srv
case "$1" in
  start)
    rm -f console.fifo; mkfifo console.fifo
    : > server.out
    ( sleep 100000000 > console.fifo & echo $! > hold.pid; ) 
    /opt/jdk25/jdk-25.0.5+8/bin/java -Xmx${XMX:-6G} -jar fabric-server-launch.jar nogui < console.fifo > server.out 2>&1 &
    echo $! > java.pid
    echo "started $(cat java.pid)";;
  cmd)
    timeout 5 sh -c "echo \"$2\" > console.fifo";;
  stop)
    [ -f java.pid ] && kill -0 $(cat java.pid) 2>/dev/null && { timeout 5 sh -c "echo stop > console.fifo"; for i in 1 2 3 4 5 6 7 8 9 10 11 12; do kill -0 $(cat java.pid) 2>/dev/null || break; sleep 5; done; kill $(cat java.pid) 2>/dev/null; }
    [ -f hold.pid ] && kill $(cat hold.pid) 2>/dev/null
    rm -f java.pid hold.pid; echo stopped;;
esac
