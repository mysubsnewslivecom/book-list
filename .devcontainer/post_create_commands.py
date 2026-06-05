#!/usr/bin/env python3

import asyncio
import logging
import os
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

# ----------------------------
# Logging
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

logger = logging.getLogger("bootstrap")


# ----------------------------
# Models
# ----------------------------
@dataclass
class Package:
    name: str
    url: str


PACKAGES = [
    Package("opencode", "https://opencode.ai/install"),
    Package(
        "nvm",
        "https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh",
    ),
]


# ----------------------------
# Downloader
# ----------------------------
class Downloader:
    @staticmethod
    def _download_sync(url: str) -> str:
        with urllib.request.urlopen(url) as response:
            data = response.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".sh") as f:
            f.write(data)
            path = f.name

        os.chmod(path, 0o755)
        return path

    async def download(self, name: str, url: str) -> tuple[str, str]:
        logger.info("[%s] downloading", name)
        path = await asyncio.to_thread(self._download_sync, url)
        logger.info("[%s] downloaded -> %s", name, path)
        return name, path


# ----------------------------
# Installer
# ----------------------------
class Installer:
    def __init__(self):
        self.log = logging.getLogger("installer")

    async def run(self, name: str, path: str) -> int:
        self.log.info("[%s] installing", name)

        process = await asyncio.create_subprocess_exec(
            "bash",
            path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if stdout:
            self.log.info("[%s] stdout:\n%s", name, stdout.decode())

        if stderr:
            self.log.warning("[%s] stderr:\n%s", name, stderr.decode())

        self.log.info("[%s] exit code: %d", name, process.returncode)
        return process.returncode


# ----------------------------
# Shell runner (uv, nvm)
# ----------------------------
class ShellRunner:
    def __init__(self):
        self.log = logging.getLogger("shell")

    async def run(self, cmd: str) -> int:
        self.log.info("running: %s", cmd)

        process = await asyncio.create_subprocess_exec(
            "bash",
            "-lc",
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if stdout:
            self.log.info(stdout.decode())

        if stderr:
            self.log.warning(stderr.decode())

        self.log.info("exit code: %d", process.returncode)
        return process.returncode


# ----------------------------
# Bootstrap orchestrator
# ----------------------------
class Bootstrapper:
    def __init__(self, packages: list[Package]):
        self.packages = packages
        self.downloader = Downloader()
        self.installer = Installer()
        self.shell = ShellRunner()
        self.temp_files: list[str] = []

    async def download_all(self) -> list[tuple[str, str]]:
        results = await asyncio.gather(*(self.downloader.download(p.name, p.url) for p in self.packages))

        for _, path in results:
            self.temp_files.append(path)

        return results

    async def install_all(self, downloads: list[tuple[str, str]]) -> bool:
        for name, path in downloads:
            code = await self.installer.run(name, path)
            if code != 0:
                logger.error("[%s] install failed", name)
                return False
        return True

    async def run_uv_sync(self) -> bool:
        return (await self.shell.run("uv sync --all-packages")) == 0

    async def run_nvm(self) -> bool:
        cmd = """
        export NVM_DIR="$HOME/.nvm"

        if [ -s "$NVM_DIR/nvm.sh" ]; then
            . "$NVM_DIR/nvm.sh"
        else
            echo "nvm not found"
            exit 1
        fi

        nvm install --lts
        """

        return (await self.shell.run(cmd)) == 0

    async def opencode_ollama_config(self) -> bool:
        ollama_config = """{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://ollama:11434/v1"
      },
      "models": {
        "gemma4-agent:26b": {
          "name": "gemma4-agent:26b"
        },
        "deepseekr1-agent:14b": {
          "name": "deepseekr1-agent:14b"
        }
      }
    }
  }
}
        """
        user_config = Path(os.path.expanduser("~")) / ".config/opencode/config.json"
        logger.info("writing opencode config to %s", user_config)
        try:
            with open(file=user_config, mode="w", encoding="utf-8") as f:
                f.write(ollama_config)
        except FileNotFoundError:
            logger.exception("failed to write opencode config file")
            return False

        return True

    def cleanup(self):
        for path in self.temp_files:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                logger.exception("cleanup failed for %s", path)

    async def run(self):
        try:
            downloads = await self.download_all()

            if not await self.install_all(downloads):
                return

            if not await self.run_uv_sync():
                logger.error("uv sync failed")
                return

            if not await self.run_nvm():
                logger.error("nvm install failed")
                return

            if not await self.opencode_ollama_config():
                logger.error("ollama config failed")
                return

            logger.info("bootstrap completed successfully")

        finally:
            self.cleanup()


# ----------------------------
# Entry point
# ----------------------------
async def main():
    bootstrapper = Bootstrapper(PACKAGES)
    await bootstrapper.run()


if __name__ == "__main__":
    asyncio.run(main())
