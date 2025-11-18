from webshotapi import Client

def test_extract(
    request_client: Client
):
    response = request_client.extract({
        'url': "https://example.com",
        'extract_html': True,
        'extract_words': True,
    })

    assert 'This domain is for use in documentation examples without ne' in response['html']
    assert response['words'][0] == {
        'word': 'Example',
        'position': {'x': 384, 'y': 162, 'width': 93, 'height': 39},
        'word_index': 0,
        'xpath': '/html[1]/body[1]/div[1]/h1[1]',
        'offset': 0
    }

