#!/usr/bin/env python3
"""Cifra un piano giornaliero con la chiave pubblica del telefono e aggiorna plans/index.json.

Uso:
  python3 tools/publish_plan.py set-key <n>        # salva la parte pubblica (campo n, base64url) in plans/key.json
  python3 tools/publish_plan.py publish piano.json # cifra piano.json -> plans/<data>.json

Formato di piano.json:
  {"date":"2026-11-21","title":"Sabato","items":[{"start":"07:00","end":"07:30","text":"...","kind":"fisso|impegno|turno|libero"}],"notes":["..."]}
Il file in chiaro NON va committato: nel repository finisce solo la versione cifrata.
"""
import base64, json, os, sys, datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PLANS = os.path.join(ROOT, "plans")
KEYF = os.path.join(PLANS, "key.json")
KEEP_DAYS = 60

def b64(b): return base64.b64encode(b).decode()
def n_to_int(s):
    s = s.strip()
    return int.from_bytes(base64.urlsafe_b64decode(s + "=" * (-len(s) % 4)), "big")

def pubkey():
    k = json.load(open(KEYF))
    return rsa.RSAPublicNumbers(e=65537, n=n_to_int(k["n"])).public_key()

def set_key(n):
    k = rsa.RSAPublicNumbers(e=65537, n=n_to_int(n)).public_key()
    assert k.key_size == 2048, "la chiave deve essere RSA 2048"
    os.makedirs(PLANS, exist_ok=True)
    json.dump({"n": n.strip(), "e": "AQAB"}, open(KEYF, "w"))
    print("chiave salvata")

def encrypt(plan):
    aes, iv = AESGCM.generate_key(256), os.urandom(12)
    ct = AESGCM(aes).encrypt(iv, json.dumps(plan, ensure_ascii=False).encode(), None)
    k = pubkey().encrypt(aes, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    return {"v": 1, "k": b64(k), "iv": b64(iv), "d": b64(ct)}

def publish(path):
    plan = json.load(open(path))
    date = plan["date"]; datetime.date.fromisoformat(date)
    os.makedirs(PLANS, exist_ok=True)
    json.dump(encrypt(plan), open(os.path.join(PLANS, date + ".json"), "w"))
    ixf = os.path.join(PLANS, "index.json")
    dates = set(json.load(open(ixf)).get("dates", [])) if os.path.exists(ixf) else set()
    dates.add(date)
    limit = (datetime.date.today() - datetime.timedelta(days=KEEP_DAYS)).isoformat()
    for d in [d for d in dates if d < limit]:
        dates.discard(d)
        f = os.path.join(PLANS, d + ".json")
        if os.path.exists(f): os.remove(f)
    json.dump({"dates": sorted(dates)}, open(ixf, "w"))
    print("pubblicato", date, "| piani:", len(dates))

if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "set-key": set_key(a[1])
    elif len(a) == 2 and a[0] == "publish": publish(a[1])
    else: print(__doc__); sys.exit(1)
