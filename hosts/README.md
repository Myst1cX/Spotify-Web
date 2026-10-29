# Ad-block host lists

How the host files in this folder are built and used by the Spotify Web app (v1.67).

## The files

| File | Edited by | What it does |
|---|---|---|
| `adblock_hosts.txt` | the workflow (never by hand) | The compiled list the app downloads. One `0.0.0.0 <domain>` per line. Every edit is overwritten on the next compile. |
| `extra_hosts.txt` | you | Hosts that are **always added** to the compiled list. They skip the Spotify-family and podcast filters, so this is where Spotify's own ad hosts live (e.g. `audio-ads.spotify.com`). |
| `allow_hosts.txt` | you | Hosts that must **never be in the compiled list**, even if an upstream list or `extra_hosts.txt` has them. Applied last, so it wins over both. Currently empty. |
| `podcast_ad_hosts.txt` | you | Opt-in podcast ad hosts (`omny.fm`, `tritondigital.com`, `adswizz.com`). **Not compiled**: the app downloads it directly and uses it only when the Settings toggle "Block podcast ad hosts" is on. |

Format of the three hand-edited files: one domain per line, `#` starts a comment. A listed domain also blocks all its subdomains (`example.com` covers `a.b.example.com`; `a.example.com` does not cover `example.com`).

## The workflow

`.github/workflows/update-adblock-hosts.yml` ("Update AdBlock Hosts") runs `scripts/compile_hosts.py` and commits `hosts/adblock_hosts.txt` if it changed.

It runs:
- every day at 03:00 UTC,
- manually (Actions tab, "Run workflow"),
- on a push to `main` that changes the workflow, `scripts/compile_hosts.py`, `extra_hosts.txt`, `allow_hosts.txt` or `podcast_ad_hosts.txt`.

## What the script does, in order

1. Downloads three upstream lists: Brave `brave-firstparty.txt`, uBlock Origin `filters.txt`, AdGuard Mobile `adservers.txt`.
2. Keeps only plain host-block rules (`||host^`, `0.0.0.0 host`, `127.0.0.1 host`, a bare host). Skipped: comments, `@@` exceptions, cosmetic/scriptlet rules, IP addresses, `localhost`, and any rule with a narrowing `$` option such as `$domain=`, `$script`, `$popup`. Only `third-party`, `3p`, `important`, `all`, `first-party`, `1p` are accepted.
3. Drops upstream hosts under `spotify.com`, `scdn.co`, `spotifycdn.com`, `spotifycdn.net`, and under any host in `podcast_ad_hosts.txt`.
4. Adds everything in `extra_hosts.txt`.
5. Removes everything in `allow_hosts.txt` (and subdomains of it).
6. Sorts, removes duplicates, writes `adblock_hosts.txt`.

Safety checks: the old list is kept (nothing is written) if any upstream download fails, if fewer than 1000 hosts result, or if the list would shrink by more than 20 %.

## What the app does with them

- Downloads `adblock_hosts.txt` on every start (and `podcast_ad_hosts.txt` only when the toggle is on) from `raw.githubusercontent.com/Myst1cX/Spotify-Web/main/hosts/`. If a download fails, the last downloaded copy stays in use. Until the first download succeeds, a copy bundled in the APK is used. That bundled copy is refreshed by hand when building a release; the workflow does not touch it.
- Each request is checked in this order, and the first match decides: ad-audio ID, core Spotify whitelist (never blocked), static files (`.js`, `.css`, images, fonts; never blocked), canvas videos, hardcoded ad patterns, then these lists.
- Blocked audio gets a silent audio file; other blocked requests get an empty reply.

**The files cannot override two things:** the app's core Spotify whitelist (adding such a host to `extra_hosts.txt` has no effect) and the app's hardcoded ad patterns (Spotify's own ad hosts are hardcoded as well as listed here, so `allow_hosts.txt` cannot unblock them; that needs an app change).

## Common tasks

- **Block one more host:** add it to `extra_hosts.txt` and push. The workflow recompiles; the app picks it up on its next start.
- **Stop blocking a host from the upstream lists:** add it to `allow_hosts.txt` and push. If a *parent* domain is also listed, allow the parent (the app matches a host and its parents).
- **Change the podcast hosts:** edit `podcast_ad_hosts.txt` and push. No recompile is needed for the app, but the push re-runs the workflow so upstream entries under those hosts are stripped from the compiled list.
- **Test locally:** from the repo root run `OUT_FILE=/tmp/test.txt python3 scripts/compile_hosts.py`. This writes to `/tmp/test.txt` instead of the real list.

`allow_hosts.txt` is empty because nothing upstream has needed unblocking so far. It is a safety valve for upstream-list hosts, not a protection against accidental deletion.
