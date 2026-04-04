import logging
import subprocess
import sys
from datetime import date
from os import getenv
from pathlib import Path

REPO_PATH = Path("/tmp/update")


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    logger.addHandler(handler)


def _run(args: list[str], cwd: Path | None = None) -> None:
    subprocess.run(args, check=True, cwd=cwd)


def clone_or_pull(repo_url: str, repo_path: Path) -> None:
    if repo_path.exists():
        logger.info("Pulling repository updates.")
        _run(["git", "-C", str(repo_path), "pull"], cwd=repo_path)
        return

    logger.info("Cloning repository.")
    _run(["git", "clone", repo_url, str(repo_path)])


def configure_git(repo_path: Path, username: str, email: str) -> None:
    _run(["git", "config", "user.name", username], cwd=repo_path)
    _run(["git", "config", "user.email", email], cwd=repo_path)


def run_main(repo_path: Path) -> None:
    _run([sys.executable, "main.py"], cwd=repo_path)


def commit_and_push(repo_path: Path) -> None:
    _run(["git", "add", "README.md", "data", "img"], cwd=repo_path)
    _run(
        ["git", "commit", "-m", f"Duty Updates {date.today().isoformat()}"],
        cwd=repo_path,
    )
    _run(["git", "push"], cwd=repo_path)


def main() -> None:
    repo_url = getenv("GITHUB_REPO_URL")
    username = getenv("GITHUB_USERNAME")
    email = getenv("GITHUB_EMAIL")

    if not repo_url or not username or not email:
        logger.error("Missing required environment variables.")
        raise SystemExit(1)

    try:
        clone_or_pull(repo_url, REPO_PATH)
        configure_git(REPO_PATH, username, email)
        run_main(REPO_PATH)
        commit_and_push(REPO_PATH)
    except subprocess.CalledProcessError:
        logger.exception("Command execution failed.")
        raise SystemExit(1) from None


if __name__ == "__main__":
    logger.info("Start.")
    try:
        main()
    finally:
        logger.info("Stop.")
