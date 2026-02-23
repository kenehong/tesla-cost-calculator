# Tesla Cost Calculator

A single-file interactive calculator for estimating the true out-the-door cost of purchasing a Tesla in Washington State.

## Features

- **Accurate WA State Fees** — Registration, title, EV fees, weight fees, RTA tax (Sound Transit), and luxury tax based on SB 5801 (2025)
- **All Tesla Models** — Model 3, Y, S, X, Cybertruck with current trim pricing (Feb 2026)
- **Compare Up to 3 Vehicles** — Side-by-side comparison with "Best" badge
- **Trade-In Analysis** — Equity calculation, timing insights, 24-month equity projection
- **Current Car Evaluation** — Enter your current loan details to compare keep vs. switch
- **Light/Dark Theme** — System preference detection with manual toggle
- **Mobile Responsive** — Full functionality on all screen sizes

## Fee Breakdown

| Fee | Amount | Source |
|-----|--------|--------|
| Destination & Doc | $1,390 | Included in Tesla price |
| Order Fee | $250 | Included in Tesla price |
| Filing Fee | $12.50 | WA DOL |
| Title Service | $18 | WA DOL (2026) |
| Registration Service | $11 | WA DOL (2026) |
| License Plates | $50 | WA DOL |
| Plate Reflection | $4 | WA DOL |
| Standard Tab | $30 | WA DOL |
| EV Registration | $150 | SB 5801 |
| EV Additional | $50 | SB 5801 |
| EV Electrification | $75 | WA DOL |
| Weight Fee | $38–92 | Model-dependent |
| RTA Tax | 1.1% of MSRP | Sound Transit areas only |
| Luxury Tax | 8% over $100K | Effective Jan 2026 |

## Tech Stack

- Single HTML file — no build step required
- Tailwind CSS v4 (browser CDN)
- Inter + JetBrains Mono fonts
- oklch color system with CSS custom properties
- Vanilla JavaScript with innerHTML rendering + focus restoration

## Usage

Open `index.html` in any modern browser. No server required.

## License

MIT
