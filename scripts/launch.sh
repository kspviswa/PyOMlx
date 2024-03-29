#!/bin/sh

PYOMLX_HOME="$HOME/.pyomlx"
PYOMLX_VENV="$PYOMLX_HOME/.venv"
FLASK_APP_PID_FILE="pid.txt"
SCRIPT_HOME=$1

#test for the presence of pyomlxhome and .venv inside
if [ -d $PYOMLX_VENV ]; then
    echo "Directory exists. Hence re-use"
    cd $PYOMLX_HOME
    . .venv/bin/activate
else
    # Create pyomlx home
    mkdir -p $PYOMLX_HOME
    cd $PYOMLX_HOME
    python3 -m venv .venv
    . .venv/bin/activate
    cp $SCRIPT_HOME/*.py .
    cp $SCRIPT_HOME/*.txt .
    $PYOMLX_VENV/bin/pip install -r requirements.txt
    
fi

nohup $PYOMLX_VENV/bin/python ./serveMlxPrompt.py > /dev/null 2>&1 &
pid=$!
echo $pid > $FLASK_APP_PID_FILE