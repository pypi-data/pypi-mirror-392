from webshotapi import Client
import os

def test_info(
    request_client: Client
):
    data = request_client.info()
    assert data['quota_limit'] > 0
    assert data['max_concurrent_requests'] > 0
    assert data['quota_remaining'] > 0

