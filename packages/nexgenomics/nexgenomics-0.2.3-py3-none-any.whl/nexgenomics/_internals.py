
import os
import configparser
import requests

def _get_api_url_stem():
    # look for config in env
    if a := os.getenv("API_URL_STEM"):
        return a

    # look for config in cwd
    try:
        cfg = configparser.ConfigParser()
        cfgpth = os.path.expanduser("./.nexgenomicsrc")
        cfg.read(cfgpth)
        return cfg["nexgenomics"]["api_url_stem"]
    except:
        pass

    # look for config in home dir
    try:
        cfg = configparser.ConfigParser()
        cfgpth = os.path.expanduser("~/.nexgenomicsrc")
        cfg.read(cfgpth)
        return cfg["nexgenomics"]["api_url_stem"]
    except:
        pass

    # return a default
    return "https://agentstore.nexgenomics.ai"

def _get_api_auth_token():
    # look for config in env
    if a := os.getenv("API_AUTH_TOKEN"):
        return a

    # look for config in cwd
    try:
        cfg = configparser.ConfigParser()
        cfgpth = os.path.expanduser("./.nexgenomicsrc")
        cfg.read(cfgpth)
        return cfg["nexgenomics"]["api_auth_token"]
    except:
        pass

    # look for config in home dir
    try:
        cfg = configparser.ConfigParser()
        cfgpth = os.path.expanduser("~/.nexgenomicsrc")
        cfg.read(cfgpth)
        return cfg["nexgenomics"]["api_auth_token"]
    except:
        pass

    # return a default
    return "not_a_valid_token"

def _handle_api_error(resp):
    if resp.status_code != 200:
        try:
            msg = resp.json()["msg"]
        except:
            msg = ""
        raise Exception (f"status code {resp.status_code} {msg}")



def get(url:str):
    url = f"{_get_api_url_stem()}/{url}"
    headers = {"Authorization": f"Bearer {_get_api_auth_token()}"}
    resp = requests.get(url,headers=headers)
    _handle_api_error(resp)
    return resp.json()


def post(url:str, data:bytes, content_type:str="application/json"):
    url = f"{_get_api_url_stem()}/{url}"
    headers = {
        "Authorization": f"Bearer {_get_api_auth_token()}",
        "Content-type": content_type
    }
    resp = requests.post(url,headers=headers,data=data)
    _handle_api_error(resp)

    return resp.json()

