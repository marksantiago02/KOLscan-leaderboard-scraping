# KOLscan Leaderboard Scraper

A Python-based web scraper that extracts cryptocurrency trader performance data from KOLscan's leaderboard. This tool automatically collects trader statistics across different time periods (Daily, Weekly, Monthly) and exports the data to CSV format.

## Features

- **Multi-Period Data Collection**: Scrapes leaderboard data for Daily, Weekly, and Monthly periods
- **Comprehensive Trader Profiles**: Extracts wallet information, PnL data, win/loss ratios, and social media handles
- **Robust Error Handling**: Includes retry mechanisms and detailed logging for debugging
- **Headless Browser Support**: Runs efficiently in headless mode for server deployments
- **CSV Export**: Automatically saves collected data to CSV files for analysis
- **Social Media Integration**: Captures associated Twitter and Telegram handles when available

## Data Points Collected

For each trader on the leaderboard, the scraper collects:

- Wallet name and address
- Account name and avatar
- Win/Loss statistics
- Profit & Loss (PnL) in both SOL and USD
- Associated social media accounts (Twitter, Telegram)
- Time period classification

## Prerequisites

- Python 3.7+
- Chrome browser (for ChromeDriver)
- Internet connection

## Installation

1. Clone the repository:
```bash
git clone https://github.com/marksantiago290/KOLscan-leaderboard-scraping.git
cd KOLscan-clone
```

2. Install required dependencies:
```bash
pip install selenium beautifulsoup4 pandas webdriver-manager
```

## Usage

### Basic Usage

Run the scraper with default settings:

```bash
python kolscan.py
```

This will:
- Launch a headless Chrome browser
- Navigate to KOLscan's leaderboard
- Scrape data from all three time periods (Daily, Weekly, Monthly)
- Save results to `kol_leaderboard.csv`
- Generate detailed logs in the `logs/` directory

### Output

The scraper generates:
- **CSV File**: `kol_leaderboard.csv` containing all scraped data
- **Log Files**: Timestamped logs in `logs/` directory for debugging and monitoring
- **Debug Files**: HTML snapshots when errors occur (for troubleshooting)

## Configuration

### Browser Options

The scraper uses Chrome with the following optimizations:
- Headless mode for server deployment
- Disabled GPU acceleration
- Custom window size (1920x1080)
- Anti-detection measures

## Data Structure

The exported CSV contains the following columns:

| Column | Description |
|--------|-------------|
| `period` | Time period in days (1, 7, 30) |
| `wallet_name` | Trader's display name |
| `wallet_address` | Unique wallet identifier |
| `wallet_avatar` | Profile image URL |
| `account_name` | Account display name |
| `win` | Number of winning trades |
| `loss` | Number of losing trades |
| `pnl_usd` | Profit/Loss in USD |
| `pnl_sol` | Profit/Loss in SOL |
| `telegram` | Telegram handle (if available) |
| `twitter` | Twitter handle (if available) |

## Error Handling

The scraper includes robust error handling:
- **Retry Mechanisms**: Multiple selector strategies for clicking elements
- **Graceful Degradation**: Continues scraping other periods if one fails
- **Debug Output**: Saves page source when critical errors occur
- **Detailed Logging**: Comprehensive error tracking and reporting

## Database Integration (Optional)

The code includes commented database integration using Prisma ORM. To enable database storage:

1. Uncomment the Prisma-related code
2. Install Prisma: `pip install prisma`
3. Configure your database schema
4. Replace `save_to_csv()` calls with `save_to_database()`

## Limitations

- Depends on KOLscan's current HTML structure
- Rate limiting may apply for frequent requests
- Requires stable internet connection
- Chrome browser dependency

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## Legal Notice

This tool is for educational and research purposes only. Please ensure compliance with KOLscan's terms of service and applicable laws regarding web scraping. Always respect rate limits and website policies.

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

If you encounter issues or have questions:
1. Check the generated log files for error details
2. Review the debug HTML files if available
3. Open an issue on GitHub with relevant log information

