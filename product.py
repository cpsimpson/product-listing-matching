import json
import re
from collections import defaultdict, namedtuple


ProductMatch = namedtuple('ProductMatch', ['quality', 'product'])


class ProductMatchList(object):
    def __init__(self):
        self._matches = []

    def add_match(self, match_quality, product):
        self._matches.append(ProductMatch(match_quality, product))

    def best_match(self):
        if len(self._matches) > 1:
            self._matches.sort(key=lambda match: match.quality, reverse=True)

        if len(self._matches) > 0:
            return self._matches[0].product

        return None


class ListingProcessor(object):
    def __init__(self):
        self.products = defaultdict(list)

    def load_products(self, filename):
        with open(filename) as f:
            for line in f.readlines():
                product_data = json.loads(line)
                product = Product.create_from_dict(product_data)
                self.products[product.manufacturer].append(product)

    def process_listings(self, filename):
        matches = 0

        with open(filename) as f:
            for line in f.readlines():
                listing = json.loads(line)

                matched = self.process_listing(listing)
                if matched:
                    matches += 1

    def process_listing(self, listing):
        title = listing.get("title", "")
        manufacturer = listing.get("manufacturer", "")

        potential_matches = ProductMatchList()
        for product in self.products[manufacturer]:

            match_quality = product.calculate_match_quality(title)
            if match_quality > 0:
                potential_matches.add_match(match_quality, product)

        best_product_match = potential_matches.best_match()
        if best_product_match:
            best_product_match.add_listing(listing)
            return True

        return False

    def store_results(self, filename):
        with open(filename, "w") as out_file:

            # handle iteritems being removed in Python 3.
            if hasattr(self.products, "iteritems"):
                products_by_manufacturer = self.products.iteritems()
            else:
                products_by_manufacturer = self.products.items()

            for manufacturer, products in products_by_manufacturer:
                out_file.writelines(
                    [
                        "{}\n".format(
                            product.serialize_listings()
                        ) for product in products
                        ]
                )


class Product(object):
    def __init__(self, name, manufacturer, model, family):
        self._name = name
        self._manufacturer = manufacturer
        self._model = model
        self._family = family
        self._listings = []

    @property
    def name(self):
        return self._name

    @property
    def manufacturer(self):
        return self._manufacturer

    def calculate_match_quality(self, title):
        """Assumes you have already done a manufacture match."""

        match_quality = 0

        if self._verify_model_match(title):
            match_quality += 1
        else:
            return 0

        if self._verify_family_match(title):
            if self._family:
                match_quality += 1

            if self._verify_name_match(title):
                match_quality += len(self.name)
        else:
            return 0

        return match_quality

    def _verify_model_match(self, title):
        model_match = re.search("\s{}\s".format(self._model), title)
        if model_match:
            accessory_match = re.search(
                "for.*\s{}\s".format(self._model), title
            )
            if not accessory_match:
                return True
        return False

    def _verify_family_match(self, title):
        if self._family:
            return re.search("\s{}\s".format(self._family), title)
        else:
            return True

    def _verify_name_match(self, title):
        split_name = self._split_name()
        return re.search(
                "\s{}\s".format(split_name), title)

    def _split_name(self):
        return " ".join(re.split("_", self._name))

    def serialize_listings(self):
        return json.dumps(
            {
                "product_name": self.name,
                "listings": self._listings
            }
        )

    def add_listing(self, listing):
        self._listings.append(listing)

    @classmethod
    def create_from_dict(cls, item):
        name = item.get("product_name", "unknown")
        manufacturer = item.get("manufacturer", "unknown")
        model = item.get("model", "unknown")
        family = item.get("family", None)

        product = Product(name, manufacturer, model, family)
        return product

