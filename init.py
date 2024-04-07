import os
import subprocess
import pendulum
from git import Repo
import logging

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()
    ]
)


GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_EMAIL = os.getenv("GITHUB_EMAIL")

def clone_and_run():
    
    repo_path = "/tmp/update"
    if os.path.exists(repo_path):
        logging.info('Pull from  repo.')
        repo = Repo(repo_path)
        origin = repo.remote("origin")
        origin.pull()
    else:
        logging.info('Cloning the repo.')
        repo = Repo.clone_from(GITHUB_REPO_URL,repo_path)
    logging.info('Changing dir.')
    os.chdir(repo_path)

    logging.info('Running the main.py.')
    subprocess.call(["python", "main.py"])

    logging.info('Set git config.')
    with repo.config_writer() as git_config:
        git_config.set_value("user", "name", GITHUB_USERNAME)
        git_config.set_value("user", "email", GITHUB_EMAIL)
    
    logging.info('Add new files.')
    repo.index.add(["README.md","data/*","img/*"])
    logging.info('Commit new files.')
    repo.index.commit(f"Duty Updates {pendulum.now().to_date_string()}")
    origin = repo.remote("origin")
    origin.push()
    logging.info('Git Pushed.')

if __name__ == "__main__":
    logging.info('Start.')
    clone_and_run()
    logging.info('Stop.')
