#!/bin/sh

PYOMLX_HOME="$HOME/.pyomlx"
PYOMLX_VENV="$PYOMLX_HOME/.venv"
FLASK_APP_PID_FILE="pid.txt"
SCRIPT_HOME=$(pwd)

pid=$(cat "$PYOMLX_HOME/$FLASK_APP_PID_FILE")
kill -9 $pid
echo "Stopped.."

