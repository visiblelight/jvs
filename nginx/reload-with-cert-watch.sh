#!/bin/sh
# certbot renews certs on its own schedule but never tells nginx to pick them up.
# Reload is cheap and safe (nginx re-reads cert files without dropping connections),
# so just reload on the same 12h cadence as certbot's renew loop.
( while :; do sleep 12h; nginx -s reload; done ) &
exec /docker-entrypoint.sh nginx -g "daemon off;"
