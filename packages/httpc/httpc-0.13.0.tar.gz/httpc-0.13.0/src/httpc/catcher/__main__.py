import sys

from httpc._base import logger
from httpc.catcher._db import TransactionDatabase


def main():
    if len(sys.argv) < 3:
        return 1
    elif sys.argv[1] == "migrate":
        with TransactionDatabase(sys.argv[2], "transactions", migrate_old_database=True):
            pass
        logger.warning(f"Database {sys.argv[2]!r} has been migrated.")


if __name__ == "__main__":
    sys.exit(main())
