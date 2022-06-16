"""Measure actual source-write to serving convergence for deterministic batches."""
import time
from . import workload, reconcile, runtime, metrics

def measure(count=100, rounds=3, start=10000):
    if type(rounds) is not int or not 1 <= rounds <= 20 or type(count) is not int or not 1 <= count <= 10000:
        raise ValueError('benchmark rounds or count outside bounds')
    samples=[]
    for iteration in range(rounds):
        begun=time.monotonic()
        workload.generate(count,seed=17+iteration,start=start+iteration*count)
        runtime.wait_for(lambda:reconcile.live()['equivalent'],timeout=120,interval=0.25)
        elapsed=time.monotonic()-begun
        samples.append({'records':count,'convergence_seconds':elapsed,'records_per_second':metrics.throughput(count,elapsed)})
    durations=[s['convergence_seconds'] for s in samples]
    return {'scope':'synthetic local single-partition pipeline; includes source write and polling overhead',
            'samples':samples,'p50_batch_seconds':metrics.percentile(durations,0.5),'p95_batch_seconds':metrics.percentile(durations,0.95),
            'reconciliation':reconcile.live()}
