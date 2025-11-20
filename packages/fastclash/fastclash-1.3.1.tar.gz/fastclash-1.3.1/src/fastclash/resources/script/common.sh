# shellcheck disable=SC2148
# shellcheck disable=SC2034
# shellcheck disable=SC2155
[ -n "$BASH_VERSION" ] && set +o noglob
[ -n "$ZSH_VERSION" ] && setopt glob no_nomatch

# ==================== 消息字典（仅中文） ====================
declare -A MSG
MSG["proxy_on"]="😼 已开启代理环境"
MSG["proxy_off"]="😼 已关闭代理环境"
MSG["proxy_enabled"]="😼 系统代理：开启"
MSG["proxy_disabled"]="😼 系统代理：关闭"
MSG["tun_enabled"]="😼 Tun 模式已开启"
MSG["tun_disabled"]="😼 Tun 模式已关闭"
MSG["tun_status_on"]="😼 Tun 状态：开启"
MSG["tun_status_off"]="😾 Tun 状态：关闭"
MSG["secret_updated"]="😼 密钥更新成功，已重启生效"
MSG["current_secret"]="😼 当前密钥："
MSG["update_success"]="🍃 订阅更新成功"
MSG["update_downloading"]="👌 正在下载：原配置已备份..."
MSG["update_validating"]="🍃 下载成功：内核验证配置..."
MSG["auto_update_set"]="😼 已设置定时更新订阅"
MSG["mixin_view"]="😼 less 查看 mixin 配置"
MSG["mixin_edit"]="😼 vim 编辑 mixin 配置"
MSG["mixin_runtime"]="😼 less 查看 运行时 配置"
MSG["web_console"]="😼 Web 控制台"
MSG["note_open_port"]="🔓 注意放行端口：9090"
MSG["panel_address"]="🌍 面板地址：http://127.0.0.1:9090/ui"
MSG["uninstalled"]="✨ 已卸载，相关配置已清除"
MSG["enjoy"]="🎉 安装完成，开始使用吧"
MSG["config_updated"]="配置更新成功，已重启生效"

_msg() {
    local key="$1"
    echo "${MSG[$key]:-$key}"
}
# ==================== 消息字典结束 ====================

# ==================== 安装模式配置 ====================
FASTCLASH_INSTALL_SCOPE=${FASTCLASH_INSTALL_SCOPE:-user}
FASTCLASH_SYSTEM_MODE=${FASTCLASH_SYSTEM_MODE:-0}

if [[ "$FASTCLASH_INSTALL_SCOPE" = "system" || "$FASTCLASH_SYSTEM_MODE" = "1" ]]; then
    FASTCLASH_INSTALL_SCOPE="system"
    FASTCLASH_SYSTEM_MODE=1
else
    FASTCLASH_INSTALL_SCOPE="user"
    FASTCLASH_SYSTEM_MODE=0
fi
# ==================== 安装模式配置结束 ====================

URL_GH_PROXY='https://gh-proxy.com/'
URL_CLASH_UI="http://board.zash.run.place"
URL_FISH_SCRIPT="https://raw.githubusercontent.com/whillhill/fastclash/main/src/fastclash/resources/script/clash.fish"

SCRIPT_BASE_DIR='./script'

RESOURCES_BASE_DIR='./resources'
RESOURCES_BIN_DIR="${RESOURCES_BASE_DIR}/bin"
RESOURCES_CONFIG="${RESOURCES_BASE_DIR}/config.yaml"
RESOURCES_CONFIG_MIXIN="${RESOURCES_BASE_DIR}/mixin.yaml"

ZIP_BASE_DIR="${RESOURCES_BASE_DIR}/zip"
ZIP_CLASH=$(echo ${ZIP_BASE_DIR}/clash*)
ZIP_MIHOMO=$(echo ${ZIP_BASE_DIR}/mihomo*)
ZIP_YQ=$(echo ${ZIP_BASE_DIR}/yq*)
ZIP_SUBCONVERTER=$(echo ${ZIP_BASE_DIR}/subconverter*)
ZIP_UI="${ZIP_BASE_DIR}/yacd.tar.xz"

