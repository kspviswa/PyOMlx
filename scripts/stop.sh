#!/bin/sh

PYOMLX_HOME="$HOME/.pyomlx"
PYOMLX_VENV="$PYOMLX_HOME/.venv"
PYOMLX_SERVER_PID="pid.txt"
SCRIPT_HOME=$(pwd)

pid=$(cat "$PYOMLX_HOME/$PYOMLX_SERVER_PID")
kill -9 $pid
echo "Stopped.."

