"""Blockchain Audit Trail (stub).

Planned:
  Every verdict is signed and its hash anchored to a public chain
  (e.g. Ethereum L2) so verdicts cannot be quietly revised after
  publication. Users can verify a verdict's integrity at any time.

Implementation note:
  For scale and cost, batch anchor: hash a Merkle root of every hour's
  verdicts into a single transaction.

Spec reference: user brief, PART 2 Feature 8.
"""


def anchor_verdict(verdict_hash: str) -> str:
    raise NotImplementedError("Blockchain audit trail — scheduled for PR #5")
