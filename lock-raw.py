#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pcr", type=int, required=True)
    parser.add_argument("--pcrlock", required=True)
    parser.add_argument("file")
    args = parser.parse_args()

    algorithms = {
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256,
        "sha384": hashlib.sha384,
        "sha512": hashlib.sha512,
    }

    digests = {}
    with open(args.file, "rb") as f:
        hs = {name: factory() for name, factory in algorithms.items()}
        while chunk := f.read(1024 * 1024):
            for h in hs.values():
                h.update(chunk)

    digests = {name: h.hexdigest() for name, h in hs.items()}

    # Let systemd-pcrlock generate the canonical format.
    fd, tmp = tempfile.mkstemp()
    os.close(fd)

    try:
        subprocess.run([
            "/usr/lib/systemd/systemd-pcrlock", "lock-raw",
            f"--pcr={args.pcr}",
            f"--pcrlock={tmp}",
            "/dev/null",
        ], check=True)

        with open(tmp) as f:
            data = json.load(f)

        for record in data["records"]:
            for digest in record["digests"]:
                alg = digest["hashAlg"]
                if alg in digests:
                    digest["digest"] = digests[alg]

        output = args.pcrlock
        os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)

        with open(output, "w") as f:
            json.dump(data, f, separators=(",", ":"))
            f.write("\n")

    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    main()
