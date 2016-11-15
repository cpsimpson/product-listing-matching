#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from product import Product, ListingProcessor


class MatcherTestCase(unittest.TestCase):

    def test_valid_match(self):

        product = Product(
            "Sony_Cyber-shot_DSC-W310", "Sony", "DSC-W310",
            "Cyber-shot"
        )

        actual_result = product.matches(
            "Sony Cyber-shot DSC-W310 - Digital camera - compact - 12.1 Mpix "
            "- optical zoom: 4 x - supported memory: MS Duo, SD, MS PRO Duo, "
            "MS PRO Duo Mark2, SDHC, MS PRO-HG Duo - silver"
        )

        self.assertTrue(actual_result, "Listing should match.")

    def test_valid_match_no_family(self):

        product = Product(
            "Sony_Cyber-shot_DSC-W310", "Sony", "DSC-W310",
            None
        )

        actual_result = product.matches(
            "Sony Cyber-shot DSC-W310 - Digital camera - compact - 12.1 Mpix "
            "- optical zoom: 4 x - supported memory: MS Duo, SD, MS PRO Duo, "
            "MS PRO Duo Mark2, SDHC, MS PRO-HG Duo - silver"
        )

        self.assertTrue(actual_result, "Listing should match.")

    def test_no_match_model_is_substring(self):
        product = Product(
            "Nikon_Coolpix_100", "Nikon", "100", "Coolpix"
        )

        actual_result = product.matches(
            "NIKON Coolpix S5100 - rose éclatant"
        )

        self.assertFalse(actual_result, "Listing should not match.")

    def test_no_match_family_is_substring(self):
        product = Product(
            "Nikon_Coolpix_100", "Nikon", "S5100", "pix"
        )

        actual_result = product.matches(
            "NIKON Coolpix S5100 - rose éclatant"
        )

        self.assertFalse(actual_result, "Listing should not match.")

    def test_accessories_no_match(self):
        title = "Nikon 85mm f/3.5 G VR AF-S DX ED Micro-Nikkor Lens + " \
                "UV Filter + Accessory Kit for Nikon D300s, D300, D40, D60, " \
                "D5000, D7000, D90, D3000 & D3100 Digital SLR Cameras"

        product_d3000 = Product.create_from_dict(
            {"product_name": "Nikon_D3000", "manufacturer": "Nikon",
             "model": "D3000",
             "announced-date": "2009-07-29T20:00:00.000-04:00"}
        )

        product_d3100 = Product.create_from_dict(
            {"product_name": "Nikon_D3100", "manufacturer": "Nikon",
             "model": "D3100",
             "announced-date": "2010-08-18T20:00:00.000-04:00"}
        )

        self.assertFalse(product_d3000.matches(title))
        self.assertFalse(product_d3100.matches(title))

    def test_product_create_from_dictionary_values_set(self):
        product = Product.create_from_dict(
            {
                "product_name": "Panasonic_Lumix_DMC-ZS1",
                "manufacturer": "Panasonic",
                "model": "DMC-ZS1",
                "family": "Lumix",
                "announced-date": "2009-01-26T19:00:00.000-05:00"
            }
        )

        self.assertEqual(product._name, "Panasonic_Lumix_DMC-ZS1")
        self.assertEqual(product._manufacturer, "Panasonic")
        self.assertEqual(product._model, "DMC-ZS1")
        self.assertEqual(product._family, "Lumix")

    def test_product_create_from_dictionary_no_family_family_is_none(self):
        product = Product.create_from_dict(
            {
                "product_name": "Samsung_TL205",
                "manufacturer": "Samsung",
                "model": "TL205",
                "announced-date": "2010-01-05T19:00:00.000-05:00"
            }
        )

        self.assertIsNone(product._family, "Family should be None")


