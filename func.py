
def normalize_pair(pair:str):
    return pair.lower().replace('/','').replace('-','')

if __name__ == '__main__':
    print(normalize_pair('ETH-USDT'))