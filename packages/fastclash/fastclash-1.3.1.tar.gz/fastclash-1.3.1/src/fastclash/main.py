#!/usr/bin/env python3
"""
fastclash 主入口文件

职责：
- 安装 / 卸载 Clash 运行环境
- 初始化脚本资源（可选）

所有运行时操作改为通过 clash 命令完成。
"""

import sys
import click

from . import __version__
from .init import ClashInitializer


def check_environment():
    """检查基本运行环境"""
    if sys.platform != 'linux':
        click.echo("[ERROR] fastclash 仅支持 Linux 系统", err=True)
        sys.exit(1)

    if sys.version_info < (3, 8):
        click.echo("[ERROR] 需要 Python 3.8 或更高版本", err=True)
        sys.exit(1)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """
    fastclash - Clash 运行环境安装器

    默认执行用户级安装。
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
def install():
    """安装 Clash 运行环境（用户级，无需 sudo）"""
    try:
        check_environment()

        initializer = ClashInitializer(
            mode='install',
            system_mode=False,
        )
        initializer.run()

    except KeyboardInterrupt:
        click.echo("\n[ERROR] 操作被用户中断", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"[ERROR] 安装失败: {e}", err=True)
        sys.exit(1)


@cli.command()
def uninstall():
    """卸载 Clash 运行环境"""
    try:
        check_environment()

        if not click.confirm('确定要卸载 用户级 Clash 环境吗？这将删除所有配置文件'):
            click.echo("[INFO] 已取消卸载")
            return

        initializer = ClashInitializer(mode='uninstall', system_mode=False, force=True)
        initializer.run()

    except KeyboardInterrupt:
        click.echo("\n[ERROR] 操作被用户中断", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"[ERROR] 卸载失败: {e}", err=True)
        sys.exit(1)


    


def main():
    """主函数"""
    cli()


if __name__ == '__main__':
    main()
