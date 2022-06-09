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

if __name__ == '__main__':
    check('initial_snapshot',snapshot)
    check('insert_update_delete',mutations)
    check('invalid_latest_and_repair',quarantine)
    folder=r.ROOT/'artifacts';folder.mkdir(exist_ok=True)
    (folder/'integration.json').write_text(json.dumps(RESULTS,indent=2)+'\n')
