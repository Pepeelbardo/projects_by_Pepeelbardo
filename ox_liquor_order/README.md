# The Ox · Liquor Order

A mobile-first web app that turns a nightly bottle count into a ready-to-send liquor order for **The Ox Bar and Grill**.

Staff count the bottles on the shelf and the app works out what to order, applying the bar's rules. The order is one tap away from the supplier through WhatsApp, text or email.

**Live app:** https://pepeelbardo.github.io/projects_by_Pepeelbardo/ox_liquor_order/

---

## The problem

Putting together a liquor order by hand has three weak points:

- **It depended on who was counting.** Each person had their own idea of "low", so the same stock could produce different orders.
- **Things were forgotten.** Without a full list, an item that wasn't counted simply didn't get ordered.
- **There were special cases to remember.** High-use bottles and items sold only by the case had rules that lived in people's heads.

The app puts those rules in one place, so anyone on shift can produce the same correct order.

## Features

- **Count by bottle.** Use − / + buttons or type the number. The targets are large enough to use one-handed behind the bar.
- **Automatic ordering rule.** When an item is at **3 or fewer**, the app orders enough to bring it back to **5**.
- **Case-only items.** Red Bull and Fever-Tree Tonic Water are ordered as **1 case** instead of a bottle count.
- **High-use reminders.** Tito's and Captain Morgan show a *"Consider ordering a case"* tag.
- **Items not on the list.** Anything that isn't in the catalog can be added by name with a quantity.
- **Progress tracking.** A progress bar shows how many items are counted, and before sending, the app warns about any item that was skipped.
- **Copy or share.** The order is copied as clean text, or sent through the phone's share menu. Only the items being ordered are included.
- **English / Spanish.** One tap switches the whole interface.
- **Nothing gets lost.** The count is saved on the device, so closing the browser mid-count doesn't erase it.
- **Search.** Jump to any item among the 69 in the catalog.

## Ordering rules

| Situation | Counted | What gets ordered |
|---|---|---|
| Standard item | 4 or more | Nothing |
| Standard item | 3 | 2 bottles (to reach 5) |
| Standard item | 0 | 5 bottles |
| Case item (Red Bull, Fever-Tree) | 3 or fewer | 1 case |
| High-use item (Tito's, Captain Morgan) | 3 or fewer | Bottles to reach 5, plus a *"Consider ordering a case"* tag |
| Not on the list | — | The quantity typed in |

Example of a copied order:

```
The Ox Bar and Grill — Liquor order
Thu, Oct 8, 2026 · Counted by: Jose

Tito's: 3 (Consider ordering a case)
Jameson: 2
Red Bull: 1 case

Total: 5 bottles + 1 case
```

## How to use it

1. Open the link on your phone. To use it like an app, choose **Add to Home Screen** from the browser menu.
2. Type your name in **Counted by**.
3. Go through the list and enter the number of bottles for each item.
4. Add anything that isn't on the list under **Other**.
5. Tap **Make order** and check the list.
6. Tap **Copy** or **Share** and send the order to the supplier.
7. Tap **Reset** to start the next count from zero.

## Updating the catalog

All the business data lives at the top of the `<script>` section in `index.html`, so no programming knowledge is needed to maintain it.

**Change the ordering rule for every item:**

```js
const REORDER_AT   = 3;   // order when there are this many or fewer
const STOCK_TARGET = 5;   // fill back up to this number
```

**Add, rename or remove an item.** Each line in `CATALOG` is one product:

```js
{ cat: "Vodka", name: "Grey Goose" },
```

**Optional settings per item:**

```js
{ cat: "Vodka",  name: "Tito's",   caseHint: true },              // shows "Consider ordering a case"
{ cat: "Mixers", name: "Red Bull", byCase: true },                // orders "1 case" instead of bottles
{ cat: "Rum",    name: "Bacardi",  reorderAt: 4, target: 8 },     // its own rule
```

Items are shown in the order they appear in the list and grouped by `cat`. After saving the file and pushing it to GitHub, the live app updates within a minute or two.

## Tech stack

- **HTML, CSS and vanilla JavaScript** in a single file, with no frameworks, build step or dependencies.
- **`localStorage`** keeps the current count on the device.
- **Web Share API** and the **Clipboard API** send the order, with a fallback for older browsers.
- **GitHub Pages** hosts the app for free.

### Design decisions

- **A single static file.** A small bar has no IT staff. One file with no server, database or login costs nothing to host and can't break due to an outdated dependency.
- **Mobile-first.** The count happens standing at the shelf with a phone in one hand, so the layout is built around large tap targets and a fixed action bar.
- **Rules as data.** The ordering logic reads per-item settings (`byCase`, `caseHint`, `reorderAt`) instead of hard-coding product names, so new exceptions are a one-line change.
- **Explicit "not counted" state.** An item left blank is different from an item counted as 0. Blank items are flagged instead of silently ordered or skipped.

## Privacy

Counts stay on the phone that entered them. The app sends no data to any server, and each device keeps its own count.

## Run it locally

```bash
git clone https://github.com/Pepeelbardo/ox-liquor-order.git
cd ox-liquor-order
# open index.html in any browser
```

## Possible next steps

- A shared count across devices, so two people can split the bar.
- Order history to see consumption over time and tune the par levels.
- Supplier-specific case sizes and automatic rounding.

## Author

**Jose Luis Sarabia** · [GitHub](https://github.com/Pepeelbardo) · [LinkedIn](https://www.linkedin.com/in/jlsarabian04/)

Built for The Ox Bar and Grill.
