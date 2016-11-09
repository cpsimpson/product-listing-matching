import argparse
from product import ListingProcessor

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--listings_file", default="data/listings.txt", help="Path to listings file."
    )
    parser.add_argument(
        "--products_file", default="data/products.txt", help="Path to products file."
    )
    parser.add_argument(
        "--results_file", default="results.txt", help="Path to results file."
    )
    args = parser.parse_args()

    loader = ListingProcessor()
    loader.load_products(args.products_file)
    loader.process_listings(args.listings_file)
    loader.store_results(args.results_file)
