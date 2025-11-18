

import requests
from . import _internals

from typing import List,Union


def get_agents():
    url = "api/v0/agents"
    return _internals.get (url)

def list():
    """
    synonym for get_agents
    """
    return get_agents()
def get_agent_list():
    """
    synonym for get_agents
    """
    return get_agents()

def hire_agent(id:str, *, title:str="", desc:str=""):
    """
    Create an agent given an image ID.
    The id (which is a UUID) is given as the first parameter.
    Optional (but recommended) parameters are title and desc.
    """
    url = f"{_internals._get_api_url_stem()}/api/v0/agent/hire"
    headers = {"Authorization": f"Bearer {_internals._get_api_auth_token()}"}
    body = {
        "template_id":id,
        "instance_title":title.strip(),
        "instance_desc":desc.strip(),
        "short_expiration":True,
    }
    resp = requests.put(url,headers=headers,json=body)
    _internals._handle_api_error(resp)
    new_agent = resp.json()


    url = f"{_internals._get_api_url_stem()}/api/v0/agent/{new_agent["id"]}/activateapionly"
    resp = requests.post(url,headers=headers,json={})
    _internals._handle_api_error(resp)


    return new_agent


def generate_agent_token(id:str, title:str=""):
    """
    Generate and return an authentication token for an agent.
    Note that the returned token is security-sensitive and must be protected.
    There is no ability to retrieve the token string after it has been generated.

    Returns a dict with the new token string in the member "token".
    Be very careful with this function, as it rate-limits the tokens you can create,
    and there is no way to retrieve the token value after this function returns.
    """

    url = f"{_internals._get_api_url_stem()}/api/v0/agent/{id}/token"
    headers = {"Authorization": f"Bearer {_internals._get_api_auth_token()}"}
    body = {
        "title":title.strip(),
    }
    resp = requests.post(url,headers=headers,json=body)
    _internals._handle_api_error(resp)

    new_token = resp.json()
    return new_token




def get_agent_tokens(id:str):
    """
    Returns a list of token metadata for the supplied agent ID.
    """
    url = f"{_internals._get_api_url_stem()}/api/v0/agent/{id}/tokens"
    headers = {"Authorization": f"Bearer {_internals._get_api_auth_token()}"}

    resp = requests.get(url,headers=headers)
    _internals._handle_api_error(resp)

    return resp.json()

def post_agent_sentences(id:str,sentences:Union[List[str],List[bytes]]):
    """
    Send a list of sentences up to the specified agent.
    By batching a number of sentences into a list, this variant can save on network traffic.
    """
    r = []
    for s in sentences:
        if isinstance(s,str):
            r.append(s)
        elif isinstance(s,bytes):
            r.append(s.decode('utf-8',errors='replace'))
        else:
            raise TypeError (f"item must be str or bytes, got {type(s)}")


    r2 = [s.replace("\r\n","\n") for s in r]
    r3 = "\n".join(r2)+"\n"

    url = f"{_internals._get_api_url_stem()}/api/v0/agent/{id}/sentences"
    headers = {
        "Authorization": f"Bearer {_internals._get_api_auth_token()}",
        "Content-type": "application/octet-stream"
    }
    resp = requests.post(url,headers=headers,data=r3)
    _internals._handle_api_error(resp)

    return resp.json()




def post_agent_sentence(id:str,sentence:str):
    """
    Send a single sentence up to the specified agent.
    Compared to post_agent_sentences, this variant can send sentences with embedded newlines.
    """

    s2 = sentence.replace("\r\n","\n")

    url = f"{_internals._get_api_url_stem()}/api/v0/agent/{id}/sentence"
    headers = {
        "Authorization": f"Bearer {_internals._get_api_auth_token()}",
        "Content-type": "application/octet-stream"
    }
    resp = requests.post(url,headers=headers,data=s2)
    _internals._handle_api_error(resp)

    return resp.json()



class Agent:
    def __init__(self):
        print ("hello")





def post_sentence(sentence:str):
    """
    Send a single sentence up to an agent which is identified by the agent token
    specified in the runtime (which can be config file, environment, or programmatic).
    This supports high-security environments where only the agent token is available,
    by intentionally avoiding the need for an agent id or a principal-auth token.
    """
    #url = f"{_internals._get_api_url_stem()}/api/v0/agent/{id}/sentence"
    url = "api/v0/agent/sentence"
    s2 = sentence.replace("\r\n","\n")
    return _internals.post (url=url, content_type="application/octet-stream", data=s2.encode('utf-8'))

def post_sentences(sentences:Union[List[str],List[bytes]]):
    """
    Send a list of sentences up to an agent which is identified by the agent token
    specified in the runtime.
    """
    r = []
    for s in sentences:
        if isinstance(s,str):
            r.append(s)
        elif isinstance(s,bytes):
            r.append(s.decode('utf-8',errors='replace'))
        else:
            raise TypeError (f"item must be str or bytes, got {type(s)}")

    r2 = [s.replace("\r\n","\n") for s in r]
    r3 = "\n".join(r2)+"\n"

    url = "api/v0/agent/sentences"
    return _internals.post(url=url,data=r3.encode('utf-8'),content_type="application/octet-stream")