class ListingProcessorTestCase(unittest.TestCase):

    def test_single_match(self):
        processor = ListingProcessor()

        listing = {
            "title": "Sony Cyber-shot DSC-W310 - Digital camera - compact - "
                     "12.1 Mpix - optical zoom: 4 x - supported memory: "
                     "MS Duo, SD, MS PRO Duo, MS PRO Duo Mark2, SDHC, "
                     "MS PRO-HG Duo - silver",
            "manufacturer": "Sony",
            "currency": "USD",
            "price": "108.75"
        }

        w310 = Product.create_from_dict(
                    {
                        "product_name": "Sony_Cyber-shot_DSC-W310",
                        "manufacturer": "Sony", "model": "DSC-W310",
                        "family": "Cyber-shot",
                        "announced-date": "2010-01-06T19:00:00.000-05:00"
                    }
                )

        wx5 = Product.create_from_dict(
                    {
                        "product_name": "Sony_Cyber-shot_DSC-WX5",
                        "manufacturer": "Sony", "model": "DSC-WX5",
                        "family": "Cyber-shot",
                        "announced-date": "2010-07-07T20:00:00.000-04:00"
                    }
                )
        processor.products = {
            "Sony": [w310, wx5]
        }
        match = processor.process_listing(listing)

        self.assertTrue(match)
        self.assertEqual(len(wx5._listings), 0)
        self.assertEqual(len(w310._listings), 1)
        self.assertDictEqual(w310._listings[0], listing)

    def test_better_match_with_family_and_model(self):
        without_family = Product.create_from_dict(
            {
                "product_name": "Leica_Digilux",
                "manufacturer": "Leica",
                "model": "Digilux",
                "announced-date": "1998-09-15T20:00:00.000-04:00"
            }
        )
        with_family = Product.create_from_dict(
            {
                "product_name": "Leica_Digilux_4.3",
                "manufacturer": "Leica",
                "model": "4.3",
                "family": "Digilux",
                "announced-date": "2000-08-31T20:00:00.000-04:00"
            }
        )

        listing = {
            "title": "Leica Digilux 4.3 2.4MP Digital Camera w/ 3x Optical "
                     "Zoom",
            "manufacturer": "Leica",
            "currency": "USD",
            "price": "225.00"
        }

        processor = ListingProcessor()

        processor.products = {
            "Leica": [without_family, with_family]
        }
        match = processor.process_listing(listing)

        self.assertTrue(match)
        self.assertEqual(len(without_family._listings), 0)
        self.assertEqual(len(with_family._listings), 1)
        self.assertDictEqual(with_family._listings[0], listing)

    def test_better_match_with_longer_model(self):
        longer_model = Product.create_from_dict(
            {
                "product_name": "Pentax-WG-1-GPS",
                "manufacturer": "Pentax",
                "model": "WG-1 GPS",
                "family": "Optio",
                "announced-date": "2011-02-06T19:00:00.000-05:00"
            }
        )
        shorter_model = Product.create_from_dict(
            {
                "product_name": "Pentax-WG-1",
                "manufacturer": "Pentax",
                "model": "WG-1",
                "family": "Optio",
                "announced-date": "2011-02-06T19:00:00.000-05:00"
            }
        )

        listing = {
            "title": "PENTAX Optio WG-1 GPS - gris",
            "manufacturer": "Pentax",
            "currency": "EUR",
            "price": "421.99"
        }

        processor = ListingProcessor()

        processor.products = {
            "Pentax": [longer_model, shorter_model]
        }
        match = processor.process_listing(listing)

        self.assertTrue(match)
        self.assertEqual(len(shorter_model._listings), 0)
        self.assertEqual(len(longer_model._listings), 1)
        self.assertDictEqual(longer_model._listings[0], listing)

    def test_duplicate_products_listing_to_first(self):
        product_1 = Product.create_from_dict(
            {
                "product_name": "Samsung-SL202",
                "manufacturer": "Samsung",
                "model": "SL202",
                "announced-date": "2009-02-16T19:00:00.000-05:00"
            }
        )
        product_2 = Product.create_from_dict(
            {
                "product_name": "Samsung_SL202",
                "manufacturer": "Samsung",
                "model": "SL202",
                "announced-date": "2009-02-16T19:00:00.000-05:00"
            }
        )

        listing = {
            "title": "Samsung SL202 10MP Digital Camera with 3x Optical "
                     "Zoom and 2.7 inch LCD (Black)",
            "manufacturer": "Samsung",
            "currency": "USD",
            "price": "79.99"
        }

        processor = ListingProcessor()

        processor.products = {
            "Samsung": [product_1, product_2]
        }
        match = processor.process_listing(listing)

        self.assertTrue(match)
        self.assertEqual(len(product_2._listings), 0)
        self.assertEqual(len(product_1._listings), 1)
        self.assertDictEqual(product_1._listings[0], listing)

    def test_duplicate_products_listing_to_first_reversed(self):
        product_1 = Product.create_from_dict(
            {
                "product_name": "Samsung-SL202",
                "manufacturer": "Samsung",
                "model": "SL202",
                "announced-date": "2009-02-16T19:00:00.000-05:00"
            }
        )
        product_2 = Product.create_from_dict(
            {
                "product_name": "Samsung_SL202",
                "manufacturer": "Samsung",
                "model": "SL202",
                "announced-date": "2009-02-16T19:00:00.000-05:00"
            }
        )

        listing = {
            "title": "Samsung SL202 10MP Digital Camera with 3x Optical "
                     "Zoom and 2.7 inch LCD (Black)",
            "manufacturer": "Samsung",
            "currency": "USD",
            "price": "79.99"
        }

        reversed_processor = ListingProcessor()

        reversed_processor.products = {
            "Samsung": [product_2, product_1]
        }
        match = reversed_processor.process_listing(listing)

        self.assertTrue(match)
        self.assertEqual(len(product_1._listings), 0)
        self.assertEqual(len(product_2._listings), 1)
        self.assertDictEqual(product_2._listings[0], listing)

    def test_name_as_tie_breaker(self):
        longer_name = Product.create_from_dict(
            {
                "product_name": "Canon_EOS_Rebel_T1i",
                "manufacturer": "Canon",
                "model": "T1i",
                "family": "Rebel",
                "announced-date": "2009-03-24T20:00:00.000-04:00"
            }
        )
        shorter_name = Product.create_from_dict(
            {
                "product_name": "Canon_EOS_500D",
                "manufacturer": "Canon",
                "model": "500D",
                "family": "EOS",
                "announced-date": "2009-03-24T20:00:00.000-04:00"
            }
        )

        listing = {
            "title": "Canon EOS Rebel T1i 500D 15.1 MP Digital SLR Camera "
                     "with Canon EF-S 18-55mm f/3.5-5.6 IS SLR Lens + Tamron "
                     "75-300 f/4-5.6 LD Lens + .42x Wide Angle Lens with "
                     "Macro + +1, +2, +4, +10 4 Piece Macro Close Up Kit + "
                     "16 GB Memory Card + Multi-Coated UV Filter (2) + "
                     "Multi-Coated Polarizer Filter + Digital Slave Flash + "
                     "50 \" Tripod + Deluxe Padded Camera Bag + 6 Piece "
                     "Accessory Kit + 3 Year Warranty Repair Contract",
            "manufacturer": "Canon",
            "currency": "USD",
            "price": "1294.95"
        }

        processor = ListingProcessor()

        processor.products = {
            "Canon": [longer_name, shorter_name]
        }
        match = processor.process_listing(listing)

        self.assertTrue(match)
        self.assertEqual(len(shorter_name._listings), 0)
        self.assertEqual(len(longer_name._listings), 1)
        self.assertDictEqual(longer_name._listings[0], listing)

    def test_name_as_tie_breaker_including_with(self):
        longer_name = Product.create_from_dict(
            {
                "product_name": "Canon_EOS_Rebel_T1i",
                "manufacturer": "Canon",
                "model": "T1i",
                "family": "Rebel",
                "announced-date": "2009-03-24T20:00:00.000-04:00"
            }
        )
        shorter_name = Product.create_from_dict(
            {
                "product_name": "Canon_EOS_500D",
                "manufacturer": "Canon",
                "model": "500D",
                "family": "EOS",
                "announced-date": "2009-03-24T20:00:00.000-04:00"
            }
        )

        listing = {
            "title": "20 Piece All Purpose Kit with Canon EOS Rebel T1i 500D "
                     "15.1 MP Digital SLR Camera (Black Body) + Sigma "
                     "28-300mm f/3.5-6.3 DG IF Macro Aspherical Lens + 8 GB "
                     "Memory Card + Multi-Coated 3 Piece Filter Kit + Premier "
                     "Holster Case + 50\" Tripod + 6 Piece Camera Accessory "
                     "Kit + 3 Year Celltime Warranty Repair Contract",
            "manufacturer": "Canon",
            "currency": "USD",
            "price": "1189.95"
        }

        processor = ListingProcessor()

        processor.products = {
            "Canon": [shorter_name, longer_name]
        }
        match = processor.process_listing(listing)

        self.assertTrue(match)
        self.assertEqual(len(shorter_name._listings), 0)
        self.assertEqual(len(longer_name._listings), 1)
        self.assertDictEqual(longer_name._listings[0], listing)
