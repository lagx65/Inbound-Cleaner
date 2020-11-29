import requests
assetids = []
tradeids = []
invalid = []
partneritems = []
valid = []
losses = []
wins = []
ties = []
pages = []
print('')
print(' _______________________________________________________ ')
print('|                                                       |')
print('|             Inbound Cleaner by Lagx#0001              |')
print('|                                                       |')
print(' ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾ ')
print('')
g = input('Enter your cookie: ')
print('')
id1 = input('Enter your userid: ')
print('')
cookies = {'.ROBLOSECURITY': g}
c = requests.Session()
c.cookies['.ROBLOSECURITY'] = g
csrftoken = c.post('https://catalog.roblox.com/v1/catalog/items/details').headers['x-csrf-token']
def getlims(id):
    r = requests.get(f"https://inventory.roblox.com/v1/users/{id}/assets/collectibles?sortOrder=Asc&limit=100").json()['data']
    for item in r:
        assetids.append(item['assetId'])

def getpages():
    headers = {'X-CSRF-TOKEN': csrftoken}
    nextpage = requests.get(f"https://trades.roblox.com/v1/trades/Inbound?sortOrder=Asc&limit=100", cookies=cookies, headers=headers).json()['nextPageCursor']
    pages.append(nextpage)
    if nextpage != None:
        for i in pages:
            if i != None:
                nextpage = requests.get(f"https://trades.roblox.com/v1/trades/Inbound?sortOrder=Asc&limit=100&cursor={i}", cookies=cookies, headers=headers).json()['nextPageCursor']
                pages.append(nextpage)
            else:
                del pages[-1] 

def getinbound():
    headers = {'X-CSRF-TOKEN': csrftoken}
    r = requests.get(f"https://trades.roblox.com/v1/trades/Inbound?sortOrder=Asc&limit=100", cookies=cookies, headers=headers).json()['data']
    for item in r:
            tradeids.append(item['id'])
    if pages[0] != None:
        for i in pages:
            r = requests.get(f"https://trades.roblox.com/v1/trades/Inbound?sortOrder=Asc&limit=100&cursor={i}", cookies=cookies, headers=headers).json()['data']
            for item in r:
                tradeids.append(item['id'])
    print(f"Finished fetching all {len(tradeids)} inbound trades. Now searching for any invalid trades...")
    print('')
        
def checktrades():
    filtered_assetids = list(dict.fromkeys(assetids))
    headers = {'X-CSRF-TOKEN': csrftoken}
    for x in tradeids:
        try:
            r = requests.get(f"https://trades.roblox.com/v1/trades/{x}", cookies=cookies, headers=headers).json()['offers']
            partner = requests.get(f"https://trades.roblox.com/v1/trades/{x}", cookies=cookies, headers=headers).json()['offers'][0]['user']['id']
            pitems = requests.get(f"https://inventory.roblox.com/v1/users/{partner}/assets/collectibles?sortOrder=Asc&limit=100").json()['data']
            for px in pitems:
                partneritems.append(px['assetId'])
            filtered_partneritems = list(dict.fromkeys(partneritems))
            for i in range(len(r[1]['userAssets'])):
                if r[1]['userAssets'][i]['assetId'] not in filtered_assetids:
                    print("Trade with user " + r[0]['user']['displayName'] + " is invalid as you no longer own the item " + r[1]['userAssets'][i]['name'])
                    invalid.append(x)
                else:
                    valid.append(x)
            for i in range(len(r[0]['userAssets'])):
                if r[0]['userAssets'][i]['assetId'] not in filtered_partneritems:
                    print("Trade with user " + r[0]['user']['displayName'] + " is invalid as they no longer own the item " + r[0]['userAssets'][i]['name'])
                    invalid.append(x)
                else:
                    valid.append(x)
            partneritems.clear()
            filtered_partneritems.clear()
        except Exception:
            print("Skipping invalid inbound trade...")

