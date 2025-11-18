from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.system_program import transfer, TransferParams
from solana.rpc.api import Client
from .exceptions import SimpleJupSwapError


def transfer_sol(to: str, lamports: int, keypair: Keypair, rpc_url: str) -> str:
	"""
	Transfer lamports to the destination address using a v0 transaction.
	Returns the transaction signature.
	"""
	try:
		client = Client(rpc_url)
		ix = transfer(TransferParams(
			from_pubkey=keypair.pubkey(),
			to_pubkey=Pubkey.from_string(to),
			lamports=lamports
		))
		bh = client.get_latest_blockhash().value.blockhash
		msg = MessageV0.try_compile(
			payer=keypair.pubkey(),
			instructions=[ix],
			recent_blockhash=bh,
			address_lookup_table_accounts=[]
		)
		tx = VersionedTransaction(msg, [keypair])
		return client.send_raw_transaction(bytes(tx)).value
	except Exception as e:
		raise SimpleJupSwapError(f"transfer_sol failed: {e}") from e


