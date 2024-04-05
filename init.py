from git import Repo

# Clone the remote repository
repo_url = "https://github.com/username/repository.git"
local_path = "/path/to/local/repository"
Repo.clone_from(repo_url, local_path)

# Add a simple text file
file_path = "/path/to/local/repository/file.txt"
with open(file_path, "w") as file:
    file.write("Hello, world!")

# Commit the changes
repo = Repo(local_path)
repo.index.add([file_path])
repo.index.commit("Added a simple text file")

# Push the changes back to the remote repository
origin = repo.remote("origin")
origin.push()