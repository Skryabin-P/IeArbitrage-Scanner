import time
import os

def normalize_pair(base_asset:str,quote_asset:str):
    return base_asset.lower()+"_"+quote_asset.lower()


if __name__ == '__main__':
    from subprocess import call


    print(normalize_pair('ETH','USDT'))
    time.sleep(1)
    call("CLS")
