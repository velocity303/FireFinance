# FireFinance 📊

**FireFinance** is a [GTK4](https://www.gtk.org/) / [Libadwaita](https://libadwaita.org/) application designed to help you visualize and plan your long-term financial future. Built with privacy-first principles in mind, all data stays on your local machine with no cloud storage, no accounts, and no tracking.

## Key Features

### Wealth Projection & Planning
- **Multi-year net worth visualization** — see your projected wealth over decades based on income, assets, expenses, and milestones
- **Milestone tracking** — plan for future large expenses like retirement, education, or major purchases
- **Income & expense management** — track recurring monthly or yearly cash flows with tax modeling

### Finance Modeling
- **Asset tracking** — Cash, crypto (BTC, STX), real estate, retirement accounts
- **Three-tier tax modeling** — Income tax, capital gains tax, and property tax rates
- **Crypto integration** — Real-time Bitcoin and Stacks prices via CoinGecko API
- **BTC as unit of account** — Toggle to view all values in Bitcoin equivalent
- **Real estate depreciation** — Factor in property tax and appreciation rates

### Tax Modeling
- Configurable income tax rate
- Configurable capital gains tax rate
- Configurable property tax rate
- Automatic tax calculations in projections

### Crypto Integration
- Real-time BTC/STX price fetching via CoinGecko API
- No API key required
- Automatic price updates at startup
- BTC as alternative unit of account

### Modern GNOME Integration
- Built with GTK4 + Libadwaita for native GNOME look and feel
- Adaptive UI works on desktop and mobile Linux devices
- GSettings integration for persistent preferences
- D-Bus activation

## Installation

### From Source
Prerequisites: GTK4, Libadwaita, Python3 + PyGObject

```bash
meson setup build
ninja -C build
./build/src/firefinance
```

### Flatpak
```bash
flatpak-builder --force-clean --repo=repo build_dir me.velocitynet.FireFinance.json
flatpak build-bundle repo firefinance.flatpak me.velocitynet.FireFinance
```

## Data Storage
All data is stored locally in `~/.local/share/firefinance/` as JSON configuration. No network requests are made beyond optional real-time crypto prices from CoinGecko. See Settings page for data directory location.

## License

This project is licensed under the MIT License. See LICENSE file for the full text.

---
*Built with privacy-first principles on Linux.*