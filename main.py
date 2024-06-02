import time
from backend.Endpoint import run_app
from frontend import CLI
from threading import Thread
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser("GenGame")
    parser.add_argument('--server',  help="Run only the flask server.", action='store_true')
    parser.add_argument('--cli',  help="Run only the CLI.", action='store_true')
    args = parser.parse_args()

    if args.server:
        run_app()
    elif not args.cli:
        Thread(target=run_app, daemon=True).start()
    if not args.server:
        time.sleep(1)
        CLI.start()
