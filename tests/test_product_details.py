import unittest
from unittest.mock import patch, Mock
from product_details import extract_weight_options, extract_packaging_options, extract_pricing_options, \
    parse_product_page, extract_product_name


class TestProductParsing(unittest.TestCase):

    @patch('requests.get')
    def test_parse_product_page(self, mock_requests_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><h1 class="product_title">Product Name</h1></body></html>'
        mock_requests_get.return_value = mock_response

        product_details = parse_product_page('https://example.com/product/123')

        self.assertEqual(product_details['product name'], 'Product Name')

    def test_extract_product_name(self):
        fake_soup = Mock()
        fake_product_name_element = Mock()
        fake_product_name_element.text = 'Fake Product Name'
        fake_soup.find.return_value = fake_product_name_element

        product_name = extract_product_name(fake_soup)

        self.assertEqual(product_name, 'Fake Product Name')

    @patch('requests.get')
    def test_extract_weight_options(self, mock_requests_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><select name="attribute_pa_vaha"><option>Виберіть опцію</option><option>100g</option><option>200g</option></select></body></html>'
        mock_requests_get.return_value = mock_response

        weight_options = extract_weight_options('https://example.com/product/123')

        self.assertEqual(weight_options, ['100g', '200g'])

    @patch('requests.get')
    def test_extract_packaging_options(self, mock_requests_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><select name="attribute_pa_pakuvannia"><option>Виберіть опцію</option><option>Option A</option><option>Option B</option></select></body></html>'
        mock_requests_get.return_value = mock_response

        packaging_options = extract_packaging_options('https://example.com/product/123')

        self.assertEqual(packaging_options, ['Option A', 'Option B'])

    @patch('requests.get')
    def test_extract_pricing_options(self, mock_requests_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><span class="woocommerce-Price-amount amount">10.99</span></body></html>'
        mock_requests_get.return_value = mock_response

        pricing_options = extract_pricing_options('https://example.com/product/123')

        self.assertEqual(pricing_options, ['10.99'])


if __name__ == '__main__':
    unittest.main()
