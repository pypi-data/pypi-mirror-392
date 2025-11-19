# kv_store.py  (single process sim of three replicas)
import threading, time
replicas=[{}, {}, {}]
def update(replica_idx,k,v):
    replicas[replica_idx][k]=v
def propagate(src,target):
    replicas[target].update(replicas[src])
# demonstration
update(0,"x",1)
print("After update at 0:",replicas)
time.sleep(1)
propagate(0,1); print("propagated 0->1:",replicas)
time.sleep(1)
propagate(1,2); print("propagated 1->2:",replicas)
# Strong consistency would require synchronous replication to all before ack.
