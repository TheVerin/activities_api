#!/bin/sh
cores=$(nproc --all)
workers=$(($((cores))*2+1))
uwsgi -M -T \
-p "${workers}" \
--http 0.0.0.0:8000 \
--module core.wsgi:application \
--buffer-size 65535 \
--max-requests 2000 \
--max-worker-lifetime 3600 \
--harakiri 20 \
--limit-as 512