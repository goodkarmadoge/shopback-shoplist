# ShopList prototype

A clickable web prototype of **ShopList**, a concept for ShopBack: one list for everything you plan to buy (To Buy, Recurring and Wishlist), with an agent that watches prices and ShopBack Cashback and asks for your yes.

It is a static site with no build step and no dependencies.

## Flows

1. **Discover and onboard:** ShopBack home icon and promo card, welcome with the tutorial video, onboarding, seeding lists, capture, coach marks.
2. **Everyday ShopList:** three shelves, To Buy details and picks, Recurring restock, Wishlist and the Cashback Wish Jar.
3. **The agent does the legwork:** morning briefing, approve, bought.
4. **Price Watchlist Update:** daily or weekly price check with the best price after Cashback per store, item detail, settings, notifications.
5. **Save from any store:** the ShopBack browser extension's “Save to ShopList” picker, and how the item lands in the app.

Interactive screens: the tutorial video widget, the Daily / Weekly report switch, the report settings and the extension's list picker.

## How it is built

- `design/*.dc.html` are the screen sources, exported from the design canvas.
- `scripts/build_screens.py` turns them into `screens.js`. Run it after changing a screen:

  ```sh
  python3 scripts/build_screens.py
  ```

- `app.js` renders the screens: `{{holes}}`, `<sc-if>`, `<sc-for>`, `<dc-import>`, click handlers and component state.
- `img/` holds simple product illustrations used in place of photos.

## Run locally

Open `index.html` in a browser, or serve the folder:

```sh
python3 -m http.server 8000
```

## Deploy

Deployed as a static site on Vercel (no framework, no build command, output is the repo root).

## Note

This is a concept prototype, not a ShopBack product. All prices, Cashback rates and caps are samples.
