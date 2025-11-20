#!/bin/bash
# Gitee 资源下载管理脚本

# Gitee 仓库配置
GITEE_REPO="https://gitee.com/whillhill/fastclash/raw/main"
GITEE_REPO_MIRROR="https://gitee.com/whillhill/fastclash/raw/master"  # 备用分支

# 下载函数
_download_from_gitee() {
    local remote_path=$1
    local local_path=$2
    local description=${3:-"资源文件"}
    
    echo "📥 正在下载 ${description}..."
    
    # 尝试主分支
    if curl -fsSL --connect-timeout 10 --retry 2 \
        -o "$local_path" \
        "${GITEE_REPO}/${remote_path}" 2>/dev/null; then
        echo "✅ ${description} 下载成功"
        return 0
    fi
    
    # 尝试备用分支
    if curl -fsSL --connect-timeout 10 --retry 2 \
        -o "$local_path" \
        "${GITEE_REPO_MIRROR}/${remote_path}" 2>/dev/null; then
        echo "✅ ${description} 下载成功 (备用源)"
        return 0
    fi
    
    # 使用 wget 重试
    if wget -q --timeout=10 --tries=2 \
        -O "$local_path" \
        "${GITEE_REPO}/${remote_path}" 2>/dev/null; then
        echo "✅ ${description} 下载成功 (wget)"
        return 0
    fi
    
    echo "❌ ${description} 下载失败"
    return 1
}

# 检查并下载资源
_ensure_resource() {
    local resource_type=$1
    local local_file=$2
    local remote_path=$3
    local description=$4
    
    # 如果本地已存在且非空，跳过下载
    if [ -f "$local_file" ] && [ -s "$local_file" ]; then
        echo "✓ ${description} 已存在"
        return 0
    fi
    
    # 创建目录
    mkdir -p "$(dirname "$local_file")"
    
    # 下载资源
    if _download_from_gitee "$remote_path" "$local_file" "$description"; then
        # 设置权限（如果是可执行文件）
        case "$resource_type" in
            "binary"|"script")
                chmod +x "$local_file" 2>/dev/null
                ;;
        esac
        return 0
    else
        rm -f "$local_file"  # 清理失败的下载
        return 1
    fi
}

# 批量下载必需资源
_download_required_resources() {
    local failed=0
    
    echo "🔍 检查必需资源..."
    
    # Country.mmdb (GeoIP 数据库)
    if ! [ -f "$RESOURCES_BASE_DIR/Country.mmdb" ]; then
        _ensure_resource "data" \
            "$RESOURCES_BASE_DIR/Country.mmdb" \
            "resources/Country.mmdb" \
            "GeoIP 数据库" || ((failed++))
    fi
    
    # mixin.yaml (默认配置)
    if ! [ -f "$RESOURCES_BASE_DIR/mixin.yaml" ]; then
        _ensure_resource "config" \
            "$RESOURCES_BASE_DIR/mixin.yaml" \
            "resources/mixin.yaml" \
            "Mixin 配置" || ((failed++))
    fi
    
    # mihomo 内核
    if ! [ -f "$ZIP_MIHOMO" ] && ! [ -f "$ZIP_CLASH" ]; then
        local arch=$(uname -m)
        local mihomo_file="mihomo-linux-${arch}-compatible-v1.19.2.gz"
        
        # 尝试下载对应架构的 mihomo
        _ensure_resource "binary" \
            "$ZIP_BASE_DIR/${mihomo_file}" \
            "binaries/mihomo/${mihomo_file}" \
            "Mihomo 内核 (${arch})" || {
            # 如果失败，尝试下载默认的 amd64 版本
            _ensure_resource "binary" \
                "$ZIP_BASE_DIR/mihomo-linux-amd64-compatible-v1.19.2.gz" \
                "binaries/mihomo/mihomo-linux-amd64-compatible-v1.19.2.gz" \
                "Mihomo 内核 (amd64 fallback)" || ((failed++))
        }
    fi
    
    # subconverter (订阅转换器)
    if ! [ -f "$ZIP_SUBCONVERTER" ]; then
        _ensure_resource "binary" \
            "$ZIP_BASE_DIR/subconverter_linux64.tar.gz" \
            "binaries/subconverter/subconverter_linux64.tar.gz" \
            "订阅转换器" || ((failed++))
    fi
    
    # yacd (Web UI)
    if ! [ -f "$ZIP_UI" ]; then
        _ensure_resource "binary" \
            "$ZIP_BASE_DIR/yacd.tar.xz" \
            "binaries/yacd/yacd.tar.xz" \
            "Web 控制台" || ((failed++))
    fi
    
    # yq (YAML 处理器)
    if ! [ -f "$ZIP_YQ" ]; then
        _ensure_resource "binary" \
            "$ZIP_BASE_DIR/yq_linux_amd64.tar.gz" \
            "binaries/yq/yq_linux_amd64.tar.gz" \
            "YAML 处理器" || ((failed++))
    fi
    
    if [ $failed -gt 0 ]; then
        echo "⚠️  有 $failed 个资源下载失败"
        return 1
    else
        echo "✅ 所有必需资源已就绪"
        return 0
    fi
}

# 下载可选资源
_download_optional_resources() {
    # Fish shell 配置
    if command -v fish >/dev/null 2>&1; then
        if ! [ -f "$SHELL_RC_FISH" ]; then
            echo "🐟 检测到 Fish Shell，下载配置文件..."
            _ensure_resource "script" \
                "$SHELL_RC_FISH" \
                "scripts/clash.fish" \
                "Fish 配置"
        fi
    fi
}

# 版本检查（可选功能）
_check_resource_updates() {
    local versions_file="/tmp/fastclash-versions.json"
    
    if _download_from_gitee "versions.json" "$versions_file" "版本信息"; then
        # 这里可以添加版本比对逻辑
        echo "📋 已获取最新版本信息"
        rm -f "$versions_file"
    fi
}

# 导出函数供其他脚本使用
export -f _download_from_gitee
export -f _ensure_resource
export -f _download_required_resources
export -f _download_optional_resources
export -f _check_resource_updates
