import os
import random
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from hdwallet import HDWallet
from hdwallet.symbols import BTC, ETH
from colorama import Fore, init
from pyfiglet import Figlet

init(autoreset=True)

def title():
    f = Figlet(font='standard')
    print(Fore.LIGHTCYAN_EX + f.renderText("Cryptonix") + Fore.RESET)

def get_clear():
    os.system('clear')

def eth_balance(addr: str) -> float:
    url = f"https://ethereum.atomicwallet.io/api/v2/address/{addr}"
    try:
        req = requests.get(url).json()
        ret = req['balance']
        return int(ret) / 1e18
    except (KeyError, requests.RequestException) as e:
        print(f"Error fetching Ethereum balance: {e}")
        return 0.0

def get_balance(addr: str) -> float:
    url = f"https://bitcoin.atomicwallet.io/api/v2/address/{addr}"
    try:
        req = requests.get(url).json()
        ret = req['balance']
        return int(ret) / 1e8
    except (KeyError, requests.RequestException) as e:
        print(f"Error fetching Bitcoin balance: {e}")
        return 0.0

def check_wallet(private_key):
    hd_btc = HDWallet(symbol=BTC)
    hd_eth = HDWallet(symbol=ETH)
    hd_btc.from_private_key(private_key)
    hd_eth.from_private_key(private_key)

    eth_addr = hd_eth.p2pkh_address()
    btc_addrs = {
        "P2PKH": hd_btc.p2pkh_address(),
        "BECH32": hd_btc.p2wpkh_address(),
        "P2WPKH": hd_btc.p2wpkh_in_p2sh_address(),
        "P2WSH": hd_btc.p2wsh_in_p2sh_address(),
        "P2SH": hd_btc.p2sh_address()
    }

    balances = {}
    for addr_type, addr in btc_addrs.items():
        balances[addr_type] = get_balance(addr)
    eth_balance_value = eth_balance(eth_addr)
    balances['ETH'] = eth_balance_value

    return private_key, btc_addrs, eth_addr, balances

def main():
    get_clear()
    title()
    print(Fore.GREEN, "Starting...", Fore.RESET)
    time.sleep(2)

    z = 1
    ff = 0

    max_workers = os.cpu_count() * 2  # Adjust the multiplier as needed

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        while True:
            try:
                private_key = "".join(random.choice("0123456789abcdef") for _ in range(64))
                futures.append(executor.submit(check_wallet, private_key))

                for future in as_completed(futures):
                    private_key, btc_addrs, eth_addr, balances = future.result()

                    get_clear()
                    title()

                    print(Fore.YELLOW, "Discord: cr0mbleonthegame", Fore.RESET)
                    print(f"Scan: {z} Found: {ff}")

                    for addr_type, addr in btc_addrs.items():
                        balance = balances.get(addr_type, 0.0)
                        print(f"{Fore.WHITE}BTC Address ({addr_type}) | BAL: {Fore.MAGENTA}{balance} | {Fore.YELLOW}{addr}")

                    eth_balance_value = balances.get('ETH', 0.0)
                    print(f"{Fore.WHITE}ETH Address (ETH)    | BAL: {Fore.MAGENTA}{eth_balance_value} | {Fore.YELLOW}{eth_addr}")
                    print(f"{Fore.WHITE}Private Key (HEX)    | {Fore.MAGENTA}{private_key}")
                    print("=" * 70)

                    z += 1

                    if any(balance > 0 for balance in balances.values()):
                        ff += 1
                        with open('found_wallets.txt', 'a') as f:
                            f.write(f'Scan: {z-1}, Found: {ff}\n')
                            for addr_type, addr in btc_addrs.items():
                                balance = balances.get(addr_type, 0.0)
                                if balance > 0:
                                    f.write(f'BTC Address ({addr_type}): {addr}\nBalance: {balance}\n')
                            if eth_balance_value > 0:
                                f.write(f'ETH Address: {eth_addr}\nBalance: {eth_balance_value}\n')
                            f.write(f'Private Key: {private_key}\n\n')

                    futures = [f for f in futures if not f.done()]

            except Exception as e:
                print(f"An error occurred: {e}")
                print("Restarting in 5 seconds...")
                time.sleep(5)

if __name__ == "__main__":
    main()
