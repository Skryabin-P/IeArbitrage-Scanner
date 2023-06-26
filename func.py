
def normalize_pair(base_asset:str,quote_asset:str):
    return base_asset.lower()+"_"+quote_asset.lower()


if __name__ == '__main__':
    print(normalize_pair('ETH','USDT'))