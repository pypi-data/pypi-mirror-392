import os
import time
import dotenv
from simplejupswap import (
	SOL_MINT,
	get_sol_balance,
	get_token_balance,
	swap,
	transfer_sol,
	load_keypair,
	close_empty_token_accounts
)

dotenv.load_dotenv()

def main() -> None:
	# RPC endpoint (override with SOLANA_MAINNET env var. this RPC is HUGELY rate limited)
	RPC = os.getenv("<RPC_URL>")

	# Load wallet
	keypair = load_keypair(os.path.expanduser("<KEYPAIR_PATH>"))
	pubkey_str = str(keypair.pubkey()) #the pubkey of the wallet

	# Get and print SOL balance (UI units)
	print("SOL balance:", get_sol_balance(pubkey_str))

	# Swap a small amount of SOL (lamports) to a token mint
	target_mint = "<TOKEN_MINT>"
	
	sig_swap = swap(SOL_MINT, target_mint, 500_000, keypair, RPC, confirm_transaction=False, skip_preflight=True, priority="veryHigh")
	print("swap sig:", sig_swap)

	time.sleep(3) #avoid rate limits and allow blockchain to update

	# swapping back to SOL
	try:
		bal = get_token_balance(pubkey_str, target_mint)
		print("token balance:", bal)
		sig_swap_back = swap(target_mint, SOL_MINT, bal, keypair, RPC, confirm_transaction=False, skip_preflight=True, priority="veryHigh")
		print("swap back sig:", sig_swap_back)
	except Exception as e:
		print("error swapping back to SOL:", e)

	# transfer SOL example- to yourself for the demo lol
	sig_xfer = transfer_sol(pubkey_str, 500_000, keypair, RPC)  # 0.0005 SOL
	print("transfer sig:", sig_xfer)

	# finally, close all empty token accounts. an important step! but this can be done in batches.
	close_empty_token_accounts(keypair, RPC)
	print("closed empty token accounts")


if __name__ == "__main__":
	main()
	
	

