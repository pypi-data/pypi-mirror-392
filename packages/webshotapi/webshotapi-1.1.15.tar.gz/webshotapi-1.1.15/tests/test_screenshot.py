from webshotapi import Client
import os

def test_screenshot_jpg(
    request_client: Client
):
    response = request_client.screenshot({
        "url": "https://example.com"
    })
    assert response.status_code == 200
    save_path = '/tmp/screenshot.jpg'
    response.save(save_path)

    file_stat = os.stat(save_path)
    assert file_stat.st_size > 20000

def test_screenshot_png(
    request_client: Client
):
    response = request_client.screenshot({
        "url": "https://example.com",
        "image_type": "png",
    })
    assert response.status_code == 200
    save_path = '/tmp/screenshot.png'
    response.save(save_path)

    file_stat = os.stat(save_path)
    assert file_stat.st_size > 15000


def test_screenshot_pdf(
    request_client: Client
):
    response = request_client.pdf({
        "url": "https://example.com",
    })
    assert response.status_code == 200
    save_path = '/tmp/screenshot.pdf'
    response.save(save_path)

    file_stat = os.stat(save_path)
    assert file_stat.st_size > 10000

def test_screenshot_json(
    request_client: Client
):
    response = request_client.screenshot_json({
        "url": "https://example.com",
    })
    assert len(response['url']) > 0
    assert response['expire_sec'] > 0
