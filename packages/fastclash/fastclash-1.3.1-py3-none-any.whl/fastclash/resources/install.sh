# shellcheck disable=SC2148
# shellcheck disable=SC1091
. script/common.sh >&/dev/null
. script/fastclash.sh >&/dev/null
. script/download.sh >&/dev/null

_valid_env

[ -d "$CLASH_BASE_DIR" ] && _error_quit "请先执行卸载脚本,以清除安装路径：$CLASH_BASE_DIR"

# 下载必需资源（如果本地没有）
_download_required_resources || _error_quit "资源下载失败，请检查网络连接"

_get_kernel

/usr/bin/install -D <(gzip -dc "$ZIP_KERNEL") "${RESOURCES_BIN_DIR}/$BIN_KERNEL_NAME"
tar -xf "$ZIP_SUBCONVERTER" -C "$RESOURCES_BIN_DIR"
tar -xf "$ZIP_YQ" -C "${RESOURCES_BIN_DIR}"
# shellcheck disable=SC2086
/bin/mv -f ${RESOURCES_BIN_DIR}/yq_* "${RESOURCES_BIN_DIR}/yq"

_set_bin "$RESOURCES_BIN_DIR"
_valid_config "$RESOURCES_CONFIG" || {
    # 检查是否通过环境变量传递了订阅链接
    if [ -n "$CLASH_SUBSCRIPTION_URL" ]; then
        url="$CLASH_SUBSCRIPTION_URL"
        _okcat '✈️ ' "使用订阅：$url"
    else
        echo -n "$(_okcat '✈️ ' '输入订阅：')"
        read -r url
    fi
    _okcat '⏳' '正在下载...'
    _download_config "$RESOURCES_CONFIG" "$url" || _error_quit "下载失败: 请将配置内容写入 $RESOURCES_CONFIG 后重新安装"
    _valid_config "$RESOURCES_CONFIG" || _error_quit "配置无效，请检查配置：$RESOURCES_CONFIG，转换日志：$BIN_SUBCONVERTER_LOG"
}
_okcat '✅' '配置可用'
: "${url:=}"

_sudo mkdir -p "$CLASH_BASE_DIR"
echo "$url" | _sudo tee "$CLASH_CONFIG_URL" >&/dev/null

_sudo /bin/cp -rf "$SCRIPT_BASE_DIR" "$CLASH_BASE_DIR"
for resource in "$RESOURCES_BASE_DIR"/*; do
    name=$(basename "$resource")
    case "$name" in
        zip|png) continue ;;
        *) _sudo /bin/cp -rf "$resource" "$CLASH_BASE_DIR" ;;
    esac
done
_sudo tar -xf "$ZIP_UI" -C "$CLASH_BASE_DIR"

_set_rc
_set_bin

_sudo mkdir -p "$CLASH_SERVICE_DIR"

if [[ "$FASTCLASH_INSTALL_SCOPE" = "system" ]]; then
    target_unit='multi-user.target'
else
    target_unit='default.target'
fi

_sudo tee "${CLASH_SERVICE_DIR}/${BIN_KERNEL_NAME}.service" >/dev/null <<EOF
[Unit]
Description=$BIN_KERNEL_NAME Daemon, A[nother] Clash Kernel.

[Service]
Type=simple
Restart=always
ExecStart=${BIN_KERNEL} -d ${CLASH_BASE_DIR} -f ${CLASH_CONFIG_RUNTIME}

[Install]
WantedBy=${target_unit}
EOF

_systemctl daemon-reload
if _systemctl enable "$BIN_KERNEL_NAME" >&/dev/null; then
    _okcat '🚀' "已设置开机自启"
else
    _failcat '💥' "设置自启失败"
fi

_merge_config_restart

wrapper_path="${CLASH_BIN_DIR}/clash"
_sudo mkdir -p "$(dirname "$wrapper_path")"
_sudo tee "$wrapper_path" >/dev/null <<EOF
#!/bin/bash
export FASTCLASH_INSTALL_SCOPE="${FASTCLASH_INSTALL_SCOPE}"
export FASTCLASH_SYSTEM_MODE="${FASTCLASH_SYSTEM_MODE}"
source "${CLASH_SCRIPT_DIR}/common.sh"
source "${CLASH_SCRIPT_DIR}/fastclash.sh"
clash "\$@"
EOF
_sudo chmod +x "$wrapper_path"

_clash_ui
_okcat '🎉' "$(_msg 'enjoy')"
_okcat '[TIP]' "执行 clash on 开启代理环境"
_quit
