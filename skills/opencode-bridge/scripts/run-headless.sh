#!/bin/sh
# Arca bridge: run a verified OpenCode binary with noninteractive stdin at EOF.
# The caller owns task authorization, session correlation and bounded supervision.
set -eu

if [ "$#" -lt 2 ]; then
    printf 'usage: sh run-headless.sh /absolute/path/to/opencode [run-options-and-message...]\n' >&2
    exit 64
fi

binary=$1
shift
case "$binary" in
    /*) ;;
    *)
        printf 'error: OpenCode executable must be an absolute verified path\n' >&2
        exit 64
        ;;
esac
if [ ! -f "$binary" ] || [ ! -x "$binary" ]; then
    printf 'error: OpenCode executable unavailable\n' >&2
    exit 69
fi

# OpenCode 1.18.35 may await EOF on inherited non-TTY pipes even with a
# complete argv prompt or --file; close stdin before OpenCode starts.
# Preserve argv and exit status; do not add --auto, --model or --variant.
exec "$binary" run "$@" </dev/null