def cancel():
    filtered_invalids = list(dict.fromkeys(invalid))
    print("")
    print(f"Declining {len(filtered_invalids)} invalid trades...")
    for i in filtered_invalids:
        try:
            headers = {'X-CSRF-TOKEN': csrftoken}
            requests.post(f'https://trades.roblox.com/v1/trades/{i}/decline', cookies=cookies, headers=headers)
        except Exception:
            print("")
    assetids.clear()
    tradeids.clear()
    invalid.clear()
    partneritems.clear()
    valid.clear()
    losses.clear()
    wins.clear()
    ties.clear()
    pages.clear()
    filtered_invalids.clear()
    print("")
    print('Now scanning for any new trades...')
    print("")
    main()

data = requests.get("https://www.rolimons.com/itemapi/itemdetails").json()
def calculate():
    filtered_valids = list(dict.fromkeys(valid))
    headers = {'X-CSRF-TOKEN': csrftoken}
    invalid.clear()
    tradeids.clear()
    partneritems.clear()
    for x in filtered_valids:
        offerval = []
        requestval = []
        r = requests.get(f"https://trades.roblox.com/v1/trades/{x}", cookies=cookies, headers=headers).json()['offers']
        for i in range(len(r[0]['userAssets'])):
            if data['items'][str(r[0]['userAssets'][i]['assetId'])][3] != -1:
                offerval.append(data['items'][str(r[0]['userAssets'][i]['assetId'])][3])
        for i in range(len(r[1]['userAssets'])):
            if data['items'][str(r[1]['userAssets'][i]['assetId'])][3] != -1:
                requestval.append(data['items'][str(r[1]['userAssets'][i]['assetId'])][3])
        totaloffer = sum(offerval)
        totalrequest = sum(requestval)
        if totaloffer > totalrequest and totaloffer - totalrequest != 0:
            print("Trade with user " + r[0]['user']['displayName'] + " is a win with a value gain of " + str(totaloffer - totalrequest) + "!")
            wins.append(x)
        if totaloffer < totalrequest and totaloffer - totalrequest != 0:
            print("Trade with user " + r[0]['user']['displayName'] + " is a loss with a value loss of " + str(totaloffer - totalrequest) + "!")
            losses.append(x)
        if totaloffer - totalrequest == 0:
            print("Trade with user " + r[0]['user']['displayName'] + " is an even valued trade!")
            ties.append(x)
        offerval.clear()
        requestval.clear()
    filtered_valids.clear()

def main():
    getlims(id1)
    getpages()
    getinbound()
    checktrades()
    if len(invalid) != 0:
        cancel()
    else:
        filtered_valids = list(dict.fromkeys(valid))
        if len(filtered_valids) != 0:
            print(f"Checking {len(filtered_valids)} valid trades for wins/losses...")
            print('')
            calculate()
            if len(losses) != 0:
                print('')
                print('--------------------------------------------------------')
                print(f"             Total wins in inbound are {len(wins)}!")
                print(f"             Total ties in inbound are {len(ties)}!")
                print(f"            Total losses in inbound are {len(losses)}!")
                print('--------------------------------------------------------')
                print('')
                YN = input(f"Would you like to decline all losses? Y/N: ")
                print('')
                #This is really really bad sorry
                if YN == str('y') or YN == str('Y') or YN == str('N') or YN == str('n'):
                    if YN == str('y') or YN == str('Y'):
                        print("Declining all losses...")
                        for i in losses:
                            try:
                                headers = {'X-CSRF-TOKEN': csrftoken}
                                requests.post(f'https://trades.roblox.com/v1/trades/{i}/decline', cookies=cookies, headers=headers)
                            except Exception:
                                print("")
                        input("Finished!")
                    if YN == str('N') or YN == str('n'):
                        input("Finished!")
                else:
                    print("Error: Unknown input.")
            else:
                print("No losses in inbound found, how lucky!")
                input("Finished!")
        else:
            print("No invalid trades found!")
            input("Finished!")
main()
