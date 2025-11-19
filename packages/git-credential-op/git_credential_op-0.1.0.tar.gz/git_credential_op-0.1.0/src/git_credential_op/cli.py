import json
import logging
import logging.handlers
import os
import subprocess
import sys

import click

if "CI_NAME" in os.environ:
    handler = logging.StreamHandler(sys.stdout)
else:
    home = os.getenv("HOME")
    handler = logging.handlers.RotatingFileHandler(
        f"{home}/.logs/git-credential-op.log", backupCount=1, maxBytes=1024 * 1024
    )

logging.basicConfig(
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    level=logging.INFO,
    handlers=[handler],
)

logger = logging.getLogger()


def read_git_input() -> dict[str, str]:
    rval = {}
    for line in sys.stdin:
        key, val = line.strip().split("=", 1)
        rval[key] = val
    return rval


def run_op(*args) -> dict | list:
    logger.debug(f"Running op {' '.join(args)}")
    return json.loads(subprocess.check_output(("op",) + args).decode())


@click.group()
@click.version_option()
def cli():
    "A simple `git credential` helper for 1password CLI (op)"


@cli.command(name="get")
def get_op_entry():
    "Get an entry from the op store"
    git_input = read_git_input()
    logger.debug(f"Input: {git_input}")
    item_list = run_op(
        "item",
        "list",
        "--categories",
        "login",
        "--format",
        "json",
        "--tags",
        "git-credential",
    )

    item_id = None
    logger.debug(f"Searching for items for {git_input['protocol']}://{git_input['host']}")
    for item in item_list:
        for url in item["urls"]:
            logger.debug(f"URL: {url['href']}")
            if url["href"].startswith(f"{git_input['protocol']}://{git_input['host']}"):
                logger.debug(f"Found item id {item['id']}")
                item_id = item["id"]
                break

    if not item_id:
        logger.error("Item not found!")
        sys.exit(1)

    fields = run_op(
        "item",
        "get",
        "--format",
        "json",
        "--reveal",
        "--fields",
        "username,password",
        item_id,
    )

    username = None
    password = None
    for field in fields:
        if field["id"] == "username":
            username = field["value"]
        elif field["id"] == "password":
            password = field["value"]

    if not username or not password:
        logger.error("Missing username/password")
        sys.exit(1)

    print(f"username={username}")
    print(f"password={password}")
    print("")


@cli.command(name="store")
def store_op_entry():
    "Save an entry to the op store (unimplemented)"
    logger.debug("store_op_entry called")


@cli.command(name="erase")
def untag_op_entry():
    "Erase an entry from the op store (unimplemented)"
    logger.debug("untag_op_entry called")


if __name__ == "__main__":
    cli()
