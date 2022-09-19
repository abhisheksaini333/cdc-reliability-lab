"""Exercise the actual running CDC stack. Run from the repository root."""
import json, pathlib, sys, time
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from cdc_lab import runtime as r, reconcile, workload, operations, replay, metrics

RESULTS = []
def check(name, action):
    start = time.monotonic()
    try:
        result = action()
    except Exception as exc:
        RESULTS.append({'scenario':name,'passed':False,'seconds':round(time.monotonic()-start,3),'error':type(exc).__name__})
        from cdc_lab.evidence import record_run
        record_run(r.ROOT/'artifacts',RESULTS)
        raise
    RESULTS.append({'scenario':name,'passed':True,'seconds':round(time.monotonic()-start,3),'result':result})
    print(json.dumps(RESULTS[-1]),flush=True)
    return result

def converge():
    r.wait_for(lambda: reconcile.live()['equivalent'],timeout=120,interval=1)
    return reconcile.live()

def snapshot():
    result=converge()
    if result['actual_count'] < 3 or int(r.clickhouse("SELECT uniqExact(event_id) FROM lab.raw_events WHERE op='r'"))<3: raise AssertionError('initial fixture snapshot missing')
    return result

def mutations():
    workload.generate(12,seed=31,start=100)
    r.postgres(workload.update_sql(100,42.25))
    r.postgres(workload.delete_sql([101,102]))
    return converge()

def quarantine():
    r.postgres(workload.update_sql(100,999))
    converge()
    r.wait_for(lambda: int(r.clickhouse("SELECT count() FROM lab.quarantine_events WHERE id=100 AND quality='invalid_value'"))>0)
    r.postgres(workload.update_sql(100,22.5))
    return converge()

def replay_twice():
    archive=replay.export_topic('lab.curated')
    before=reconcile.digest(reconcile.served_rows())
    count=int(r.clickhouse('SELECT count() FROM lab.raw_events'))
    delivered=replay.publish(archive,'lab.curated')+replay.publish(archive,'lab.curated')
    r.wait_for(lambda:int(r.clickhouse('SELECT count() FROM lab.raw_events'))>=count+delivered)
    if reconcile.digest(reconcile.served_rows())!=before:raise AssertionError('replay changed current state')
    return {'replayed_deliveries':delivered,'state_digest':before,'reconciliation':converge()}

def worker_restart():
    job=operations.active_job();operations.wait_checkpoint(job)
    before=operations.checkpoint_status(job)['counts']['completed']
    operations.restart('taskmanager')
    r.postgres(workload.update_sql(103,34.5))
    result=converge()
    r.wait_for(lambda:operations.checkpoint_status(job)['counts']['completed']>before,timeout=150)
    return {'job':job,'checkpoint_before':before,'checkpoint_after':operations.checkpoint_status(job)['counts']['completed'],'reconciliation':result}

def connector_restart():
    r.compose('stop','connect')
    r.postgres(workload.update_sql(104,35.5))
    r.compose('start','connect')
    from cdc_lab.startup import connector_ready
    r.wait_for(connector_ready)
    return converge()

def serving_restart():
    r.compose('stop','clickhouse')
    r.postgres(workload.update_sql(105,36.5))
    r.compose('start','clickhouse')
    r.wait_for(lambda:r.clickhouse('SELECT 1').strip()=='1')
    return converge()

def savepoint_restore():
    from cdc_lab import pipeline
    old=operations.active_job()
    location=operations.savepoint(cancel=True)
    r.wait_for(lambda:r.http_json('http://127.0.0.1:4704/jobs/'+old)['state']=='CANCELED')
    r.postgres(workload.update_sql(106,37.5))
    pipeline.submit(restore=location)
    r.wait_for(lambda:operations.active_job(),timeout=120)
    result=converge()
    operations.wait_checkpoint()
    status=operations.checkpoint_status()
    if not status.get('latest',{}).get('restored'):raise AssertionError('restore evidence missing')
    return {'savepoint':location,'restored':status['latest']['restored'],'reconciliation':result}

def schema_evolution():
    from cdc_lab import schema, contracts
    r.postgres((r.ROOT/'migrations/001-add-note.sql').read_text())
    schema.preflight()
    r.postgres("UPDATE readings SET note='additive evolution',value=38.5 WHERE id=107;")
    converge()
    sql="BEGIN; ALTER TABLE readings ALTER COLUMN value TYPE TEXT USING value::text; SELECT json_agg(t) FROM (SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='public' AND table_name='readings') t; ROLLBACK;"
    output=r.postgres(sql)
    rows=json.loads(next(line for line in output.splitlines() if line.startswith('[')))
    errors=contracts.validate_schema(schema.normalize_types(rows))
    if 'incompatible:value' not in errors:raise AssertionError('incompatible source type accepted')
    schema.preflight()
    return {'rejected':errors,'reconciliation':converge()}

if __name__ == '__main__':
    check('initial_snapshot',snapshot)
    check('insert_update_delete',mutations)
    check('invalid_latest_and_repair',quarantine)
    check('repeated_bounded_replay',replay_twice)
    check('taskmanager_checkpoint_recovery',worker_restart)
    check('connector_outage_recovery',connector_restart)
    check('serving_outage_recovery',serving_restart)
    check('savepoint_restore',savepoint_restore)
    check('schema_evolution_gate',schema_evolution)
    folder=r.ROOT/'artifacts';folder.mkdir(exist_ok=True)
    (folder/'integration.json').write_text(json.dumps(RESULTS,indent=2)+'\n')
    from cdc_lab.evidence import record_run
    record_run(folder,RESULTS)
