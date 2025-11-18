from __future__ import annotations

import asyncio
from enum import Enum, auto
from pathlib import Path

import aiohttp

from kimi_cli.share import get_share_dir
from kimi_cli.ui.shell.console import console
from kimi_cli.utils.aiohttp import new_client_session
from kimi_cli.utils.logging import logger

PYPI_URL = "https://pypi.org/pypi/cimi/json"


class UpdateResult(Enum):
    UPDATE_AVAILABLE = auto()
    UP_TO_DATE = auto()
    FAILED = auto()


LATEST_VERSION_FILE = get_share_dir() / "latest_version.txt"


def semver_tuple(version: str) -> tuple[int, int, int]:
    v = version.strip()
    if v.startswith("v"):
        v = v[1:]
    v = v.split("-")[0].split("+")[0]
    
    import re
    
    match = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?", v)
    if not match:
        return (0, 0, 0)
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3) or 0)
    return (major, minor, patch)


async def _get_latest_version(session: aiohttp.ClientSession) -> str | None:
    try:
        async with session.get(PYPI_URL) as resp:
            if resp.status == 200:
                data = await resp.json()
                version = data.get("info", {}).get("version")
                if version:
                    logger.debug("Latest version from PyPI: {version}", version=version)
                    return version
    except aiohttp.ClientError:
        logger.exception("Failed to get latest version from PyPI:")
    
    return None


async def do_update(*, print: bool = True, check_only: bool = False) -> UpdateResult:
    from kimi_cli.constant import VERSION as current_version

    def _print(message: str) -> None:
        if print:
            console.print(message)

    async with new_client_session() as session:
        logger.info("Checking for updates...")
        _print("Checking for updates...")
        
        latest_version = await _get_latest_version(session)
        if not latest_version:
            _print("[red]Failed to check for updates.[/red]")
            return UpdateResult.FAILED

        logger.debug("Latest version: {latest_version}", latest_version=latest_version)
        LATEST_VERSION_FILE.write_text(latest_version, encoding="utf-8")

        cur_t = semver_tuple(current_version)
        lat_t = semver_tuple(latest_version)

        if cur_t >= lat_t:
            logger.debug("Already up to date: {current_version}", current_version=current_version)
            _print("[green]Already up to date.[/green]")
            return UpdateResult.UP_TO_DATE

        logger.info(
            "Update available: current={current_version}, latest={latest_version}",
            current_version=current_version,
            latest_version=latest_version,
        )
        
        _print(f"[yellow]Update available: {latest_version}[/yellow]")
        return UpdateResult.UPDATE_AVAILABLE
