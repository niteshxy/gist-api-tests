import pytest
import json
from helpers.api_client import HttpClient
from configparser import ConfigParser

config = ConfigParser()
config.read('config/config.ini')
base_url = config['github']['base_url']
access_token = config['github']['access_token']
client = HttpClient(base_url, access_token)
gist_payloads = json.load(open('test_data/test_data.json'))

@pytest.fixture
def public_gist():
    payload = gist_payloads['create_public_gist']
    response = client.create_gist(payload)
    assert response.status_code == 201
    gist_id = response.json()['id']
    yield gist_id
    client.delete_gist(gist_id)

@pytest.fixture
def private_gist():
    if not access_token:
        pytest.skip("Skipping private gist tests as no access token is provided.")
    payload = gist_payloads['create_private_gist']
    response = client.create_gist(payload)
    assert response.status_code == 201
    gist_id = response.json()['id']
    yield gist_id
    client.delete_gist(gist_id)

def test_create_public_gist():
    payload = gist_payloads['create_public_gist']
    response = client.create_gist(payload)
    assert response.status_code == 201
    assert response.json()['description'] == payload['description']
    assert response.json()['public'] is True
    assert 'test_file.txt' in response.json()['files']
    assert response.json()['files']['test_file.txt']['content'] == payload['files']['test_file.txt']['content']
    client.delete_gist(response.json()['id'])

@pytest.mark.skipif(not access_token, reason="No access token provided")
def test_create_private_gist():
    payload = gist_payloads['create_private_gist']
    response = client.create_gist(payload)
    assert response.status_code == 201
    assert response.json()['description'] == payload['description']
    assert response.json()['public'] is False
    assert 'test_private_file.txt' in response.json()['files']
    assert response.json()['files']['test_private_file.txt']['content'] == payload['files']['test_private_file.txt']['content']
    client.delete_gist(response.json()['id'])

def test_get_existing_public_gist(public_gist):
    gist_id = public_gist
    response = client.get_gist(gist_id)
    assert response.status_code == 200
    assert response.json()['id'] == gist_id
    assert response.json()['public'] is True

@pytest.mark.skipif(not access_token, reason="No access token provided")
def test_get_existing_private_gist(private_gist):
    gist_id = private_gist
    response = client.get_gist(gist_id)
    assert response.status_code == 200
    assert response.json()['id'] == gist_id
    assert response.json()['public'] is False

def test_get_nonexistent_gist():
    gist_id = "nonexistent_gist_id"
    response = client.get_gist(gist_id)
    assert response.status_code == 404
    assert 'Not Found' in response.json()['message']

@pytest.mark.skipif(not access_token, reason="No access token provided")
def test_update_gist(private_gist):
    gist_id = private_gist
    payload = gist_payloads['update_gist']
    response = client.update_gist(gist_id, payload)
    assert response.status_code == 200
    assert response.json()['description'] == payload['description']
    assert 'test_file.txt' in response.json()['files']
    assert response.json()['files']['test_file.txt']['content'] == payload['files']['test_file.txt']['content']
    assert 'new_file.py' in response.json()['files']
    assert response.json()['files']['new_file.py']['content'] == payload['files']['new_file.py']['content']

@pytest.mark.skipif(not access_token, reason="No access token provided")
def test_delete_gist(private_gist):
    gist_id = private_gist
    response = client.delete_gist(gist_id)
    assert response.status_code == 204
    # Verify deletion by trying to get the gist
    get_response = client.get_gist(gist_id)
    assert get_response.status_code == 404

def test_list_public_gists():
    response = client.list_public_gists()
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.skipif(not access_token, reason="No access token provided")
def test_list_authenticated_user_gists():
    response = client.list_authenticated_user_gists()
    assert response.status_code == 200
    assert isinstance(response.json(), list)