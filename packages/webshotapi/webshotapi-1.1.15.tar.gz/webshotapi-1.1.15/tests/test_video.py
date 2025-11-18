from webshotapi import Client
import os

def test_video_webm(
    request_client: Client
):
    response = request_client.video({
        "url": "https://example.com",
        "video_format": "webm"
    })
    assert response.status_code == 200
    save_path = '/tmp/screenshot-binary.webm'
    response.save(save_path)

    file_stat = os.stat(save_path)
    assert file_stat.st_size > 30000

def test_video_json(
    request_client: Client
):
    response = request_client.video_json({
        "url": "https://example.com",
    })
    assert len(response['url']) > 0
    assert response['expire_sec'] > 0
