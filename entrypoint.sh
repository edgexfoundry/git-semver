#!/bin/bash

USER_ID=${LOCAL_UID:-9001}
GROUP_ID=${LOCAL_GID:-9001}

echo "Starting with UID: $USER_ID, GID: $GROUP_ID"
useradd -u $USER_ID -o -m user -d /home/user
groupmod -g $GROUP_ID user
chown -R user:user /home/user
export HOME=/home/user

# Set current working directory to safe
git config --global --add safe.directory "$PWD"

exec /usr/sbin/gosu user "$@"