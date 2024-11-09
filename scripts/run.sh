#!/bin/bash

# set environment variables - only for local development
# set -o allexport
# source .env
# set +o allexport

rq worker "worker" --with-scheduler -c db.redis_connection &
python save_logs.py &
gunicorn main:app --worker-tmp-dir /dev/shm --config gunicorn.config.py &
wait
