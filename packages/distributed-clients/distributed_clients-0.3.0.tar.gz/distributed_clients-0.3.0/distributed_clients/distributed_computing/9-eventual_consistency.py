import time

# Three replicas
replicas = {
    "R1": {"x": 10},
    "R2": {"x": 10},
    "R3": {"x": 10}
}

def print_replicas():
    for r, data in replicas.items():
        print(f"{r}: {data}")
    print("-" * 40)

# STRONG CONSISTENCY
def strong_consistency_update(new_value):
    # Update all replicas at the same instant
    for r in replicas:
        replicas[r]["x"] = new_value
    print("After Strong Consistency Update (all replicas updated together):")
    print_replicas()

# EVENTUAL CONSISTENCY
def eventual_consistency_update(new_value):
    # Update only replica R1 first
    replicas["R1"]["x"] = new_value
    print("After updating ONLY R1 (inconsistent state):")
    print_replicas()

    # Simulate network delay
    print("Propagating update to other replicas after delay...")
    time.sleep(2)
    replicas["R2"]["x"] = new_value
    replicas["R3"]["x"] = new_value
    print("After propagation (Eventual Consistency achieved):")
    print_replicas()

print("\nINITIAL STATE")
for r in replicas:
    print(f"{r}: {replicas[r]}")
print("-" * 40)

print("\nSTRONG CONSISTENCY")
strong_consistency_update(50)

print("\nEVENTUAL CONSISTENCY DEMO")
eventual_consistency_update(99)
