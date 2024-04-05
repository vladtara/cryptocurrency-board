import os
import subprocess
import pendulum
from git import Repo
from dotenv import load_dotenv


GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_EMAIL = os.getenv("GITHUB_EMAIL")
#load_dotenv()

def clone_and_run():
    repo_path = "/tmp/update"
    if os.path.exists(repo_path):
        repo = Repo(repo_path)
        origin = repo.remote("origin")
        origin.fetch()
    else:
        repo = Repo.clone_from(GITHUB_REPO_URL,repo_path)

    os.chdir(repo_path)
    subprocess.call(["python", "main.py"])

    with repo.config_writer() as git_config:
        git_config.set_value("user", "name", GITHUB_USERNAME)
        git_config.set_value("user", "email", GITHUB_EMAIL)

    repo.index.add(["README.md","data/","img/"])
    repo.index.commit(f"Duty Updates {pendulum.now().to_date_string()}")
    origin = repo.remote("origin")
    origin.push()

if __name__ == "__main__":
    clone_and_run()
