#!/usr/bin/env python3
"""CI : demarre un vrai serveur Fabric 1.21.1 avec Cobblemon 1.8.4, Mega Showdown (et ses dependances) et le mod,
puis verifie le chargement : auto-test du mod (-Dnormandy_fakemons.selftest=true), Deviljho et sa forme Mega,
la Deviljhonite et ses composants Mega Showdown, et les erreurs de chargement des donnees."""
import glob, json, os, queue, re, shutil, subprocess, sys, threading, time, urllib.request

OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "out")
SRV = os.path.abspath("run-server")
UA = {"User-Agent": "cobblepulse-fakemons-ci/1.0 (github actions)"}
props = dict(l.strip().split("=", 1) for l in open("gradle.properties") if "=" in l and not l.startswith("#"))
os.makedirs(OUT, exist_ok=True)


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def log(msg):
    print(msg, flush=True)
    with open(os.path.join(OUT, "server-steps.txt"), "a") as fh:
        fh.write(msg + "\n")


def versions(slug):
    return json.loads(get(f"https://api.modrinth.com/v2/project/{slug}/version"
                          "?loaders=%5B%22fabric%22%5D&game_versions=%5B%221.21.1%22%5D"))


os.makedirs(os.path.join(SRV, "mods"), exist_ok=True)
wanted = [("fabric-api", None), ("fabric-language-kotlin", None), ("cobblemon", "1.8.4"),
          ("cobblemon-mega-showdown", "1.8.4")]
done = set()
while wanted:
    slug, want = wanted.pop(0)
    if slug in done:
        continue
    done.add(slug)
    try:
        vs = versions(slug)
    except Exception as e:
        log(f"!! {slug}: {e}")
        continue
    pick = next((v for v in vs if want is None or want in v["version_number"]), vs[0] if vs else None)
    if not pick:
        log(f"!! pas de version pour {slug}")
        continue
    f = [f for f in pick["files"] if f["primary"]] or pick["files"]
    open(os.path.join(SRV, "mods", f[0]["filename"]), "wb").write(get(f[0]["url"]))
    log(f"mod {slug} {pick['version_number']} -> {f[0]['filename']}")
    for d in pick.get("dependencies", []):           # dependances requises (architectury, accessories, owo...)
        if d.get("dependency_type") == "required" and d.get("project_id"):
            try:
                dep = json.loads(get(f"https://api.modrinth.com/v2/project/{d['project_id']}"))["slug"]
                if dep not in done:
                    wanted.append((dep, None))
            except Exception as e:
                log(f"!! dep {d}: {e}")
for j in [j for j in glob.glob("build/libs/*.jar") if not j.endswith("-sources.jar")]:
    shutil.copy(j, os.path.join(SRV, "mods"))
    log("mod normandy_fakemons " + j)

installer = json.loads(get("https://meta.fabricmc.net/v2/versions/installer"))[0]["version"]
loader = props.get("loader_version")
open(os.path.join(SRV, "server.jar"), "wb").write(
    get(f"https://meta.fabricmc.net/v2/versions/loader/1.21.1/{loader}/{installer}/server/jar"))
open(os.path.join(SRV, "eula.txt"), "w").write("eula=true\n")
open(os.path.join(SRV, "server.properties"), "w").write(
    "online-mode=false\nview-distance=4\nsimulation-distance=4\nspawn-protection=0\nmax-tick-time=-1\n"
    "level-seed=normandy\nsync-chunk-writes=false\n")

COMMANDS = [
    "sleep 5",
    "forceload add 0 0",
    "sleep 3",
    "summon minecraft:item 0 120 0 {Item:{id:\"normandy_fakemons:deviljhonite\",count:1},NoGravity:1b,PickupDelay:32767,Age:-32768}",
    "data get entity @e[type=minecraft:item,limit=1] Item",
    "spawnpokemonat 0 100 0 deviljho",
    "spawnpokemonat 4 100 0 deviljho mega_evolution=mega",
    "spawnpokemonat 8 100 0 guillopard",
    "sleep 3",
    "data get entity @e[type=cobblemon:pokemon,limit=3,sort=nearest] Pokemon.Species",
    "data get entity @e[type=cobblemon:pokemon,limit=3,sort=nearest] Pokemon.FormId",
    "reload",
    "sleep 8",
    "list",
]

proc = subprocess.Popen(["java", "-Xmx5G", "-Dnormandy_fakemons.selftest=true", "-jar", "server.jar", "nogui"], cwd=SRV,
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
lines = queue.Queue()
logf = open(os.path.join(OUT, "server.log"), "w")


def reader():
    for line in proc.stdout:
        logf.write(line)
        logf.flush()
        lines.put(line)
    lines.put(None)


threading.Thread(target=reader, daemon=True).start()


def wait_for(token, timeout):
    end = time.time() + timeout
    while time.time() < end:
        try:
            line = lines.get(timeout=1)
        except queue.Empty:
            continue
        if line is None:
            return False
        if token in line:
            return True
    return False


ok = wait_for("Done (", 1500)
log("server ready: %s" % ok)
if ok:
    for c in COMMANDS:
        if c.startswith("sleep "):
            time.sleep(float(c.split()[1]))
            continue
        log("> " + c)
        proc.stdin.write(c + "\n")
        proc.stdin.flush()
        time.sleep(2)
    time.sleep(5)
try:
    proc.stdin.write("stop\n")
    proc.stdin.flush()
except Exception:
    pass
try:
    proc.wait(timeout=180)
except subprocess.TimeoutExpired:
    proc.kill()
logf.close()

text = open(os.path.join(OUT, "server.log"), errors="replace").read().splitlines()
keys = re.compile(r"normandy|deviljho|fakemon|SELFTEST|guillopard|soufflecarnage|ragebrulante|wasteland", re.I)
bad = re.compile(r"\b(ERROR|WARN)\b|Exception|Couldn't|Failed|Unknown|Invalid|error", re.I)
with open(os.path.join(OUT, "server-summary.txt"), "w") as fh:
    for l in text:
        if keys.search(l) or ("mega_showdown" in l.lower() and bad.search(l)):
            fh.write(l + "\n")
with open(os.path.join(OUT, "server-errors.txt"), "w") as fh:
    for l in text:
        if bad.search(l) and ("ERROR" in l or "Exception" in l or "Couldn't" in l or "Failed" in l):
            fh.write(l + "\n")
for crash in glob.glob(os.path.join(SRV, "crash-reports", "*")):
    shutil.copy(crash, OUT)
summary = [l for l in text if "SELFTEST SUMMARY" in l]
log("selftest: " + (summary[-1] if summary else "ABSENT"))
log("exit code %s" % proc.returncode)
