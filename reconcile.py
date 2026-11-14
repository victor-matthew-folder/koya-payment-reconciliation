#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.

Run: python3 reconcile.py
"""
import json

# Step 1: for every txn_id, remember only its LATEST attempt (by timestamp).
latest = {}  # txn_id -> the newest event seen so far

with open("payments.jsonl", encoding="utf-8") as f:
    for line in f:
        # Ignore lines that can't be read (broken JSON)
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue

        # Ignore events without a txn_id
        txn_id = event.get("txn_id")
        if not txn_id:
            continue

        # Keep this event only if it is newer than what we already stored.
        # (ts looks like 2026-09-21T15:30:26Z, so comparing text works.)
        if txn_id not in latest or event["ts"] > latest[txn_id]["ts"]:
            latest[txn_id] = event

# Step 2: count only the payments whose latest attempt is a success.
total = 0.0
count = 0
for event in latest.values():
    if event["status"] == "success":
        # Some amounts are text with commas, e.g. "55,707.77"
        amount = float(str(event["amount"]).replace(",", ""))
        total += amount
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
