import asyncio
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv
from .node_client import NodeClient
from .trust import RubixTrustService


def load_nft_config() -> dict:
    """
    Local copy of NFT config loader so dna.handler does not depend on host.*.
    Adjust defaults to match your previous host.config_loader.
    """
    return {
        "artifact_path": os.getenv("NFT_ARTIFACT_PATH", "artifacts/pickleball.json"),
        "metadata_path": os.getenv("NFT_METADATA_PATH", "artifacts/pickleball-meta.json"),
        "value": float(os.getenv("NFT_VALUE", "0.001")),
        "data": os.getenv("NFT_INIT_DATA", "init data"),
    }

class RubixMessageHandler:
    """
    Encapsulates:
      - RubixTrustService (signing + verification)
      - NFT deployment / token file
      - Building signed outbound messages
      - Parsing & verifying remote responses
      - Triggering NFT executions
    """

    def __init__(
        self,
        mnemonic_env: str = "HOST_MNEMONIC",
        token_filename: str = "token.txt",
        trust_service: RubixTrustService | None = None,
    ) -> None:
        self.nft_cfg = load_nft_config()

        # trust layer (sign + verify)
        self.trust = trust_service or RubixTrustService(
            mnemonic_env=mnemonic_env,
            framework="host",
        )
        self.did = self.trust.did
        self.signer = self.trust.signer  # still available for NFT deploy

        # where we persist the NFT address
        current_dir = Path(__file__).parent
        self.token_path = current_dir / token_filename
        print("Path: ", self.token_path)
        self.nft_token = self._load_or_deploy_nft()

        self.last_parts: List[Dict[str, Any]] = []

        print("✅ Host Rubix NFT:", self.nft_token)

    # ---------- NFT address init ----------

    def execute_nft(self, nft_address: str, payload: Any) -> Dict:
        """
        Execute an NFT using the existing signer from trust service.
        """
        nft_data = json.dumps(payload)

        try:
            print("NFT: ", nft_address)
            print("Data: ", nft_data)
            # ✅ use the real Rubix SDK method name
            response = self.signer.execute_nft(
                nft_address=nft_address,
                nft_data=nft_data,
            )
            print("Executed")
        except Exception as e:
            raise RuntimeError(f"Rubix execute_nft call failed: {e}")

        if not response.get("status", False):
            raise RuntimeError(
                f"NFT Execution Failed: {response.get('message', '<no message>')}"
            )

        return response

    def _load_or_deploy_nft(self) -> str:
        if not self.token_path.exists():
            raise RuntimeError(
                f"token.txt not found at {self.token_path}. "
                "Create this file with a valid NFT address."
            )

        token = self.token_path.read_text(encoding="utf-8").strip()
        if not token:
            raise RuntimeError(f"token.txt at {self.token_path} is empty.")

        print("ℹ️ Using existing NFT token:", token)
        return token

        # deploy a new NFT via signer (we still do deployment here)
        resp = self.signer.deploy_nft(
            artifact_file=self.nft_cfg["artifact_path"],
            metadata_file=self.nft_cfg["metadata_path"],
            nft_value=self.nft_cfg["value"] or 0.001,
            nft_data=self.nft_cfg["data"] or "init data",
        )
        if resp.get("error"):
            raise RuntimeError(f"NFT deployment failed: {resp['error']}")

        nft_address = resp["nft_address"]
        self.token_path.write_text(nft_address, encoding="utf-8")
        print("🚀 Deployed new NFT:", nft_address)
        return nft_address

    # ---------- outbound message builder ----------

    def build_outgoing_payload(
        self,
        task: str,
        state: dict,
    ) -> tuple[dict, str]:
        """
        Build the A2A message payload with a signed host block.

        Returns: (payload, message_id)

        NOTE: We do NOT send `taskId` to the remote A2A server.
        Task/context IDs live only in the host envelope for Rubix/NFT/debugging.
        """
        task_id = state.get("task_id", str(uuid.uuid4()))
        context_id = state.get("context_id", str(uuid.uuid4()))
        message_id = str(uuid.uuid4())

        host_envelope = {
            "original_message": task,
            "task_id": task_id,
            "context_id": context_id,
            "message_id": message_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # sign via RubixTrustService
        host_signed = self.trust.sign_envelope(host_envelope)

        payload = {
            "message": {
                "role": "user",
                "parts": [
                    {
                        "type": "text",
                        "text": json.dumps({"host": host_signed}),
                    }
                ],
                "messageId": message_id,
                # ❌ don't send taskId to remote
                "contextId": context_id,
            }
        }

        return payload, message_id   # ✅ only TWO values
    # ---------- inbound response handling ----------

    async def handle_response_parts(
        self,
        resp_parts: List[Dict[str, Any]],
        original_task: str,
        remote_name: str,
        *,
        execute_nft: bool = True,
    ) -> Dict[str, Any]:
        """
        Parse remote parts, verify signatures, write to NFT.

        Returns a dict like:
          {
            "messages": [...],
            "trust_issues": [...],
            "error": "..." | None
          }
        """
        verified: List[Dict[str, Any]] = []
        trust_issues: List[str] = []
        error_msg: Optional[str] = None

        for part in resp_parts:
            raw_text = part.get("text") or part.get("content", "")
            try:
                payload = json.loads(raw_text)
            except (TypeError, json.JSONDecodeError):
                continue

            # Expect {"host": {...}, "agent": {...}}
            if not isinstance(payload, dict) or "agent" not in payload:
                continue

            host_block = payload.get("host")
            agent_block = payload["agent"]

            signer_did = agent_block.get("agent")
            env = agent_block.get("envelope", {})
            sig = agent_block.get("signature")

            if not (signer_did and env and sig):
                trust_issues.append("Missing fields in agent block")
                print("Missing fields in agent block")
                continue

            # verify via trust service
            if not self.trust.verify_envelope(signer_did, env, sig):
                trust_issues.append(f"Invalid signature from {signer_did}")
                print(f"Invalid signature from {signer_did}")
                continue

            # Optional consistency check
            if env.get("original_message") != original_task:
                trust_issues.append("Original message mismatch")
                print("Original message mismatch")

            verified.append(
                {
                    "host": host_block,
                    "agent": agent_block,
                    "agent_sig_valid": True,
                }
            )
            print("Verified")

        if not verified and not trust_issues:
            error_msg = "No valid envelope response"
            print("No valid envelope response")

        # Save for NFT execution
        self.last_parts = verified

        # write to NFT
        if execute_nft and verified:
            try:
                payload = self._build_nft_payload(remote_name)
                resp = await asyncio.to_thread(
                    self.execute_nft,
                    self.nft_token,
                    payload,
                )
                print("🚀 NFT execution result:", resp)
            except Exception as e:
                print("⚠️ NFT execution failed:", e)

        result: Dict[str, Any] = {
            "messages": verified,
            "trust_issues": trust_issues or None,
        }
        if error_msg:
            result["error"] = error_msg
        return result

    def _build_nft_payload(self, remote_name: str) -> Dict[str, Any]:
        """
        Build the JSON that will be stored in the NFT.
        Here we keep it simple: host + list of agent blocks.
        """
        host_block = None
        responses = []
        for entry in self.last_parts:
            if not host_block and entry.get("host"):
                host_block = entry["host"]
            if entry.get("agent"):
                responses.append(entry["agent"])

        return {
            "comment": f"Pickleball scheduling with {remote_name}",
            "executor": "host_agent",
            "did": self.did,
            "host": host_block,
            "responses": responses,
        }