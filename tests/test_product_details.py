from unittest.mock import patch, Mock
from product_details import get_product_page_links, parse_product_page


@patch('product_details.requests.get')
def test_get_product_page_links_mocked(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b'<a href="product-page-1">Product 1</a><a href="product-page-2">Product 2</a>'
    mock_get.return_value = mock_response

    shop_url = 'https://www.example.com/shop'
    product_page_links = get_product_page_links(shop_url)

    assert isinstance(product_page_links, list)
    assert len(product_page_links) == 2
    assert 'product-page-1' in product_page_links
    assert 'product-page-2' in product_page_links
    mock_get.assert_called_once_with(shop_url)


@patch('product_details.requests.get')
@patch('product_details.BeautifulSoup')
def test_parse_product_page_mocked(mock_soup, mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b'<script type="application/json" id="wix-warmup-data">{"data": "json_data_here"}</script>'
    mock_get.return_value = mock_response

    mock_soup_instance = Mock()
    mock_soup.return_value = mock_soup_instance

    mock_json_loads = Mock()
    mock_json_loads.return_value = {
        'appsWarmupData': {
            '1380b703-ce81-ff05-f115-39571d94dfcd': {
                'productPage_UAH_1': {
                    'catalog': {
                        'product': {
                            'name': 'Product Name',
                            'description': 'Product Description',
                            'productItems': [{'formattedPrice': '10,00₴'}],
                            'options': [{'selections': [{'key': '1'}]}],
                            'additionalInfo': [{'info_data': 'info_value'}]
                        }
                    }
                }
            }
        }
    }

    with patch('product_details.json.loads', mock_json_loads):
        product_info = parse_product_page('https://www.example.com/product-page-1')

    assert isinstance(product_info, dict)
    assert 'product name' in product_info
    assert 'description' in product_info
    assert 'prices' in product_info
    assert 'weight_volume' in product_info
    assert 'packaging' in product_info
    assert 'additional_info' in product_info

    mock_get.assert_called_once_with('https://www.example.com/product-page-1')

    mock_soup.assert_called_once_with(mock_response.content, 'html.parser')
