# anvi_bodycare_bot
Telegram bot name: @anvi_bodycare_bot


ANVI Bodycare Bot is your personal assistant for all things ANVI. Discover a world of natural skincare and wellness products right at your fingertips. Whether you're looking for information about our products or seek self-care tips and advice, our bot is here to assist you 24/7.

## Local run
You need to specify ANVI_BOT_TOKEN environment variable to run it locally

# parser feature
This parser is created to extract product data (names, URLs, prices, and cover image URLs) from a website.

It works exclusively with the following URL: https://www.anvibodycare.com/shop.

## Requirements

To run this parser, the following libraries:

- requests
- beautifulsoup4

You can install them using `pip install -r requirements.txt`

# product_parser
This parcer is created to extract these details about all existing products in the shop and present them in a .json file:
- product name
- description
- prices
- packaging options
- weight/volume options
- additional information.

If any of the values in the data are empty - the information about the product does not exist.

Works only with https://www.anvibodycare.com/shop

## Requirements
To run, install the following libraries:

- requests
- bs4
- cachetools

You can install them using `pip install -r requirements.txt`
