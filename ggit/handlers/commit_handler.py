import datetime
import logging
from io import TextIOWrapper
from logging import Logger
import os
from pathlib import Path
from pprint import pprint
from typing import Dict, List
from ggit.entities.user import User

from ggit.managers import ConfigManager, StashManager, DifferenceManager
from ggit.entities import Tree, Blob, Commit
from ggit.utils import Folder
from ggit.database import CommitRepository


def build_tree(folder: Dict[str, Dict], current_root: Path) -> Tree:
    """
    Build a tree object given a :class:"ggit.utils.Folder" internal dictionary
    
    Parameters
    ----------
    folder : Dict[str, Dict]
        The folder dictionary
    current_root : Path
        The current root path

    Returns
    -------
    Tree
        The tree object
    """

    tree = Tree()

    for i in folder:
        if folder[i] is None:
            blob_path = current_root / i
            mode = "100644"
            if os.access(blob_path, os.X_OK):
                mode = "100755"
            if blob_path.is_symlink():
                mode = "120000"
            tree.append_item(Blob(blob_path.read_bytes()), i, mode)
        else:
            tree.append_item(build_tree(folder[i], current_root / i), i, "040000")

    return tree


def commit_handler(
    args: Dict[str, str], logger: Logger = logging.getLogger("message")
) -> None:
    """This handler"""

    root = Path(ConfigManager()["repository.path"])

    stash_manager = StashManager(root)

    if len(stash_manager.stashed_files) == 0:
        logger.info("Nothing to commit")
        return

    if args["message_file"] is not None:
        message = args["message_file"].read()
    else:
        message = args["message"]

    conf_manager = ConfigManager()

    tree = build_tree(
        Folder(root, whitelist=list(stash_manager.stashed_files.keys())).folder, root
    )

    if args["author"] is not None:
        author = User(args["author"].split(",")[0], args["author"].split(",")[1])
    else:
        author = User(conf_manager["user.name"], conf_manager["user.email"])
    committer = User(conf_manager["user.name"], conf_manager["user.email"])

    commit_repo = CommitRepository()

    if conf_manager["HEAD"] == "None":
        parent = None
    else:
        parent = commit_repo.get_commit(conf_manager["HEAD"])

    commit = Commit(
        tree=tree,
        parent=parent,
        date_time=datetime.datetime.now(),
        author=author,
        committer=committer,
        message=message,
    )

    commit_repo.add_commit(commit)

    commit_repo.data_source.close()

    conf_manager["HEAD"] = commit.hash

    stash_manager.clear_stash()
    diff_manager = DifferenceManager(root)
    diff_manager.update_current_state()
