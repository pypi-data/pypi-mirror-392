import base64
import logging
from typing import Optional, Dict, Any, Union

import requests
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from .exceptions import SimpleJupSwapError


SOL_MINT = "So11111111111111111111111111111111111111112"

PRIORITY_FEE_LAMPORTS = {
	"low": 0,
	"medium": 10_000,
	"high": 50_000,
	"veryHigh": 100_000,
}


def _get_priority_level_from_lamports(lamports: int) -> str:
	"""
	Determine priority level string from custom lamports value based on preset ranges.
	"""
	if lamports < PRIORITY_FEE_LAMPORTS["medium"]:
		return "low"
	elif lamports < PRIORITY_FEE_LAMPORTS["high"]:
		return "medium"
	elif lamports < PRIORITY_FEE_LAMPORTS["veryHigh"]:
		return "high"
	else:
		return "veryHigh"

def _get_session(session: Optional[requests.Session]) -> requests.Session:
	return session or requests.Session()


def get_sol_balance(pubkey: str, session: Optional[requests.Session] = None) -> float:
	"""
	Return SOL UI balance for a given public key.
	"""
	s = _get_session(session)
	try:
		resp = s.get(f"https://lite-api.jup.ag/ultra/v1/balances/{pubkey}", timeout=5)
		resp.raise_for_status()
		data = resp.json()
		return float(data["SOL"]["uiAmount"])
	except Exception as e:
		raise SimpleJupSwapError(f"get_sol_balance failed: {e}") from e


def get_sol_balance_lamports(pubkey: str, session: Optional[requests.Session] = None) -> int:
	"""
	Return SOL balance in lamports for a given public key.
	"""
	s = _get_session(session)
	try:
		resp = s.get(f"https://lite-api.jup.ag/ultra/v1/balances/{pubkey}", timeout=5)
		resp.raise_for_status()
		data = resp.json()
		return int(data["SOL"]["amount"])
	except Exception as e:
		raise SimpleJupSwapError(f"get_sol_balance_lamports failed: {e}") from e


def get_all_token_balances(pubkey: str, session: Optional[requests.Session] = None) -> Dict[str, Any]:
	"""
	Return all token balances map for a given public key (raw Jupiter response).
	"""
	s = _get_session(session)
	try:
		resp = s.get(f"https://lite-api.jup.ag/ultra/v1/balances/{pubkey}", timeout=5)
		resp.raise_for_status()
		return resp.json()
	except Exception as e:
		raise SimpleJupSwapError(f"get_all_token_balances failed: {e}") from e


def get_token_balance(pubkey: str, mint: str, session: Optional[requests.Session] = None) -> int:
	"""
	Return raw token balance (amount as integer) for a specific mint.
	Returns 0 if the mint is not found in the wallet or if the account has zero balance.
	Note: 0 can mean either no account exists or the account exists with zero balance.
	"""
	s = _get_session(session)
	try:
		resp = s.get(f"https://lite-api.jup.ag/ultra/v1/balances/{pubkey}?mint={mint}", timeout=5)
		resp.raise_for_status()
		data = resp.json()
		if mint not in data:
			return 0
		return int(data[mint]["amount"])
	except Exception as e:
		raise SimpleJupSwapError(f"get_token_balance failed: {e}") from e


def get_token_price(mint: str, session: Optional[requests.Session] = None) -> float:
	"""
	Return the USD price for a given token mint.
	"""
	s = _get_session(session)
	try:
		resp = s.get("https://lite-api.jup.ag/price/v3", params={"ids": mint}, timeout=5)
		resp.raise_for_status()
		body = resp.json()
		info = body.get(mint)
		if not info or "usdPrice" not in info:
			raise SimpleJupSwapError(f"price not available for {mint}")
		return float(info["usdPrice"])
	except Exception as e:
		raise SimpleJupSwapError(f"get_token_price failed: {e}") from e


def quote(
	input_mint: str,
	output_mint: str,
	amount: int,
	slippage_bps: int = 200,
	session: Optional[requests.Session] = None
) -> Dict[str, Any]:
	"""
	Get a Jupiter quote for a swap.
	"""
	s = _get_session(session)
	url = (
		"https://lite-api.jup.ag/swap/v1/quote"
		f"?inputMint={input_mint}&outputMint={output_mint}"
		f"&amount={amount}&slippageBps={slippage_bps}&restrictIntermediateTokens=true"
	)
	try:
		resp = s.get(url, timeout=5)
		resp.raise_for_status()
		q = resp.json()
		if "errorCode" in q and q["errorCode"] is not None:
			raise SimpleJupSwapError(f"Jupiter quote error: {q['errorCode']} {q.get('errorMessage','')}")
		return q
	except Exception as e:
		raise SimpleJupSwapError(f"quote failed: {e}") from e


def swap(
	input_mint: str,
	output_mint: str,
	amount: int,
	keypair: Keypair,
	rpc_url: str,
	*,
	slippage_bps: int = 200,
	skip_preflight: bool = False,
	max_retries: int = 3,
	session: Optional[requests.Session] = None,
	confirm_transaction: bool = False,
	priority: Union[str, int] = "high",
) -> str:
	"""
	Execute a Jupiter swap by fetching a signed transaction, signing with the provided keypair,
	and sending to the provided RPC.
	Returns the transaction signature.
	"""
	s = _get_session(session)
	q = quote(input_mint, output_mint, amount, slippage_bps=slippage_bps, session=s)
	
	# Allows for custom priority fee lamports or string preset name
	if isinstance(priority, int):
		priority_lamports = priority
		priority_level = _get_priority_level_from_lamports(priority)
	else:
		priority_lamports = PRIORITY_FEE_LAMPORTS.get(priority, PRIORITY_FEE_LAMPORTS["high"])
		priority_level = priority
	
	body = {
		"quoteResponse": q,
		"userPublicKey": str(keypair.pubkey()),
		"wrapAndUnwrapSol": True,
		"dynamicComputeUnitLimit": True,
		"prioritizationFeeLamports": {
			"priorityLevelWithMaxLamports": {
				"maxLamports": priority_lamports,
				"priorityLevel": priority_level,
			}
		}
	}
	try:
		swap_resp = s.post("https://lite-api.jup.ag/swap/v1/swap", json=body, timeout=5)
		swap_resp.raise_for_status()
		swap_json = swap_resp.json()
		raw = base64.b64decode(swap_json["swapTransaction"])
		tx = VersionedTransaction.from_bytes(raw)
		signed = VersionedTransaction(tx.message, [keypair])

		client = Client(rpc_url)
		res = client.send_raw_transaction(
			bytes(signed),
			TxOpts(skip_preflight=skip_preflight, max_retries=max_retries)
		)
		sig = res.value
		logging.info("Swap sent: https://solscan.io/tx/%s", sig)

		if confirm_transaction:
			confirmation = client.confirm_transaction(
				sig,
				commitment="finalized"
			)
			if confirmation.value[0].err:
				raise SimpleJupSwapError(f"confirmation failed: {confirmation.value[0].err}")
			else:
				logging.info("Swap confirmed: https://solscan.io/tx/%s", sig)

		return sig
	except Exception as e:
		raise SimpleJupSwapError(f"swap failed: {e}") from e