_set_var() {
    local user=$USER
    local home=$HOME
    [ -n "$SUDO_USER" ] && {
        user=$SUDO_USER
        home=$(awk -F: -v user="$SUDO_USER" '$1==user{print $6}' /etc/passwd)
    }

    FASTCLASH_EFFECTIVE_USER="$user"
    FASTCLASH_EFFECTIVE_HOME="$home"

    if [[ "$FASTCLASH_INSTALL_SCOPE" = "system" ]]; then
        CLASH_BASE_DIR='/opt/clash'
        CLASH_SERVICE_DIR='/etc/systemd/system'
        CLASH_BIN_DIR='/usr/local/bin'
        SYSTEMCTL_CMD='systemctl'
        JOURNALCTL_CMD='journalctl'
        SUDO_PREFIX='sudo'
    else
        CLASH_BASE_DIR="${home}/.local/share/clash"
        CLASH_SERVICE_DIR="${home}/.config/systemd/user"
        CLASH_BIN_DIR="${home}/.local/bin"
        SYSTEMCTL_CMD='systemctl --user'
        JOURNALCTL_CMD='journalctl --user'
        SUDO_PREFIX=''
    fi

    CLASH_SCRIPT_DIR="${CLASH_BASE_DIR}/$(basename $SCRIPT_BASE_DIR)"
    CLASH_CONFIG_URL="${CLASH_BASE_DIR}/url"
    CLASH_CONFIG_RAW="${CLASH_BASE_DIR}/$(basename $RESOURCES_CONFIG)"
    CLASH_CONFIG_RAW_BAK="${CLASH_CONFIG_RAW}.bak"
    CLASH_CONFIG_MIXIN="${CLASH_BASE_DIR}/$(basename $RESOURCES_CONFIG_MIXIN)"
    CLASH_CONFIG_RUNTIME="${CLASH_BASE_DIR}/runtime.yaml"
    CLASH_UPDATE_LOG="${CLASH_BASE_DIR}/fastclash-update.log"

    [ -n "$BASH_VERSION" ] && {
        _SHELL=bash
    }
    [ -n "$ZSH_VERSION" ] && {
        _SHELL=zsh
    }
    [ -n "$fish_version" ] && {
        _SHELL=fish
    }

    # rc配置文件
    command -v bash >&/dev/null && {
        SHELL_RC_BASH="${home}/.bashrc"
    }
    command -v zsh >&/dev/null && {
        SHELL_RC_ZSH="${home}/.zshrc"
    }
    command -v fish >&/dev/null && {
        SHELL_RC_FISH="${home}/.config/fish/conf.d/clash.fish"
    }

    # 系统信息
    local os_info=$(cat /etc/os-release)
    if [[ "$FASTCLASH_INSTALL_SCOPE" = "system" ]]; then
        echo "$os_info" | grep -iqsE "rhel|centos" && CLASH_CRON_TAB="/var/spool/cron/$user"
        echo "$os_info" | grep -iqsE "debian|ubuntu" && CLASH_CRON_TAB="/var/spool/cron/crontabs/$user"
    else
        CLASH_CRON_TAB="${CLASH_BASE_DIR}/fastclash-cron"
    fi
}
_set_var

_sudo() {
    if [[ "$SUDO_PREFIX" = "sudo" ]]; then
        sudo "$@"
    else
        "$@"
    fi
}

_systemctl() {
    if [[ "$SUDO_PREFIX" = "sudo" ]]; then
        sudo $SYSTEMCTL_CMD "$@"
    else
        $SYSTEMCTL_CMD "$@"
    fi
}

_journalctl() {
    if [[ "$SUDO_PREFIX" = "sudo" ]]; then
        sudo $JOURNALCTL_CMD "$@"
    else
        $JOURNALCTL_CMD "$@"
    fi
}

# shellcheck disable=SC2120
_set_bin() {
    local bin_base_dir="${CLASH_BASE_DIR}/bin"
    [ -n "$1" ] && bin_base_dir=$1
    BIN_CLASH="${bin_base_dir}/clash"
    BIN_MIHOMO="${bin_base_dir}/mihomo"
    BIN_YQ="${bin_base_dir}/yq"
    BIN_SUBCONVERTER_DIR="${bin_base_dir}/subconverter"
    BIN_SUBCONVERTER_CONFIG="$BIN_SUBCONVERTER_DIR/pref.yml"
    BIN_SUBCONVERTER_PORT="25500"
    BIN_SUBCONVERTER="${BIN_SUBCONVERTER_DIR}/subconverter"
    BIN_SUBCONVERTER_LOG="${BIN_SUBCONVERTER_DIR}/latest.log"

    [ -f "$BIN_CLASH" ] && {
        BIN_KERNEL=$BIN_CLASH
    }
    [ -f "$BIN_MIHOMO" ] && {
        BIN_KERNEL=$BIN_MIHOMO
    }
    BIN_KERNEL_NAME=$(basename "$BIN_KERNEL")
}
_set_bin

