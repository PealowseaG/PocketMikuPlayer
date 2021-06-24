#!/bin/bash
# change directory to this script being
SCRIPT_DIR=$(cd $(dirname $0); pwd)
echo "This script base directory is ""$SCRIPT_DIR"

# set the port# of NSX-(39) to MIDI_OUT
MIDI_OUT=$(aplaymidi -l | grep NSX- | awk '{print $1}')
echo "Pocket Miku's port is ""$MIDI_OUT"

# check MIDI_KEY(microKEY-) connected
MIDI_KEY=microKEY-
COUNT01=$(aplaymidi -l | grep -c $MIDI_KEY)
# Case: one microKEY connected
if [ $COUNT01 -eq 1 ];then
# set the port# of MIDI_KEY to MIDI_IN
MIDI_IN=$(aplaymidi -l | grep $MIDI_KEY | awk '{print $1}')
# connect MIDI_IN to MIDI_OUT
aconnect $MIDI_IN $MIDI_OUT
echo "MIDI_KEY's port is ""$MIDI_IN"
fi
# Case: No actual MIDI_KEY
if [ $COUNT01 -lt 1 -o $COUNT01 -gt 1 ];then
echo No actual "$MIDI_KEY"
fi

# pocketmiku_player after change dir of (this).sh
cd $SCRIPT_DIR
python3 pocketmiku_player.py

# Case : quit (=0)
# disconnect MIDI_IN to MIDI_OUT
aconnect -x
# disable variable values
unset COUNT01
unset MIDI_IN
unset MIDI_KEY
unset MIDI_OUT
unset SCRIPT_DIR
echo $COUNT01,$INPUT01,$MIDI_IN,$MIDI_KEY,$MIDI_OUT,$SCRIPT_DIR
# shutdown
sudo shutdown now
# exit
exit 0
