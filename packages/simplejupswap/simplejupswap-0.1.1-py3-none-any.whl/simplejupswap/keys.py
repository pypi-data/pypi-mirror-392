from typing import Union, List
from solders.keypair import Keypair
import json
import os


def load_keypair(source: Union[str, bytes, List[int], Keypair]) -> Keypair:
	"""
	Load a Keypair from:
	- str: path to JSON array of 64-byte secret key
	- bytes: raw 64-byte secret key
	- List[int]: list of 64 integers
	- Keypair: returned as-is
	"""
	if isinstance(source, Keypair):
		return source
	if isinstance(source, bytes):
		return Keypair.from_bytes(source)
	if isinstance(source, list):
		return Keypair.from_bytes(bytes(source))
	if isinstance(source, str):
		path = os.path.expanduser(source)
		with open(path, "r") as f:
			return Keypair.from_bytes(bytes(json.load(f)))
	raise TypeError("Unsupported keypair source")


