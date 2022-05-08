from aiolava import Lava, LavaError
import asyncio

token = 'your_token_here'

async def main(token):
    client = Lava(token)

    try:
        ping_result = await client.test_ping()
        print(ping_result)

        all_wallets = await client.wallet_list()
        print(all_wallets)

        all_transfers = await client.transactions_list(
            transfer_type='transfer',
            account=all_wallets[0].get('account'),
        )
        print(all_transfers)
    except LavaError as e:
        print(e)


if __name__ == '__main__':
    asyncio.run(main(token))
