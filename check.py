from pathlib import Path

for tenant in sorted(Path("data").iterdir()):
    for level in sorted(tenant.iterdir()):
        n = len(list(level.glob("*.txt")))
        print(tenant.name, level.name, n, "files")