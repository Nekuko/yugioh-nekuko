import csv
import requests


print('Already Used')

response = requests.get('https://db.ygoprodeck.com/api/v7/cardinfo.php')

all_cards = response.json()['data']
exit()

with open('cards.csv', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    header = next(reader)

new_list = []
for card in all_cards:
    if card['type'] == 'Skill Card':
        continue

    for key in ['archetype', 'card_prices', 'banlist_info']:
        if key not in card.keys():
            continue
        card.pop(key)

    if 'card_sets' not in card.keys():
        card['card_sets'] = None

    else:
        for value in card['card_sets']:
            value.pop('set_price')
        new_list.append(card)

with open('cards.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=header)
    writer.writeheader()
    for card in new_list:
        writer.writerow(card)
