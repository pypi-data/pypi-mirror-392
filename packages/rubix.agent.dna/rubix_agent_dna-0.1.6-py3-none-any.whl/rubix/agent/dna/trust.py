import json
import os
from typing import Any, Dict, Optional

import requests
from rubix.client import RubixClient
from rubix.signer import Signer

from .node_client import NodeClient


class RubixTrustService:
    """
    Handles:
      - RubixClient + Signer
      - DID management
      - Signing envelopes
      - Verifying signatures via /api/verify-signature
    """

    def __init__(
        self,
        mnemonic_env: str = "HOST_MNEMONIC",
        framework: str = "host",
        timeout: float = 300.0,
    ) -> None:
        node = NodeClient(framework=framework)
        self.base_url = node.get_base_url().rstrip("/")
        self.timeout = timeout

        client = RubixClient(node_url=self.base_url, timeout=timeout)
        mnemonic = os.getenv(mnemonic_env)
        if not mnemonic:
            raise RuntimeError(f"❌ {mnemonic_env} is missing in .env file!")

        self.signer = Signer(rubixClient=client, mnemonic=mnemonic)
        self.did = self.signer.did

        print("✅ RubixTrustService DID:", self.did)
        print("✅ RubixTrustService base URL:", self.base_url)

    # ---------- signing ----------

    def sign_envelope(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sign an envelope dict and return a block:
          { "agent": <did>, "envelope": {...}, "signature": "<hex>" }
        """
        print("Public Key (hex): ", self.signer.get_keypair().public_key)
        keypair = self.signer.get_keypair()

        envelope_json = json.dumps(envelope, sort_keys=True)
        # sig = self.signer.sign(envelope_json.encode("utf-8"))
        signature_bytes = keypair.sign(envelope_json)

        # sig = ""
        if isinstance(sig, (bytes, bytearray)):
            sig = sig.hex()
        else:
            sig = str(sig)

        return {
            "agent": self.did,
            "envelope": envelope,
            "signature": signature_bytes,
        }

    # ---------- verification ----------

    def verify_envelope(
        self,
        signer_did: str,
        envelope: Dict[str, Any],
        signature: str,
        timeout: Optional[float] = None,
    ) -> bool:
        """
        Verify that `signature` is valid for the given DID + envelope.
        Uses host node's /api/verify-signature.
        """
        url = f"{self.base_url}/api/verify-signature"
        envelope_json = json.dumps(envelope, sort_keys=True)

        params = {
            "signer_did": signer_did,
            "signed_msg": envelope_json,
            "signature": signature,
        }
        try:
            resp = requests.get(url, params=params, timeout=timeout or self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return bool(data.get("status", False))
        except Exception as e:
            # you can log here if you like
            print(f"⚠️ verify_envelope error: {e}")
            return False