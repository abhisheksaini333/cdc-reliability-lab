"""Start the dedicated lab and wait for real service readiness."""
from . import runtime, pipeline

def start():
    from .config import load_env
    load_env(runtime.ROOT / '.env')
    runtime.compose('up','-d',timeout=180)
    runtime.wait_for(lambda: runtime.postgres('SELECT 1;').strip() == '1')
    runtime.wait_for(lambda: runtime.http_json('http://127.0.0.1:4703/').get('version'))
    runtime.wait_for(lambda: runtime.http_json('http://127.0.0.1:4704/overview').get('taskmanagers',0) >= 1)
    runtime.wait_for(lambda: runtime.clickhouse('SELECT 1').strip() == '1')
    for topic in ('lab.public.readings','lab.curated','lab.quarantine','__debezium-heartbeat.lab'):
        runtime.create_topic(topic)
    runtime.register_connector()
    runtime.wait_for(lambda: connector_ready())
    pipeline.initialize_serving()
    return pipeline.submit()

def connector_ready():
    status = runtime.http_json('http://127.0.0.1:4703/connectors/lab-source/status')
    return status.get('connector',{}).get('state') == 'RUNNING' and bool(status.get('tasks')) and all(t.get('state') == 'RUNNING' for t in status['tasks'])
