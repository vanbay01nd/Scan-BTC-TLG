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
    if 'win' in platform.platform().lower():
        os.system('cls')
    elif 'linux' in platform.platform().lower() or 'darwin' in platform.platform().lower():
        os.system('clear')
    else:
        raise ValueError('Not Supported Platform: "%s"' % platform.platform())

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

            balances = {addr_type: get_balance(addr) for addr_type, addr in btc_addrs.items()}
            eth_balance_value = eth_balance(eth_addr)

            get_clear()
            title()

            print(Fore.YELLOW, "Discord: cr0mbleonthegame", Fore.RESET)
            print(f"Scan: {z} Found: {ff}")

            for addr_type, addr in btc_addrs.items():
                balance = balances[addr_type]
                print(f"{Fore.WHITE}BTC Address ({addr_type}) | BAL: {Fore.MAGENTA}{balance} | {Fore.YELLOW}{addr}")

            print(f"{Fore.WHITE}ETH Address (ETH)    | BAL: {Fore.MAGENTA}{eth_balance_value} | {Fore.YELLOW}{eth_addr}")
            print(f"{Fore.WHITE}Private Key (HEX)    | {Fore.MAGENTA}{private_key}")
            print("=" * 70)

            z += 1  

            if any(balance > 0 for balance in balances.values()) or eth_balance_value > 0:
                ff += 1
                with open('btcWin.txt', 'a') as f:
                    for addr_type, addr in btc_addrs.items():
                        if balances[addr_type] > 0:
                            f.write(f'{addr}\n{private_key}\n')
                    if eth_balance_value > 0:
                        f.write(f'{eth_addr}\n{private_key}\n')

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Restarting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    main()
