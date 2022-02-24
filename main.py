from ip2geotools.databases.noncommercial import DbIpCity
from solana.rpc.api import Client
import socket
import time


## returns [hostname, ip address, city, country, latency]
def ping(hostname: str) -> list:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        start = time.time()
        s.connect((hostname, 80))
        latency = (time.time() - start) * 1000
        s.close()

    ip = socket.gethostbyname(hostname)
    geo = DbIpCity.get(ip, api_key="free")
    return [hostname, ip, geo.city, geo.country, round(latency,2)]


## returns {pubkey: # slots scheduled in current epoch}
def get_leaders(rpc_url="https://solana-api.projectserum.com") -> dict:
    c = Client(rpc_url)
    leaders = {}
    for k, v in c.get_leader_schedule()['result'].items():
        leaders.update({k: len(v)})

    return leaders


## returns a sorted list of tuples (id, # slots) by asc. slot count
def sort_leaders(leaders: dict) -> list:
    # first transform the dict into a list of tuples
    l2 = []
    for k, v in leaders.items():
        t: tuple = (k, v)
        l2.append(t)

    l2.sort(key = lambda n: n[1], reverse=True)
    return l2


## returns a dictionary of cluster nodes {ID : (gossip, tpu, rpc)}
def get_cluster(rpc_url="https://solana-api.projectserum.com") -> dict:
    c = Client(rpc_url)
    validators = {}
    for e in c.get_cluster_nodes()['result']:
        validators.update({ e['pubkey'] : (e.get('gossip'), e.get('tpu'), e.get('rpc'))})

    return validators


## show top 10 validator pubkeys, IP addrs (gossip, tpu, rpc), and geolocation
def doxx_nodes_verbose(rpc_url="https://solana-api.projectserum.com"):
    leaders = sort_leaders(get_leaders())[:10]
    nodes = get_cluster()
    for machine in leaders:
        endpoints = nodes.get(machine[0])
        for addr in endpoints:
            if addr is not None:
                ip = addr.split(":")[0]
                try:
                    res = ping(ip)
                    print(f"{machine}::{ip}:\t\t{res}")
                except socket.gaierror:
                    pass
 
## same as above but only caring about the TPU endpoint, and if RPC is avail
def doxx_nodes(rpc_url="https://solana-api.projectserum.com"):
    leaders = sort_leaders(get_leaders())
    nodes = get_cluster()
    for machine in leaders:
        pubkey = machine[0]
        addrs = nodes.get(pubkey) # gossip, tpu, rpc
        tpu = addrs[1]
        ip = tpu.split(":")[0]
        geo = ping(ip)

        print(f"{pubkey : <35}\tTPU:{tpu: <20} ({geo[2]}, {geo[3]} {geo[4]}ms)")
 


## pprint helper function 
def pprint(i):
    for item in i:
        print(item)


doxx_nodes()
    # x = get_leaders()
    # print(x)
    # pprint(sort_leaders(x))
    # print(get_cluster())
    # print(ping('1.1.1.1'))






