"""Exercise the actual running CDC stack. Run from the repository root."""
import json, pathlib, sys, time
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from cdc_lab import runtime as r, reconcile, workload, operations, replay, metrics

RESULTS = []
def check(name, action):
    start = time.monotonic()
    result = action()
    RESULTS.append({'scenario':name,'passed':True,'seconds':round(time.monotonic()-start,3),'result':result})
    print(json.dumps(RESULTS[-1]),flush=True)
    return result

def converge():
    r.wait_for(lambda: reconcile.live()['equivalent'],timeout=120,interval=1)
    return reconcile.live()

def snapshot():
    result=converge()
    if result['actual_count'] < 3: raise AssertionError('initial fixture snapshot missing')
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

if __name__ == '__main__':
    check('initial_snapshot',snapshot)
    check('insert_update_delete',mutations)
    check('invalid_latest_and_repair',quarantine)
    check('repeated_bounded_replay',replay_twice)
    check('taskmanager_checkpoint_recovery',worker_restart)
    check('connector_outage_recovery',connector_restart)
    check('serving_outage_recovery',serving_restart)
    check('savepoint_restore',savepoint_restore)
    folder=r.ROOT/'artifacts';folder.mkdir(exist_ok=True)
    (folder/'integration.json').write_text(json.dumps(RESULTS,indent=2)+'\n')
