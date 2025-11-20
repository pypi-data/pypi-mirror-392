# lb_rr_lc.py (pseudo single-process backends as counters)
backends=[{"id":1,"conns":0},{"id":2,"conns":0},{"id":3,"conns":0}]
rr_index=0
def choose_rr():
    global rr_index
    sel=backends[rr_index % len(backends)]; rr_index+=1; return sel
def choose_lc():
    return min(backends, key=lambda b:b["conns"])
# simulate 6 requests
for i in range(6):
    s=choose_rr(); s["conns"]+=1; print("RR ->", s["id"])
for i in range(6):
    s=choose_lc(); s["conns"]+=1; print("LC ->", s["id"])
