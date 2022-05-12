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
    sub.add_parser("schema")
    sub.add_parser("metrics")
    sub.add_parser("savepoint")
    export = sub.add_parser("export")
    export.add_argument("topic")
    export.add_argument("output")
    replay = sub.add_parser("replay")
    replay.add_argument("archive")
    replay.add_argument("target")
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
    elif args.action == "schema":
        from .schema import preflight
        print(json.dumps(preflight()))
    elif args.action == "metrics":
        from .metrics import live_quality
        print(json.dumps(live_quality()))
    elif args.action == "savepoint":
        from .operations import savepoint
        print(json.dumps({"savepoint":savepoint()}))
    elif args.action == "export":
        from .replay import export_topic, write_bundle
        data = export_topic(args.topic)
        write_bundle(args.output,data)
        print(json.dumps({"records":data["record_count"],"sha256":data["sha256"]}))
    elif args.action == "replay":
        from .replay import read_bundle,publish
        print(json.dumps({"published":publish(read_bundle(args.archive),args.target)}))
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