_set_rc() {
    local rc_line="source $CLASH_SCRIPT_DIR/common.sh && source $CLASH_SCRIPT_DIR/fastclash.sh && watch_proxy"

    if [ "$1" = "unset" ]; then
        [ -n "$SHELL_RC_BASH" ] && sed -i "\|$CLASH_SCRIPT_DIR|d" "$SHELL_RC_BASH" 2>/dev/null
        [ -n "$SHELL_RC_ZSH" ] && sed -i "\|$CLASH_SCRIPT_DIR|d" "$SHELL_RC_ZSH" 2>/dev/null
        [ -n "$SHELL_RC_FISH" ] && rm -f "$SHELL_RC_FISH" 2>/dev/null
        return
    fi

    if [ -n "$SHELL_RC_BASH" ]; then
        mkdir -p "$(dirname "$SHELL_RC_BASH")"
        grep -Fqs "$CLASH_SCRIPT_DIR/fastclash.sh" "$SHELL_RC_BASH" 2>/dev/null || echo "$rc_line" >>"$SHELL_RC_BASH"
    fi

    if [ -n "$SHELL_RC_ZSH" ]; then
        mkdir -p "$(dirname "$SHELL_RC_ZSH")"
        grep -Fqs "$CLASH_SCRIPT_DIR/fastclash.sh" "$SHELL_RC_ZSH" 2>/dev/null || echo "$rc_line" >>"$SHELL_RC_ZSH"
    fi

    if [ -n "$SHELL_RC_FISH" ]; then
        mkdir -p "$(dirname "$SHELL_RC_FISH")"
        curl \
            --silent \
            --show-error \
            --fail \
            --location \
            --output "$SHELL_RC_FISH" \
            "$URL_FISH_SCRIPT" || \
        wget \
            --no-verbose \
            --no-check-certificate \
            --timeout 5 \
            --tries 1 \
            --output-document "$SHELL_RC_FISH" \
            "$URL_FISH_SCRIPT"
        chmod 755 "$SHELL_RC_FISH"
    fi
}

# 获取内核文件mihomo优先
# 如果存在mihomo则优先使用clash作为备选
function _get_kernel() {
    [ -f "$ZIP_CLASH" ] && {
        ZIP_KERNEL=$ZIP_CLASH
        BIN_KERNEL=$BIN_CLASH
    }

    [ -f "$ZIP_MIHOMO" ] && {
        ZIP_KERNEL=$ZIP_MIHOMO
        BIN_KERNEL=$BIN_MIHOMO
    }

    [ ! -f "$ZIP_MIHOMO" ] && [ ! -f "$ZIP_CLASH" ] && {
        local arch=$(uname -m)
        _failcat "${ZIP_BASE_DIR} 目录下没有内核文件"
        _download_clash "$arch"
        ZIP_KERNEL=$ZIP_CLASH
        BIN_KERNEL=$BIN_CLASH
    }

    BIN_KERNEL_NAME=$(basename "$BIN_KERNEL")
    _okcat "使用内核：$BIN_KERNEL_NAME"
}

_get_random_port() {
    local randomPort=$(shuf -i 1024-65535 -n 1)
    ! _is_bind "$randomPort" && { echo "$randomPort" && return; }
    _get_random_port
}

function _get_proxy_port() {
    local mixed_port=$(_sudo "$BIN_YQ" '.mixed-port // ""' $CLASH_CONFIG_RUNTIME)
    MIXED_PORT=${mixed_port:-7890}

    _is_already_in_use "$MIXED_PORT" "$BIN_KERNEL_NAME" && {
        local newPort=$(_get_random_port)
        local msg="代理端口${MIXED_PORT} 被占用 已更换为$newPort"
        _sudo "$BIN_YQ" -i ".mixed-port = $newPort" $CLASH_CONFIG_RUNTIME
        MIXED_PORT=$newPort
        _failcat '⚠️' "$msg"
    }
}

