# FireFinance

FireFinance is a **GNOME-oriented GTK4 Libadwaita** application designed to help users manage their personal finances with clarity and ease.

## Purpose
The core goal of FireFinance is to provide a visual way for individuals to track how their wealth evolves over time and identify milestones toward retirement or other long-term financial goals. It emphasizes privacy by ensuring that all data remains on your local machine—**no cloud storage required**.

## Features
*   **Visual Forecasting**: Visualize your wealth growth over several decades to see if you are on track for your goals.
*   **Privacy First**: All data is stored locally. You have full control over your information without any external tracking or cloud syncing.
*   **Crypto-Friendly Integration**: While not exclusively for Bitcoiners, FireFinance includes specific support for:
    *   Bitcoin (BTC) and Stacks (STX) price updates.
    *   Accounting capabilities for these assets.
    *   Option to set BTC as your unit of account for all transactions.
*   **Modern UI**: Built with GTK4 and Libadwaita, providing a native look and feel on the GNOME desktop environment.

## Current Status
⚠️ **Under Construction**: This project is currently in active development. Some features may be incomplete or subject to change.

## Installation (Development)
To build the application from source:
1. Ensure you have the required dependencies for GTK4, Libadwaita, and Python3.
2. Run the following commands:
   ```bash
   meson setup build
   ninja -C build
   ```

## License
This project is licensed under the **MIT License**. See the `COPYING` file for more details.

---
*Designed for people who want to look at their future, not just their past.*
