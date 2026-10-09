"""Check a deployed Sawaal Saathi URL and write proof_report.txt (attach it to your article).

  python3 verify_deployment.py https://YOUR-ID.lambda-url.us-east-1.on.aws/

It only passes the "Bedrock" check when the answer really came from Amazon Bedrock.
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone

SAMPLE_ANSWER = ("During my second year at college I led a team of four for a project. Our app kept crashing "
                 "on the demo week, and my task was to find out why. I decided to add logging, tested each "
                 "feature one by one and fixed a database bug in two days. As a result we presented on time "
                 "and our project won second place out of 20 teams. I learned to stay calm and test step by step.")


def call(url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if payload is not None else "GET")
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.status, r.read().decode("utf-8")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    url = sys.argv[1]
    lines, ok = [f"Sawaal Saathi deployment check", f"URL: {url}",
                 f"Time (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}", ""], True

    def rec(name, passed, detail=""):
        nonlocal ok
        ok = ok and passed
        lines.append(f"[{'PASS' if passed else 'FAIL'}] {name} {detail}".rstrip())

    try:
        t = time.time()
        s, body = call(url)
        rec("Web page loads", s == 200 and "Sawaal Saathi" in body, f"({time.time() - t:.1f}s)")

        s, body = call(url, {"action": "question", "track": "tech"})
        q = json.loads(body).get("question", "")
        rec("Question endpoint", bool(q), f'-> "{q}"')

        t = time.time()
        s, body = call(url, {"action": "score", "question": q or "Tell me about a project.",
                             "answer": SAMPLE_ANSWER, "lang": "en"})
        d = json.loads(body)
        card = d.get("card", {})
        rec("Scorecard works", "score" in card, f"-> {card.get('score')}/100, {card.get('level')}")
        rec("Feedback comes from Amazon Bedrock", d.get("source") == "bedrock",
            f"(source={d.get('source')}, {time.time() - t:.1f}s)")
        lines.append("Feedback sample:\n" + str(d.get("feedback", ""))[:600])

        s, body = call(url, {"action": "selfcheck"})
        info = json.loads(body)
        rec("Bedrock self-check", info.get("bedrock") is True,
            f"(model={info.get('model')}, region={info.get('region')}, error={info.get('error', 'none')})")
    except Exception as e:
        rec("Request completed", False, f"-> {type(e).__name__}: {e}")

    lines += ["", "RESULT: " + ("ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED, see the README troubleshooting")]
    report = "\n".join(lines)
    print(report)
    with open("proof_report.txt", "w", encoding="utf-8") as f:
        f.write(report + "\n")
    print("\nSaved proof_report.txt")
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
