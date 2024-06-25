from colorama import Fore, init
from hdwallet import HDWallet
from hdwallet.symbols import BTC, ETH
import random
import requests
import os
import time
import platform
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

def save_to_file(data: str, filename: str):
    with open(filename, 'a') as f:
        f.write(data + '\n')

def main():
    get_clear()
    title()
    print(Fore.GREEN, "Starting...", Fore.RESET)
    time.sleep(2)

    z = 1
    ff = 0

    while True:
        try:
            private_key = "".join(random.choice("0123456789abcdef") for _ in range(64))
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
            balances['ETH'] = eth_balance(eth_addr)

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
                data_to_save = ""
                for addr_type, addr in btc_addrs.items():
                    balance = balances.get(addr_type, 0.0)
                    if balance > 0:
                        data_to_save += f'BTC Address ({addr_type}): {addr}\nBalance: {balance}\n'
                if eth_balance_value > 0:
                    data_to_save += f'ETH Address: {eth_addr}\nBalance: {eth_balance_value}\n'
                data_to_save += f'Private Key: {private_key}\n'

                save_to_file(data_to_save, 'found_addresses.txt')

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Restarting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    main()
