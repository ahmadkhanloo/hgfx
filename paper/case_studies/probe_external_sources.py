"""Read-only public-source accessibility inventory. Never downloads participant-level data.

This is NOT a study replication, data license verification or scientific parity check.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URLS = {
    "oberwelland_osf_node": "https://api.osf.io/v2/nodes/3xrn2/",
    "oberwelland_osf_files": "https://api.osf.io/v2/nodes/3xrn2/files/",
    "oberwelland_osfstorage": "https://api.osf.io/v2/nodes/3xrn2/files/osfstorage/",
    "gao_osf_node": "https://api.osf.io/v2/nodes/sk82r/",
    "gao_osf_files": "https://api.osf.io/v2/nodes/sk82r/files/",
    "gao_osfstorage": "https://api.osf.io/v2/nodes/sk82r/files/osfstorage/",
    "reed_github_metadata": "https://api.github.com/repos/ModelDBRepository/258631/contents/IRL_Data.mat",
    "mathys_oracle_demo_metadata": "https://api.github.com/repos/ComputationalPsychiatry/hgf-toolbox/contents/demo/example_binary_input.txt?ref=2437f4dc241541072722a2695ddeca7b44d83dd3",
}


def probe(label, url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "HGFX-public-source-screening/1.0 (metadata only)",
            "Accept": "application/json",
        },
    )
    out = {"candidate": label, "url": url, "status": None, "accessible_json": False, "listed_files": [], "error": None}
    try:
        with urllib.request.urlopen(req, timeout=18) as response:
            out["status"] = response.status
            # Limit metadata to 128 KB; never fetch file content from a data-download URL.
            raw = response.read(131073)
            if len(raw) > 131072:
                out["error"] = "metadata_exceeds_128KiB_limit"
                return out
            payload = json.loads(raw)
            out["accessible_json"] = True
            entries = payload.get("data", [])
            if isinstance(entries, dict):
                entries = [entries]
            if isinstance(payload, list):
                entries = payload
            for item in entries[:50]:
                attr = item.get("attributes", item)
                out["listed_files"].append({
                    "name": str(attr.get("name", attr.get("filename", item.get("id", ""))))[:160],
                    "kind": str(attr.get("kind", item.get("type", "")))[:60],
                    "size": attr.get("size"),
                    "id": str(item.get("id", ""))[:100],
                })
            if "links" in payload and isinstance(payload["links"], dict):
                out["pagination"] = {"next": payload["links"].get("next")}
    except urllib.error.HTTPError as exc:
        out["status"] = exc.code
        out["error"] = f"HTTP_{exc.code}"
    except Exception as exc:
        out["error"] = f"{type(exc).__name__}: {str(exc)[:160]}"
    return out


def main():
    output = Path(sys.argv[1] if len(sys.argv) > 1 else "external_source_probe.json")
    result = {
        "scope": "public API metadata only; no raw participant data or fit",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "github_run_id": os.getenv("GITHUB_RUN_ID"),
        "github_sha": os.getenv("GITHUB_SHA"),
        "results": [probe(name, url) for name, url in URLS.items()],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
