#!/bin/bash

PYOMLX_HOME="$HOME/.pyomlx"
PYOMLX_VENV="$PYOMLX_HOME/.venv"
PYOMLX_SERVER_PID="pid.txt"
PYOMLX_VERSION_FILE="$PYOMLX_HOME/version.txt"
PYOMLX_VERSION="0.1.1"  # assuming this is your pyomlx version
SCRIPT_HOME=$1
PYOMLX_STARTUP_LOG="/tmp/pyomlx-startup.log"
PYOMLX_LOG="/tmp/pyomlx-running.log"

# Function to check if Python 3.11 is installed and return its path
is_python3_11_installed() {
    # Define common paths to check, including Homebrew installations
    local paths_to_check=(
        "/usr/bin/python3"
        "/usr/local/bin/python3"
        "/opt/homebrew/bin/python3"
        "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"
    )

    # Check each path
    for path in "${paths_to_check[@]}"; do
        if [ -x "$path" ]; then  # Check if the path exists and is executable
            echo "$path"  # Return the path if found
            return 0      # Return success
        fi
    done

    echo ""  # Return an empty string if not found
    return 1  # Return failure
}

# Usage of the function in an if/else statement
python_path=$(is_python3_11_installed)


# Use the output in an if/else statement
if [ -n "$python_path" ]; then
    echo "Python 3.11 is installed at: $python_path" >> $PYOMLX_LOG
else
    echo "Python 3.11 is not installed. Due to sentencepiece requirement, PyOMlx needs Python 3.11" >> $PYOMLX_STARTUP_LOG
    exit 1
fi

install_pyomlx() {
    echo "Entering install" >> $PYOMLX_LOG
    mkdir -p $PYOMLX_HOME
    cd $PYOMLX_HOME
    echo "Inside install" >> $PYOMLX_LOG
    $python_path -m venv .venv
    . .venv/bin/activate
    echo "Activated env" >> $PYOMLX_LOG
    cp $SCRIPT_HOME/*.txt .
    echo "$PYOMLX_VERSION" > $PYOMLX_VERSION_FILE
    $PYOMLX_VENV/bin/pip install -r requirements.txt
    echo "Finished install" >> $PYOMLX_LOG
}

run_pyomlx() {
    cd $PYOMLX_HOME
    . .venv/bin/activate
    nohup mlx_lm.server --host 127.0.0.1 --port 11435 --use-default-chat-template > /dev/null 2>&1 &
    pid=$!
    echo $pid > $PYOMLX_SERVER_PID
}

#test for the presence of pyomlxhome and .venv inside
if [ -d $PYOMLX_VENV ]; then
    echo "Directory exists. Hence re-use" >> $PYOMLX_LOG
    
    if [ -f $PYOMLX_VERSION_FILE ]; then
        expected_version=$(cat $PYOMLX_VERSION_FILE)
        if [ "$expected_version" = "$PYOMLX_VERSION" ]; then
            # Version is correct, proceed to activate and run server
            echo "Version is correct, proceed to activate and run server" >> $PYOMLX_LOG
            run_pyomlx
        else
            # Version is incorrect, create new version file and proceed to install requirements
            echo "Version is incorrect, create new version file and proceed to install requirements" >> $PYOMLX_LOG
            rm -rf $PYOMLX_HOME
            install_pyomlx
            run_pyomlx
        fi
    else
        # Version file does not exist, create it and proceed to install requirements
        echo "Version file does not exist, create it and proceed to install requirements" >> $PYOMLX_LOG
        rm -rf $PYOMLX_HOME
        install_pyomlx
        run_pyomlx
    fi
    
else
    echo "Brand new install" >> $PYOMLX_LOG
    install_pyomlx
    run_pyomlx
fi