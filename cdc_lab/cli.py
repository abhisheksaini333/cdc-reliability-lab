"""Local CDC operator entry point."""
import argparse, json
from . import runtime

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("init-env")
    sub.add_parser("topics")
    sub.add_parser("register")
    sub.add_parser("submit")
    sub.add_parser("serving")
    sub.add_parser("reconcile")
    load = sub.add_parser("generate")
    load.add_argument("--count",type=int,default=100)
    load.add_argument("--seed",type=int,default=17)
    load.add_argument("--start",type=int,default=1000)
    args = parser.parse_args(argv)
    if args.action == "init-env":
        from .config import create_env
        create_env(runtime.ROOT / ".env")
        print("Created private local credentials")
    elif args.action == "topics":
        for topic in ("lab.public.readings", "lab.curated", "lab.quarantine", "__debezium-heartbeat.lab"):
            runtime.create_topic(topic)
    elif args.action == "reconcile":
        from .reconcile import live
        result = live()
        print(json.dumps(result))
        if not result["equivalent"]: raise SystemExit(1)
    elif args.action == "generate":
        from .workload import generate
        print(json.dumps({"mutations":generate(args.count,args.seed,args.start)}))
    elif args.action == "submit":
        from .pipeline import submit
        print(submit())
    elif args.action == "serving":
        from .pipeline import initialize_serving
        initialize_serving()
    elif args.action == "register":
        result = runtime.register_connector()
        print(json.dumps({"name": result.get("name", "lab-source"), "registered": True}))

if __name__ == "__main__":
    main()
