#!/usr/bin/env python3
"""CI (diagnostic) : extrait des references utiles des jars de Cobblemon et de Biomes O' Plenty dans out/refs :
presets d'apparition de Cobblemon, tags de blocs, code des positions d'apparition « grounded », et tout ce qui
concerne le bloc biomesoplenty:dried_salt."""
import glob, json, os, re, subprocess, sys, urllib.request, zipfile

OUT = os.path.join(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "out"), "refs")
os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "cobblepulse-fakemons-ci/1.0 (github actions)"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
        return r.read()


def write(name, text):
    open(os.path.join(OUT, name), "w").write(text)


cob = (glob.glob("run-server/mods/Cobblemon*.jar") + glob.glob("run-server/mods/cobblemon-fabric*.jar"))
cob = [c for c in cob if "mega" not in c.lower()]
rep = []
if cob:
    z = zipfile.ZipFile(cob[0])
    names = z.namelist()
    pres = [n for n in names if "spawn_detail_presets" in n and n.endswith(".json")]
    write("cobblemon-presets.txt", "\n\n".join(f"== {n}\n{z.read(n).decode()}" for n in sorted(pres)))
    tags = [n for n in names if "/tags/block/" in n and n.endswith(".json")]
    write("cobblemon-block-tags.txt", "\n\n".join(f"== {n}\n{z.read(n).decode()}" for n in sorted(tags)))
    cls = [n for n in names if n.endswith(".class") and re.search(r"spawning/(context|condition|detail|preset|influence)|Grounded|SpawnablePosition", n)]
    write("cobblemon-spawn-classes.txt", "\n".join(sorted(cls)))
    tmp = os.path.join(OUT, "cls")
    os.makedirs(tmp, exist_ok=True)
    dump = []
    for n in sorted(cls):
        if re.search(r"Grounded|SpawnablePositionResolver|PositionResolver|SpawningContextCalculator|ContextCalculator", n):
            p = os.path.join(tmp, n.replace("/", "_"))
            open(p, "wb").write(z.read(n))
            try:
                dump.append(f"== {n}\n" + subprocess.run(["javap", "-c", "-p", p], capture_output=True, text=True).stdout)
            except Exception as e:
                dump.append(f"== {n}: {e}")
    write("cobblemon-grounded-javap.txt", "\n".join(dump))
    rep.append(f"cobblemon jar {cob[0]}: {len(pres)} presets, {len(tags)} block tags, {len(cls)} spawn classes")
    # starters (3.10.2): the starter config classes, where Cobblemon loads them, and any starter data in the jar
    st = [n for n in names if n.endswith(".class") and re.search(r"(?i)starter", n)]
    sdump = [f"== classes\n" + "\n".join(sorted(st))]
    for n in sorted(st) + ["com/cobblemon/mod/common/Cobblemon.class"]:
        if n not in names:
            continue
        if n.endswith("Cobblemon.class") or re.search(r"config/starter/|StarterHandler|CobblemonStarterHandler", n):
            p = os.path.join(tmp, n.replace("/", "_"))
            open(p, "wb").write(z.read(n))
            out = subprocess.run(["javap", "-c", "-p", p], capture_output=True, text=True).stdout
            if n.endswith("Cobblemon.class"):            # only the starter parts of the big class
                keep, lines = [], out.splitlines()
                for i, l in enumerate(lines):
                    if re.search(r"(?i)starter", l):
                        keep += lines[max(0, i - 6):i + 6] + ["--"]
                out = "\n".join(keep)
            sdump.append(f"== {n}\n{out}")
    data = [n for n in names if re.search(r"(?i)starter", n) and not n.endswith(".class")]
    sdump.append("== data files\n" + "\n".join(data))
    for n in data[:10]:
        if n.endswith(".json"):
            sdump.append(f"== {n}\n" + z.read(n).decode("utf-8", "replace")[:6000])
    write("cobblemon-starters.txt", "\n\n".join(sdump))
    rep.append(f"starters: {len(st)} classes, {len(data)} data files")
try:
    vs = json.loads(get("https://api.modrinth.com/v2/project/biomes-o-plenty/version"
                        "?loaders=%5B%22fabric%22%5D&game_versions=%5B%221.21.1%22%5D"))
    f = [f for f in vs[0]["files"] if f["primary"]] or vs[0]["files"]
    data = get(f[0]["url"])
    p = os.path.join(OUT, "bop.jar")
    open(p, "wb").write(data)
    z = zipfile.ZipFile(p)
    hits = []
    for n in z.namelist():
        if n.endswith((".json", ".mcmeta")):
            t = z.read(n).decode("utf-8", "replace")
            if "dried_salt" in t or "dried_salt" in n:
                hits.append(f"== {n}\n{t[:4000]}")
    write("bop-dried_salt.txt", "\n\n".join(hits))
    # the block's class / properties: strings in the classes that mention dried_salt
    cl = []
    for n in z.namelist():
        if n.endswith(".class"):
            b = z.read(n)
            if b"dried_salt" in b:
                q = os.path.join(OUT, "bop_" + n.replace("/", "_"))
                open(q, "wb").write(b)
                out = subprocess.run(["javap", "-c", "-p", q], capture_output=True, text=True).stdout
                i = out.find("dried_salt")
                cl.append(f"== {n}\n{out[max(0, i - 3000):i + 3000]}")
    write("bop-dried_salt-classes.txt", "\n\n".join(cl))
    os.remove(p)
    rep.append(f"bop {vs[0]['version_number']}: {len(hits)} json, {len(cl)} classes mention dried_salt")
except Exception as e:
    rep.append(f"bop: {e}")
write("README.txt", "\n".join(rep) + "\n")
print("\n".join(rep))
