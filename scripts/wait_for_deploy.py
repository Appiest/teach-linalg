"""Wait for the newest 'Deploy course site' run on GitHub and print its conclusion.

Exit codes: 0 success, 1 failed or timed out, 2 GitHub API unreachable.
"""

import json
import sys
import time
import urllib.error
import urllib.request

RUNS_URL = "https://api.github.com/repos/Appiest/teach-linalg/actions/runs?per_page=5"
TIMEOUT_SECONDS = 600


def latest_deploy_run() -> dict | None:
    request = urllib.request.Request(RUNS_URL, headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request, timeout=20) as response:
        runs = json.load(response)["workflow_runs"]
    return next((run for run in runs if run["name"] == "Deploy course site"), None)


def main() -> None:
    started = time.time()
    time.sleep(20)
    while time.time() - started < TIMEOUT_SECONDS:
        try:
            run = latest_deploy_run()
        except (urllib.error.URLError, TimeoutError) as error:
            print(f"GitHub API unreachable: {error}")
            sys.exit(2)
        if run and run["status"] == "completed":
            print(f"{run['conclusion']}: {run['html_url']}")
            sys.exit(0 if run["conclusion"] == "success" else 1)
        time.sleep(20)
    print("Timed out waiting for the deploy run")
    sys.exit(1)


if __name__ == "__main__":
    main()
