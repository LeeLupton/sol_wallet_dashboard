from flask import Flask, render_template
import requests

app = Flask(__name__)

# Wallet addresses
wallets = {
    "Photon Wallet": "your_photon_wallet_address",
    "Phantom Wallet": "your_phantom_wallet_address",
    "Exodus Wallet": "your_exodus_wallet_address",
    "Odinbot Wallet": "your_odinbot_wallet_address",
    "Coinbase Wallet": "your_coinbase_wallet_address",
    "Robinhood Wallet": "your_robinhood_wallet_address",
}

def fetch_sol_balance(address):
    """Fetch SOL balance for a given wallet address using Solana API."""
    url = f"https://api.mainnet-beta.solana.com"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [address]
    }
    response = requests.post(url, json=payload).json()
    return response['result']['value'] / 10**9  # Convert Lamports to SOL

def fetch_spl_tokens(address):
    """Fetch SPL token balances for a given wallet address."""
    url = "https://api.mainnet-beta.solana.com"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            address,
            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},  # SPL Token Program
            {"encoding": "jsonParsed"}
        ]
    }
    response = requests.post(url, json=payload).json()
    token_data = response.get('result', {}).get('value', [])
    
    tokens = []
    for token in token_data:
        token_info = token['account']['data']['parsed']['info']
        mint = token_info['mint']
        balance = int(token_info['tokenAmount']['amount']) / (10 ** int(token_info['tokenAmount']['decimals']))
        tokens.append({"mint": mint, "balance": balance})
    return tokens

def fetch_sol_price():
    """Fetch current SOL price in USD using CoinGecko API."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
    response = requests.get(url).json()
    return response['solana']['usd']

def fetch_token_prices(mints):
    """Fetch prices for SPL tokens using CoinGecko API."""
    url = "https://api.coingecko.com/api/v3/simple/token_price/solana"
    params = {"contract_addresses": ",".join(mints), "vs_currencies": "usd"}
    response = requests.get(url, params=params).json()
    return {mint: response.get(mint, {}).get('usd', 0) for mint in mints}

@app.route('/')
def dashboard():
    sol_price = fetch_sol_price()
    wallet_data = []
    total_sol = 0
    total_usd = 0

    for name, address in wallets.items():
        # Fetch SOL balance
        sol_balance = fetch_sol_balance(address)
        total_sol += sol_balance

        # Fetch SPL tokens
        spl_tokens = fetch_spl_tokens(address)
        mint_addresses = [token['mint'] for token in spl_tokens]
        token_prices = fetch_token_prices(mint_addresses)

        spl_value = 0
        for token in spl_tokens:
            mint = token['mint']
            balance = token['balance']
            token['usd_value'] = balance * token_prices.get(mint, 0)
            spl_value += token['usd_value']

        # Calculate total USD value for this wallet
        wallet_usd_value = (sol_balance * sol_price) + spl_value
        total_usd += wallet_usd_value

        wallet_data.append({
            "name": name,
            "sol": sol_balance,
            "usd": wallet_usd_value,
            "spl_tokens": spl_tokens
        })

    # Add total card
    wallet_data.append({
        "name": "Total",
        "sol": total_sol,
        "usd": total_usd,
        "spl_tokens": []  # No SPL tokens for the total card
    })

    return render_template('dashboard.html', wallets=wallet_data, sol_price=sol_price)

if __name__ == '__main__':
    app.run(debug=True)
