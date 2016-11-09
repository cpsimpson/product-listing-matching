import json
import re
from collections import defaultdict


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

        potential_matches = []
        for product in self.products[manufacturer]:

            match_weight = product.matches(title)
            if match_weight > 0:
                potential_matches.append((match_weight, product))

        if len(potential_matches) > 1:
            potential_matches.sort(key=lambda match: match[0], reverse=True)

        if len(potential_matches) > 0:
            potential_matches[0][1].add_listing(listing)
            return True

        return False

    def store_results(self, filename):
        with open(filename, "w") as out_file:

            if hasattr(self.products, "iteritems"):
                products = self.products.iteritems()
            else:
                products = self.products.items()
            for manufacturer, products in products:
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

    def __repr__(self):
        return self.name

    @property
    def name(self):
        return self._name

    @property
    def manufacturer(self):
        return self._manufacturer

    def matches(self, title):
        """Assumes you have already done a manufacture match."""
        model_match = re.search("\s{}\s".format(self._model), title)
        if model_match:
            accessory_match = re.search(
                "for.*\s{}\s".format(self._model), title
            )
            if not accessory_match:
                if self._family:
                    if re.search("\s{}\s".format(self._family), title):
                        split_name = self._split_name()
                        if re.search(
                                "\s{}\s".format(split_name), title):
                            return 3 + len(self.name)
                        return 2
                else:
                    if re.search(
                            "\s{}\s".format(self._split_name()), title):
                        return 2 + len(self.name)

                    return 1
        return 0

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

