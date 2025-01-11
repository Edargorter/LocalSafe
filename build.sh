#!/bin/bash

cmd="pyinstaller"
specfile="local_safe.spec"

if ! command -v $cmd 2>&1 >/dev/null
then
    echo "$cmd could not be found"
    exit 1
fi

eval "$cmd $specfile"
