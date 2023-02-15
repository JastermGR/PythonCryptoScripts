import asyncio
import telegram
import requests
import pprint
from os.path import exists
import time
import signal
import sys

collection_addy = '0x6b02935008c23325b28f17f6281a8456f46fc121'
collection_name = 'Eyeball Gen 0'
base_link ='https://minted.network/collections/cronos/'
token_decimals = 10**18

notify_theshold = 2 #for changes greater than  2%
prev_floor = 0
filename = "EyeballFloor.txt"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://minted.network/',
    'content-type': 'application/json',
    'apollographql-client-name': 'minted-ui-prod',
    'apollographql-client-version': 'current',
    'Origin': 'https://minted.network',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}

json_data = {
    'operationName': 'getCollection',
    'variables': {
        'address': collection_addy,
        'chain': 'CRONOS',
    },
    'query': 'query getCollection($address: EvmAddress!, $chain: Blockchain!) {\n  collection(address: $address, chain: $chain) {\n    ...CollectionDetailFields\n    ...CollectionPriceFields\n    ...CollectionVolumeFields\n    ...CollectionAttributesFields\n    ...CollectionSocialsFields\n    __typename\n  }\n}\n\nfragment CollectionDetailFields on AssetCollection {\n  ...CollectionIdentifyFields\n  name\n  logo {\n    url\n    __typename\n  }\n  banner {\n    url\n    __typename\n  }\n  creator {\n    ...UserFields\n    __typename\n  }\n  description\n  assetCount\n  ownerCount\n  raritySource\n  isRarityEnable\n  highestCollectionOffer\n  __typename\n}\n\nfragment CollectionIdentifyFields on AssetCollection {\n  address\n  name\n  chain {\n    name\n    __typename\n  }\n  status\n  __typename\n}\n\nfragment UserFields on UserAccount {\n  evmAddress\n  name\n  avatar {\n    url\n    __typename\n  }\n  nonce\n  __typename\n}\n\nfragment CollectionPriceFields on AssetCollection {\n  floorPrice {\n    latestFloorPrice\n    change24h\n    latestFloorPriceNative\n    latestGlobalFloorPrice\n    latestGlobalFloorPriceNative\n    __typename\n  }\n  __typename\n}\n\nfragment CollectionVolumeFields on AssetCollection {\n  volume {\n    change24h\n    volume7d\n    volume24h\n    volume30d\n    volumeAll\n    __typename\n  }\n  __typename\n}\n\nfragment CollectionAttributesFields on AssetCollection {\n  attributes {\n    propertyName\n    traits {\n      trait\n      traitValue\n      percentage\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CollectionSocialsFields on AssetCollection {\n  socials {\n    website\n    discord\n    telegram\n    twitter\n    instagram\n    scan\n    __typename\n  }\n  __typename\n}',
}

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)


def readFile():
    file_exists = exists(filename)
    if file_exists:
        f = open(filename,'r')
        collection_addy,floor = f.readline().split('[')
    else:
        floor = 0
    global prev_floor
    #print("Floor is:"+floor)
    prev_floor = float(floor)

def writeFile(price):
    global collection_addy
    file_exists = exists(filename)
    if not file_exists:
        f = open(filename,"x")
    else:
        f = open(filename,'w')
    f.write(collection_addy+"["+str(price))
    f.close()



def snipeFloor():
    global link
    global prev_floor
    response = requests.post('https://api.minted.network/graphql', headers=headers, json=json_data)
    msg = "SAME"
    if response.status_code == 200:
        data = response.json()['data']['collection']
        floor_price_data = data['floorPrice']
        price = float(floor_price_data['latestFloorPriceNative']) / token_decimals
        print(price, "$CRO")
        difference = 0
        if prev_floor != 0:
            difference = (price-prev_floor)/price * 100
            difference = float("{:.1f}".format(difference))
        else:
            difference= 50
        if float(prev_floor) != price and abs(difference) > notify_theshold:
            print("New Floor")
            prev_floor = price
            writeFile(price)
            msg = f"New floor on Collection {collection_name}: {price} $CRO ({difference} %). \nMaximum reward threshold: {2*price} $CRO."
        else:
            print("OLD Floor")
            msg = "SAME"
    else:
        msg = "ERROR"

    return msg


async def main():
    bot = telegram.Bot(XXXXXXX)
    async with bot:
        #print(await bot.get_me())
        #print((await bot.get_updates()))                                    #RUN THIS TO GET CHAT ID
        message = snipeFloor()
        if message != "SAME":
           await bot.send_message(text=message, chat_id=XXXXX)            #ADD THE CHAT ID


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    readFile()
    while(True):
        asyncio.run(main())
        time.sleep(60)
        #t = Timer(30.0, )
        #t.start()  # after 30 seconds, "hello, world" will be printed




