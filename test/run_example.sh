#!/usr/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_ROOT=$(readlink -f $DIR/..)
if [ ! -z "$2" ]
  then
    PYTHON=$1
    EXAMPLE=$2
    export PYTHONPATH=$PROJECT_ROOT:$PYTHONPATH
    if [ ! -f "$EXAMPLE" ]
      then
        echo "'$EXAMPLE' example not found"
        exit 1
    fi
    $PYTHON $EXAMPLE
    exit 0
fi
echo "Usage: ${BASH_SOURCE[0]} <python_runnable> <example_base_name>"