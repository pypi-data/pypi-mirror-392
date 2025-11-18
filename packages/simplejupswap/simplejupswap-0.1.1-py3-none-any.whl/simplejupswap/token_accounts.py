from typing import List

from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import close_account, CloseAccountParams
from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts
from .exceptions import SimpleJupSwapError


def close_empty_token_accounts(keypair: Keypair, rpc_url: str, batch_size: int = 10) -> List[str]:
	"""
	Close all empty SPL token accounts for the owner in batches.
	Returns a list of transaction signatures (one per batch).
	"""
	try:
		client = Client(rpc_url)
		owner = keypair.pubkey()
		resp = client.get_token_accounts_by_owner_json_parsed(
			owner,
			TokenAccountOpts(program_id=TOKEN_PROGRAM_ID)
		)
		to_close = []
		for acc in resp.value:
			try:
				amount = int(acc.account.data.parsed["info"]["tokenAmount"]["amount"])
				if amount == 0:
					to_close.append(acc.pubkey)
			except (KeyError, TypeError, ValueError) as e:
				raise SimpleJupSwapError(f"failed to parse token account {acc.pubkey}: {e}") from e

		signatures: List[str] = []
		for start in range(0, len(to_close), batch_size):
			batch = to_close[start:start + batch_size]
			if not batch:
				continue
			ixs = [
				close_account(CloseAccountParams(
					program_id=TOKEN_PROGRAM_ID,
					account=pk,
					dest=owner,
					owner=owner
				))
				for pk in batch
			]
			bh = client.get_latest_blockhash().value.blockhash
			msg = MessageV0.try_compile(
				payer=owner,
				instructions=ixs,
				recent_blockhash=bh,
				address_lookup_table_accounts=[]
			)
			tx = VersionedTransaction(msg, [keypair])
			signatures.append(client.send_raw_transaction(bytes(tx)).value)

		return signatures
	except SimpleJupSwapError:
		raise
	except Exception as e:
		raise SimpleJupSwapError(f"close_empty_token_accounts failed: {e}") from e


