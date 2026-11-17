# ShopList prototype

A clickable web prototype of **ShopList**, a concept for ShopBack: your smart shopping list. Keep track of products you want to buy, get research reports and smart alerts for price drops, and get the best prices and Cashback on everything you buy online. Items are sorted into Buy Now, Wish List and Recurring Purchases, and Karma, the AI shopping assistant, does the legwork.

The screens follow the look of ShopBack’s existing AI assistant flows: chat-style layout, the gradient sparkle, black pill buttons, pastel gradient cards, emoji-led chips and the Figtree typeface.

It is a static site with no build step and no dependencies.

## Flows

1. **Discover and onboard:** ShopBack home icon and promo card, welcome with the tutorial video, onboarding, a blank ShopList with three stacked lists where you pick a list and type to add your first items, capture, coach marks.
2. **Everyday ShopList:** Buy Now details and picks, Wish List and the Cashback Wish Jar, Recurring restock.
3. **Karma does the legwork:** morning briefing, approve, the ShopBack store page, Activate Cashback, bought.
4. **Price Watchlist Update:** daily or weekly price check with the best price after Cashback per store, item detail, settings, notifications.
5. **Save from any store:** the ShopBack browser extension's “Save to ShopList” picker, and how the item lands in the app.
6. **Inside the ShopBack app:** the Notifications inbox with a ShopList filter, and the Account screen with ShopList entries.

Interactive screens: the blank ShopList (pick a list, type to add, move cards between lists), the tutorial video widget, the Daily / Weekly report switch, the report settings and the extension's list picker.

## Matching the ShopBack app

ShopList is designed to live inside the native ShopBack app. The home screen, tab bar, store page, Activate Cashback step, Notifications and Account screens are rebuilt in HTML from the existing ShopBack iOS UI, using screens on Mobbin as reference. ShopList takes the middle tab (the Watchlist slot); Watchlist stays reachable from Account. Store logos are plain coloured tiles, not the real logo artwork.

## How it is built

- `design/*.dc.html` are the screen sources, exported from the design canvas.
- `scripts/build_screens.py` turns them into `screens.js`. Run it after changing a screen:

  ```sh
  python3 scripts/build_screens.py
  ```

- `app.js` renders the screens: `{{holes}}`, `<sc-if>`, `<sc-for>`, `<dc-import>`, click handlers and component state.
- `img/` holds simple product illustrations used in place of photos, and the assistant sparkle.
- `fonts/` holds Figtree (SIL Open Font License, see `fonts/OFL.txt`).

## Run locally

Open `index.html` in a browser, or serve the folder:

```sh
python3 -m http.server 8000
```

## Deploy

Deployed as a static site on Vercel (no framework, no build command, output is the repo root).

## Note

This is a concept prototype, not a ShopBack product. All prices, Cashback rates and caps are samples.
