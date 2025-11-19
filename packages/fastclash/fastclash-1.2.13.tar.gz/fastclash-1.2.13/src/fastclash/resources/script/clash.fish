set -gx fish_version $FISH_VERSION
set -gx clash_proxy_file "$HOME/.cache/clash/proxy.env"

function __clash_sync_env --argument file
    if test -f $file
        for line in (cat $file)
            set -l key (echo $line | cut -d'=' -f1)
            set -l value (echo $line | cut -d'=' -f2-)
            set -gx $key $value
        end
    end
end

function clash
    bash -i -c "clash $argv"
    return $status
end

function clash-on
    set -l file $clash_proxy_file
    mkdir -p (dirname $file)
    bash -i -c "clash on; env | grep -E '^(http|https|all|no|HTTP|HTTPS|ALL|NO)_PROXY=' > \"$file\""
    __clash_sync_env $file
end

function clash-off
    bash -i -c "clash off"
    set -e http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY no_proxy NO_PROXY
    rm -f $clash_proxy_file
end
