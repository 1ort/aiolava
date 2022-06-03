
# aiolava
Async API wrapper for lava.ru

## Quickstart
1. Copy `aiolava/` folder into your project
2. Install dependencies `pip install -r aiolava/requirements.txt`
3. See examples
4. Read the [documentation](https://dev.lava.ru/). All methods have same names as their urls(`https://api.lava.ru/test/ping` is equal to `Lava.test_ping()` etc.)

## Usage
1. `from aiolava import Lava, LavaError`
2. `client = Lava("your_token")`
3.  See example 
```
ping_result = await client.test_ping()
print(ping_result)

all_wallets = await client.wallet_list()
print(all_wallets)
```
## Exception handling
[See error codes](https://dev.lava.ru/errors)
```
from aiolava import Lava, LavaError

client = Lava(token)
try:
	all_wallets = await client.wallet_list()
	all_transfers = await client.transactions_list(
		transfer_type='transfer',
		account=all_wallets[0].get('account'),
	)
	print(all_transfers)
except LavaError as e:
	print(e)
```
`> {'status': 'error', 'message': 'Invalid token', 'code': 5}`