function _get_ui_port() {
    local ext_addr=$(_sudo "$BIN_YQ" '.external-controller // ""' $CLASH_CONFIG_RUNTIME)
    local ext_port=${ext_addr##*:}
    UI_PORT=${ext_port:-9090}

    _is_already_in_use "$UI_PORT" "$BIN_KERNEL_NAME" && {
        local newPort=$(_get_random_port)
        local msg="控制端口${UI_PORT} 被占用 已更换为$newPort"
        _sudo "$BIN_YQ" -i ".external-controller = \"0.0.0.0:$newPort\"" $CLASH_CONFIG_RUNTIME
        UI_PORT=$newPort
        _failcat '⚠️' "$msg"
    }
}

_get_color() {
    local hex="${1#\#}"
    local r=$((16#${hex:0:2}))
    local g=$((16#${hex:2:2}))
    local b=$((16#${hex:4:2}))
    printf "\e[38;2;%d;%d;%dm" "$r" "$g" "$b"
}
_get_color_msg() {
    local color=$(_get_color "$1")
    local msg=$2
    local reset="\033[0m"
    printf "%b%s%b\n" "$color" "$msg" "$reset"
}

function _okcat() {
    local color=#c8d6e5
    local emoji=✅
    [ $# -gt 1 ] && emoji=$1 && shift
    local msg="${emoji} $1"
    _get_color_msg "$color" "$msg" && return 0
}

function _failcat() {
    local color=#fd79a8
    local emoji=❌
    [ $# -gt 1 ] && emoji=$1 && shift
    local msg="${emoji} $1"
    _get_color_msg "$color" "$msg" >&2 && return 1
}

function _quit() {
    exec $_SHELL -i
}

function _error_quit() {
    [ $# -gt 0 ] && {
        local color=#f92f60
        local emoji=💥
        [ $# -gt 1 ] && emoji=$1 && shift
        local msg="${emoji} $1"
        _get_color_msg "$color" "$msg"
    }
    exec $_SHELL -i
}

_is_bind() {
    local port=$1
    # 优先尝试带进程信息的输出；失败则降级为无进程信息
    { ss -lnptu 2>/dev/null || netstat -lnptu 2>/dev/null || ss -lntu 2>/dev/null || netstat -lntu 2>/dev/null; } | grep ":${port}\b"
}

_is_already_in_use() {
    local port=$1
    local progress=$2
    local out
    out=$(_is_bind "$port")
    # 未绑定
    [ -z "$out" ] && return 1
    # 已绑定但能检测到是同一进程名，则不算占用
    echo "$out" | grep -qs "$progress" && return 1
    # 其他情况均视为被占用
    return 0
}

function _is_root() {
    [ "$(whoami)" = "root" ]
}

function _valid_env() {
    if [[ "$FASTCLASH_INSTALL_SCOPE" = "system" ]]; then
        _is_root || _error_quit "系统级安装需要 root 或 sudo 权限"
    fi
    [ -n "$ZSH_VERSION" ] && [ -n "$BASH_VERSION" ] && _error_quit "请不要同时使用bash和zsh"
    [ "$(ps -p 1 -o comm=)" != "systemd" ] && _error_quit "系统不支持 systemd"
}

function _valid_config() {
    local file="$1"
    [ -e "$file" ] && [ "$(wc -l <"$file")" -gt 1 ] || return 1
    local msg
    msg=$("$BIN_KERNEL" -d "$(dirname "$file")" -f "$file" -t 2>&1) || {
        "$BIN_KERNEL" -d "$(dirname "$file")" -f "$file" -t
        echo "$msg" | grep -qs "unsupport proxy type" && _error_quit "配置包含不支持的代理类型 请使用 mihomo 内核"
        return 1
    }
}

_download_clash() {
    local arch=$1
    local url sha256sum
    case "$arch" in
    x86_64)
        url=https://downloads.clash.wiki/ClashPremium/clash-linux-amd64-2023.08.17.gz
        sha256sum='92380f053f083e3794c1681583be013a57b160292d1d9e1056e7fa1c2d948747'
        ;;
    *86*)
        url=https://downloads.clash.wiki/ClashPremium/clash-linux-386-2023.08.17.gz
        sha256sum='254125efa731ade3c1bf7cfd83ae09a824e1361592ccd7c0cccd2a266dcb92b5'
        ;;
    armv*)
        url=https://downloads.clash.wiki/ClashPremium/clash-linux-armv5-2023.08.17.gz
        sha256sum='622f5e774847782b6d54066f0716114a088f143f9bdd37edf3394ae8253062e8'
        ;;
    aarch64)
        url=https://downloads.clash.wiki/ClashPremium/clash-linux-arm64-2023.08.17.gz
        sha256sum='c45b39bb241e270ae5f4498e2af75cecc0f03c9db3c0db5e55c8c4919f01afdd'
        ;;
    *)
        _error_quit "不支持的架构$arch，请手动下载内核到 ${ZIP_BASE_DIR} 目录，下载地址：https://downloads.clash.wiki/ClashPremium/"
        ;;
    esac

    _okcat '📥' "正在下载clash内核${arch} 版本..."
    local clash_zip="${ZIP_BASE_DIR}/$(basename $url)"
    curl \
        --progress-bar \
        --show-error \
        --fail \
        --insecure \
        --connect-timeout 15 \
        --retry 1 \
        --output "$clash_zip" \
        "$url"
    echo $sha256sum "$clash_zip" | sha256sum -c ||
        _error_quit "校验失败，请手动下载到 ${ZIP_BASE_DIR} 目录，下载地址：https://downloads.clash.wiki/ClashPremium/"
}

_download_raw_config() {
    local dest=$1
    local url=$2
    local agent='clash-verge/v2.0.4'
    curl \
        --silent \
        --show-error \
        --insecure \
        --connect-timeout 4 \
        --retry 1 \
        --user-agent "$agent" \
        --output "$dest" \
        "$url" ||
        wget \
            --no-verbose \
            --no-check-certificate \
            --timeout 3 \
            --tries 1 \
            --user-agent "$agent" \
            --output-document "$dest" \
            "$url"
}
_download_convert_config() {
    local dest=$1
    local url=$2
    _start_convert
    local convert_url=$(
        target='clash'
        base_url="http://127.0.0.1:${BIN_SUBCONVERTER_PORT}/sub"
        curl \
            --get \
            --silent \
            --output /dev/null \
            --data-urlencode "target=$target" \
            --data-urlencode "url=$url" \
            --write-out '%{url_effective}' \
            "$base_url"
    )
    _download_raw_config "$dest" "$convert_url"
    _stop_convert
}
function _download_config() {
    local dest=$1
    local url=$2
    [ "${url:0:4}" = 'file' ] && return 0
    _download_raw_config "$dest" "$url" || return 1
    _okcat '🔍' '正在验证配置文件...'
    _valid_config "$dest" || {
        _failcat '⚠️' "配置验证失败，尝试转换..."
        _download_convert_config "$dest" "$url" || _failcat '❌' "配置转换失败，查看日志：$BIN_SUBCONVERTER_LOG"
    }
}

_start_convert() {
    _is_already_in_use $BIN_SUBCONVERTER_PORT 'subconverter' && {
        local newPort=$(_get_random_port)
        _failcat '⚠️' "转换端口$BIN_SUBCONVERTER_PORT 被占用 已更换为$newPort"
        [ ! -e "$BIN_SUBCONVERTER_CONFIG" ] && {
            _sudo /bin/cp -f "$BIN_SUBCONVERTER_DIR/pref.example.yml" "$BIN_SUBCONVERTER_CONFIG"
        }
        _sudo "$BIN_YQ" -i ".server.port = $newPort" "$BIN_SUBCONVERTER_CONFIG"
        BIN_SUBCONVERTER_PORT=$newPort
    }
    local start=$(date +%s)
    # 启动shell子进程避免kill影响主进程
    ("$BIN_SUBCONVERTER" 2>&1 | tee "$BIN_SUBCONVERTER_LOG" >/dev/null &)
    while ! _is_bind "$BIN_SUBCONVERTER_PORT" >&/dev/null; do
        sleep 1s
        local now=$(date +%s)
        [ $((now - start)) -gt 1 ] && _error_quit "订阅转换服务启动失败，查看日志：$BIN_SUBCONVERTER_LOG"
    done
}
_stop_convert() {
    pkill -9 -f "$BIN_SUBCONVERTER" >&/dev/null
}
