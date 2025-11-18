import json
import logging
import os
import sys
from os import getenv
from os.path import join

import certifi
import requests
import yaml

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

_config_file = ".config/.vault/vault.yml"
_home = getenv("HOME")

try:
    _config = yaml.safe_load(open(join(_home, _config_file)))
except (FileNotFoundError, TypeError):
    if not os.path.exists("/etc/vault"):
        os.makedirs("/etc/vault")
    _home = "/etc/vault"
    _config_file = "vault.yml"
    try:
        _config = yaml.safe_load(open(join(_home, _config_file)))
    except FileNotFoundError:
        logging.error(f"No vault configuration found in {_home}")
        sys.exit(1)


def get_secret(id: str):
    """
    :param id: The ID of the secret to retrieve
    :return: a json object with key/value pairs
             or an empty object if the secret retrieval fails

    This method retrieves a secret from a Vault server using the provided ID.
    If the request is successful (status code 200), the method extracts the key-value pairs JSON object.
    If the request fails, the method logs an HTTP error message and returns a n empty json {}.
    """

    # check if data is available in config file
    if id in _config:
        return _config[id]
    else:
        base_url = _config['wixAPI']['url']
        certs = certifi.where()
        # urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        # logging.warning(f"No vault bundle.pem found at {certs} - working insecure !!")

        token = _config['wixAPI']['token']
        headers = {"auth": token}
        uri = _config['wixAPI']['uri']
        url = f"{base_url}{uri}/{id}"
        resp = requests.get(url, headers=headers, verify=certs)
        if resp.status_code == 200:
            content = resp.json()['value']
            if isinstance(content, str):
                secret = content
            else:
                secret = json.loads(resp.json()["value"])
            return secret

        else:
            print(f"http error {resp.status_code}")
            logging.error(f"WIX api error {resp}")
            return {}


def get_user_pwd(id: str) -> tuple:
    """
    :param id: The ID of the secret to retrieve
    :param repo: The name of the secret repository to retrieve the seret from - defaults to 'secret'
    :return: a tuple username, password values if the secrets has such keys, else None, None

    This method retrieves a secret from a Vault server using the provided ID.
    If the request is successful (status code 200), the method extracts the  username and password key value
    if such keys exist.
    If the request fails, the method prints an HTTP error message and returns (None, None).
    """

    # check if data is available in config file
    if id in _config:
        return _config[id]['username'], _config[id]['password']
    else:
        base_url = _config['wixAPI']['url']
        certs = certifi.where()
        token = _config['wixAPI']['token']

        headers = {"auth": token}
        uri = _config['wixAPI']['uri']
        url = f"{base_url}{uri}/{id}"
        resp = requests.get(url, headers=headers, verify=certs)
        if resp.status_code == 200:
            content = resp.json()['value']
            if isinstance(content, str):
                secret = content
            else:
                secret = json.loads(resp.json()["value"])
            if 'username' in secret and 'password' in secret:
                return secret['username'], secret['password']
            else:
                return None, None

        else:
            print(f"http error {resp.status_code}")
            logging.error(f"WIX api error {resp}")
            return None, None


# def list_secret(repo: str = 'secret'):
#     """
#     :param repo: The name of a secret repository to retrieve the secret from - defaults to 'secret'
#     :return: A list containing all items keys from the repository
#
#     """
#
#     base_url = _config['vault']['vault_addr']
#     certs = join(_home, _config['vault']['certs'].replace("~/", ''))
#     token = _config['vault']['token']
#
#     headers = {"X-Vault-Token": token}
#     uri = f"/v1/{repo}/metadata"
#     url = f"{base_url}{uri}"
#     resp = requests.request('LIST', url, headers=headers, verify=certs)
#     if resp.status_code == 200:
#         return resp.json()["data"]["keys"]
#
#     else:
#         print(f"http error {resp.status_code}")
#         logging.error(f"Vault api error {resp}")
#         return None, None


def upd_secret(id: str, data):
    """
    :param id: The ID of the secret to retrieve
    :param data: The data to be uploaded in place of the exitisting one
    :param repo: The name of the repository to retrieve the secret from - defaults to 'secret'
    :return: the response status code from the vault - 200 if successful.

    """

    # check if data is available in config file
    if id in _config:
        _config[id] = data
        with open(join(_home, _config_file), 'w') as fd:
            yaml.safe_dump(_config, fd)
        return 200

    else:
        base_url = _config['wixAPI']['url']
        certs = certifi.where()
        token = _config['wixAPI']['token']

        headers = {"auth": token}
        uri = _config['wixAPI']['uri']
        url = f"{base_url}{uri}"
        data = {'name': id, 'value': data}
        resp = requests.request('PUT', url, headers=headers, json=data, verify=certs)

        if resp.status_code != 200:
            logging.warning(f"WIX update error for {id} with new {data}")
        return None, None
