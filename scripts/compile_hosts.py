#!/usr/bin/env python3
"""Compile hosts/adblock_hosts.txt for Spotify Web from upstream lists + hosts/extra_hosts.txt.

Output format matches SpotiDuck's list ("0.0.0.0 <domain>" per line) so the same
parser can read it. Differences from SpotiDuck's workflow:
  * rules with a $domain= (or other non-trivial) option are skipped instead of
    being turned into global blocks;
  * IP literals and localhost are skipped;
  * hosts/allow_hosts.txt removes entries from the final list;
  * hosts/podcast_ad_hosts.txt entries (and their subdomains) are never taken from
    upstream lists, so the app's podcast toggle alone decides whether they are blocked;
  * the file is NOT overwritten if a source fails or the result shrinks sharply.
"""
import os
import re
import sys
import urllib.request

HOSTS_DIR = os.environ.get("HOSTS_DIR", "hosts")  # run from the repo root
OUT = os.environ.get("OUT_FILE", os.path.join(HOSTS_DIR, "adblock_hosts.txt"))
MIN_DOMAINS = int(os.environ.get("MIN_DOMAINS", "1000"))
MAX_SHRINK = float(os.environ.get("MAX_SHRINK", "0.20"))  # abort if >20% smaller

SOURCES = [
    "https://raw.githubusercontent.com/brave/adblock-lists/master/brave-lists/brave-firstparty.txt",
    "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/filters.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/MobileFilter/sections/adservers.txt",
]

# Upstream entries under these suffixes are never taken (Spotify's own
# infrastructure). hosts/extra_hosts.txt is exempt: it is hand-maintained.
SPOTIFY_FAMILY = ("spotify.com", "scdn.co", "spotifycdn.com", "spotifycdn.net")

# $options that do not narrow a host rule, so the rule is still a plain host block.
HARMLESS_OPTIONS = {"third-party", "3p", "important", "all", "first-party", "1p"}

DOMAIN_RE = re.compile(r"^[a-z0-9.\-]+$")
IP_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8", errors="ignore")


def valid(d):
    return (bool(DOMAIN_RE.match(d)) and "." in d and not d.startswith((".", "-"))
            and not d.endswith((".", "-")) and not IP_RE.match(d) and ".." not in d)


def parse_rule(line):
    """Return a domain for a plain host-block rule, else None."""
    line = line.strip()
    if not line or line[0] in "#!" or line.startswith("@@") or line.startswith("["):
        return None
    if "##" in line or "#@#" in line or "#?#" in line or "#$#" in line:
        return None  # cosmetic / scriptlet rules
    # Options after '$': only keep the rule if every option is harmless.
    if "$" in line:
        line, opts = line.split("$", 1)
        for o in opts.split(","):
            if o.strip().lower() not in HARMLESS_OPTIONS:
                return None
    if line.startswith("||"):
        line = line[2:]
        if "^" in line:
            line = line.split("^", 1)[0]
        elif "/" in line or "*" in line:
            return None
    else:
        parts = line.split()
        if len(parts) >= 2 and parts[0] in ("0.0.0.0", "127.0.0.1"):
            line = parts[1]
        elif len(parts) == 1 and not line.startswith(("|", "/", "*")):
            line = parts[0]
        else:
            return None
        if "#" in line:
            line = line.split("#", 1)[0]
    line = line.lower().strip()
    return line if valid(line) else None


def read_list(path):
    out = set()
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for raw in f:
            raw = raw.split("#", 1)[0].strip().lower()
            if raw and valid(raw):
                out.add(raw)
    return out


def previous_count():
    if not os.path.exists(OUT):
        return 0
    with open(OUT, encoding="utf-8") as f:
        return sum(1 for l in f if l.startswith("0.0.0.0 "))


def main():
    domains = set()
    failed = []
    podcast = read_list(os.path.join(HOSTS_DIR, "podcast_ad_hosts.txt"))
    for u in SOURCES:
        try:
            content = fetch(u)
        except Exception as e:  # noqa: BLE001
            failed.append(u)
            print(f"FAILED {u}: {e}", file=sys.stderr)
            continue
        n = 0
        for line in content.splitlines():
            d = parse_rule(line)
            if (d and not any(d == s or d.endswith("." + s) for s in SPOTIFY_FAMILY)
                    and not any(d == p or d.endswith("." + p) for p in podcast)):
                domains.add(d)
                n += 1
        print(f"{n:6d} domains from {u}")
    if failed:
        sys.exit(f"Aborting: {len(failed)} source(s) failed, keeping the old list.")

    extra = read_list(os.path.join(HOSTS_DIR, "extra_hosts.txt"))
    allow = read_list(os.path.join(HOSTS_DIR, "allow_hosts.txt"))
    domains |= extra
    domains = {d for d in domains if not any(d == a or d.endswith("." + a) for a in allow)}
    final = sorted(domains)
    print(f"{len(extra)} extra, {len(allow)} allow, {len(final)} total")

    old = previous_count()
    if len(final) < MIN_DOMAINS:
        sys.exit(f"Aborting: only {len(final)} domains (< {MIN_DOMAINS}).")
    if old and len(final) < old * (1 - MAX_SHRINK):
        sys.exit(f"Aborting: list shrank from {old} to {len(final)} (> {MAX_SHRINK:.0%}).")

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Spotify Web compiled AdBlock hostlist\n")
        f.write("# Brave Shields + uBlock Origin + AdGuard Mobile + extra_hosts.txt, minus allow_hosts.txt\n\n")
        for d in final:
            f.write(f"0.0.0.0 {d}\n")


if __name__ == "__main__":
    main()
