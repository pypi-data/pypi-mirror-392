import json
import os
from typing import Any, Dict, Optional

import requests
from rubix.client import RubixClient
from rubix.signer import Signer
from rubix.did import online_signature_verify, signatureResponseError

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
        print("Agent is going to sign")
        print("Public Key (hex): ", self.signer.get_keypair().public_key)
        keypair = self.signer.get_keypair()

        envelope_json = json.dumps(envelope, sort_keys=True)
        envelope_bytes = envelope_json.encode("utf-8")
        signature_bytes = keypair.sign(envelope_bytes)
        signature_hex = signature_bytes.hex()
        return {
            "agent": self.did,
            "envelope": envelope,
            "signature": signature_hex,
        }

    # ---------- verification ----------

    def verify_envelope(
        self,
        signer_did: str,
        envelope: Dict[str, Any],
        signature: str,                 # hex string from sign_envelope
        timeout: Optional[float] = None # kept for API compat, not used
    ) -> bool:
        """
        Verify that `signature` is valid for the given DID + envelope.
        Uses Rubix node's online_signature_verify helper.
        """

        # 1) Build canonical JSON exactly as in sign_envelope
        envelope_json = json.dumps(envelope, sort_keys=True)
        message_bytes = envelope_json.encode("utf-8")

        # 2) Convert hex string -> raw bytes for verifier
        try:
            signature_bytes = bytes.fromhex(signature)
        except ValueError:
            print("⚠️ verify_envelope: invalid hex signature string")
            return False

        # 3) Delegate to Rubix helper
        try:
            is_valid = online_signature_verify(
                rubixNodeBaseUrl=self.base_url,
                did=signer_did,
                message=message_bytes,
                signature=signature_bytes,
            )
            return bool(is_valid)
        except signatureResponseError as e:
            print(f"⚠️ verify_envelope error: {e}")
            return False