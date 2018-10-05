import requests

def magnet_to_torrent(magnet_link):
    data = dict(magnet=magnet_link)
    r = requests.post('http://magnet2torrent.com/upload/', data=data,
                      allow_redirects=False, timeout=2)
    torrent_url = r.headers['Location']
    return torrent_url