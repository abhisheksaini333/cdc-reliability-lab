"""Local CDC operator entry point."""
import argparse, json
from . import runtime

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("init-env")
    sub.add_parser("topics")
    sub.add_parser("register")
    args = parser.parse_args(argv)
    if args.action == "init-env":
        from .config import create_env
        create_env(runtime.ROOT / ".env")
        print("Created private local credentials")
    elif args.action == "topics":
        for topic in ("lab.public.readings", "lab.curated", "lab.quarantine", "__debezium-heartbeat.lab"):
            runtime.create_topic(topic)
    elif args.action == "register":
        result = runtime.register_connector()
        print(json.dumps({"name": result.get("name", "lab-source"), "registered": True}))

if __name__ == "__main__":
    main()
