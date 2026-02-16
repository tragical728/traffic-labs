import sys
import os
import subprocess

if len(sys.argv) < 2:
    print("Usage: python deploy.py <name>")
    sys.exit(1)

name = sys.argv[1]

print(f"Deploying: {name}")

os.makedirs(f"sites/{name}", exist_ok=True)
os.system(f"cp -r landing/* sites/{name}/")

with open("docker-compose.yml", "r") as f:
    compose = f.read()

if name not in compose:
    service = f"""  {name}:
    build: ./landing
    networks:
      - traffic-net

"""
    compose = compose.replace("  nginx:", service + "  nginx:")
    
    if "depends_on:" in compose:
        compose = compose.replace(
            "depends_on:",
            f"depends_on:\n      - {name}"
        )
    
    with open("docker-compose.yml", "w") as f:
        f.write(compose)
    print(f"Added {name} to docker-compose.yml")

with open("nginx.conf", "r") as f:
    nginx = f.read()

if f"server {name}:80" not in nginx:
    nginx = nginx.replace(
        "upstream backend {",
        f"upstream backend {{\n        server {name}:80;"
    )
    with open("nginx.conf", "w") as f:
        f.write(nginx)
    print(f"Added {name} to nginx.conf")

print("Restarting...")
subprocess.run(["docker-compose", "up", "-d", "--build"])

print("Done")
subprocess.run(["docker-compose", "ps"])