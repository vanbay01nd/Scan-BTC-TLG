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

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def eth_balance(addr: str, session: requests.Session) -> float:
    url = f"https://ethereum.atomicwallet.io/api/v2/address/{addr}"
    try:
        req = session.get(url).json()
        ret = req['balance']
        return int(ret) / 1e18
    except (KeyError, requests.RequestException) as e:
        print(f"Error fetching Ethereum balance: {e}")
        return 0.0

def btc_balance(addr: str, session: requests.Session) -> float:
    url = f"https://bitcoin.atomicwallet.io/api/v2/address/{addr}"
    try:
        req = session.get(url).json()
        ret = req['balance']
        return int(ret) / 1e8
    except (KeyError, requests.RequestException) as e:
        print(f"Error fetching Bitcoin balance: {e}")
        return 0.0

def check_wallet(private_key):
    session = requests.Session()
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

    btc_balances = {}
    for addr_type, addr in btc_addrs.items():
        btc_balances[addr_type] = btc_balance(addr, session)
    eth_balance_value = eth_balance(eth_addr, session)

    return private_key, btc_addrs, eth_addr, btc_balances, eth_balance_value

def main():
    clear_screen()
    title()
    print(Fore.GREEN + "Starting..." + Fore.RESET)
    time.sleep(2)

    total_scans = 0
    found_wallets = 0

    max_workers = 7  # Chỉ định 7 luồng

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        try:
            while True:
                private_key = "".join(random.choice("0123456789abcdef") for _ in range(64))
                futures.append(executor.submit(check_wallet, private_key))

                for future in as_completed(futures):
                    clear_screen()
                    title()
                    total_scans += 1

                    private_key, btc_addrs, eth_addr, btc_balances, eth_balance_value = future.result()

                    print(Fore.YELLOW + "Discord: cr0mbleonthegame" + Fore.RESET)
                    print(f"Scan: {total_scans} Found: {found_wallets}\n")

                    for addr_type, addr in btc_addrs.items():
                        btc_balance = btc_balances.get(addr_type, 0.0)
                        print(f"{Fore.WHITE}BTC Address ({addr_type}) | BAL: {Fore.MAGENTA}{btc_balance} | {Fore.YELLOW}{addr}")

                    print(f"{Fore.WHITE}ETH Address (ETH)    | BAL: {Fore.MAGENTA}{eth_balance_value} | {Fore.YELLOW}{eth_addr}")
                    print(f"{Fore.WHITE}Private Key (HEX)    | {Fore.MAGENTA}{private_key}")
                    print("=" * 70)

                    if any(balance > 0 for balance in btc_balances.values()) or eth_balance_value > 0:
                        found_wallets += 1
                        with open('found_wallets.txt', 'a') as f:
                            f.write(f'Scan: {total_scans}, Found: {found_wallets}\n')
                            for addr_type, addr in btc_addrs.items():
                                btc_balance = btc_balances.get(addr_type, 0.0)
                                if btc_balance > 0:
                                    f.write(f'BTC Address ({addr_type}): {addr}\nBalance: {btc_balance}\n')
                            if eth_balance_value > 0:
                                f.write(f'ETH Address: {eth_addr}\nBalance: {eth_balance_value}\n')
                            f.write(f'Private Key: {private_key}\n\n')

                    futures = [f for f in futures if not f.done()]

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Restarting in 5 seconds...")
            time.sleep(5)
            main()

if __name__ == "__main__":
    main()
