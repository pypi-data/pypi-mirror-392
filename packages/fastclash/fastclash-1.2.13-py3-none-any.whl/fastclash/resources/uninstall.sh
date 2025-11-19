#!/bin/bash
# shellcheck disable=SC2148
# shellcheck disable=SC1091
. script/common.sh >&/dev/null
. script/fastclash.sh >&/dev/null

_valid_env

clash off >&/dev/null

_systemctl disable "$BIN_KERNEL_NAME" >&/dev/null
_sudo rm -f "${CLASH_SERVICE_DIR}/${BIN_KERNEL_NAME}.service"
_systemctl daemon-reload

_sudo rm -rf "$CLASH_BASE_DIR"

if [[ "$FASTCLASH_INSTALL_SCOPE" = "system" ]]; then
    _sudo sed -i '/clash update/d' "$CLASH_CRON_TAB" 2>/dev/null
else
    crontab -l 2>/dev/null | grep -v 'clash update' | crontab - || true
fi

_set_rc unset

_sudo rm -f "${CLASH_BIN_DIR}/clash"

_okcat '✨' "$(_msg 'uninstalled')"
_quit
