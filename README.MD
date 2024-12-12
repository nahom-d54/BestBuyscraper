# BestBuy Scraper

This project contains a Python script for web scraping.

## Requirements

- Python 3.x
- `httpx` library
- `beautifulsoup4` library

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/nahom-d54/BestBuyscraper.git
   ```
2. Navigate to the project directory:
   ```sh
   cd scraper
   ```
3. Install the required libraries:
   ```sh
   pip install httpx bs4
   ```

## Usage

1. Run the scraper script:

   ```sh
   python main.py
   ```

2. The script will output the scraped data to a file named `Bestbuy_{parsed_url.query}_{page}.json`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## Contact

For any questions or suggestions, please open an issue or contact the repository owner.
