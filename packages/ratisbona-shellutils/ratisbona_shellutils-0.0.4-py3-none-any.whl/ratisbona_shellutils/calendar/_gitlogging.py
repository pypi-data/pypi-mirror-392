from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from git import Repo

from ratisbona_utils.monads import Maybe, Just, Nothing


def find_git_root(starting_path: Path=Path(".")) -> Maybe[Path]:
    """
    Searches up the directory tree from the starting path to find the Git repository root.

    Args:
        starting_path (str): The directory to start searching from.

    Returns:
        str | None: The path to the Git repository root if found, otherwise None.
    """
    path = starting_path.resolve()

    for parent in [path] + list(path.parents):  # Walk up the tree
        if (parent / ".git").is_dir():  # Check if .git folder exists
            return Just(parent)

    return Nothing  # No Git repository found

@dataclass(frozen=True)
class LogEntry:
    commit_hash: str
    author: str
    the_datetime: datetime
    message: str



def get_git_log(repo_path:Path, max_entries=100) -> list[LogEntry]:
    """
    Reads the log entries from a Git repository.

    Args:
        repo_path (str): Path to the Git repository.
        max_entries (int): Maximum number of log entries to fetch.

    Returns:
        list[dict]: A list of log entries with details about commits.
    """

    repo = Repo(repo_path)
    if repo.bare:
        raise ValueError("Cannot read log from a bare repository.")

    log_entries = []
    for commit in repo.iter_commits(max_count=max_entries):
        log_entries.append(LogEntry(
            commit_hash=commit.hexsha,
            author=commit.author.name,
            the_datetime=commit.committed_datetime,
            message=commit.message.strip(),
        ))

    return log_entries


if __name__ == "__main__":
    # Specify the path to your Git repository
    maybe_repository_path = find_git_root()

    # Fetch the log entries
    logs = maybe_repository_path.bind(get_git_log).default_or_throw([])

    # Print the log entries
    for log in logs:
        print(f"Commit: {log.commit_hash}")
        print(f"Author: {log.author}")
        print(f"Date: {log.the_datetime}")
        print(f"Message: {log.message}")
        print("-" * 40)
