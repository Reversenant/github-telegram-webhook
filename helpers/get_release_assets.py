import requests
import logging

class Not200Exception(Exception):
    pass

def get_release_assets(assets_url: str) -> str:
    result = ""
    try:
        r = requests.get(assets_url)
        if r.status_code != 200:
            raise Not200Exception("Can not get assets by assets_url")
        assets = r.json()
        for asset in assets:
            browser_download_url = asset['browser_download_url']
            asset_name = asset['name']
            result += f'<a href="{browser_download_url}">{asset_name}</a>\n'
    except Exception as e:
        logging.error(f"Can't find assets for release: {e}")
    return result
