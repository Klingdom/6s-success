"""Pull Amazon's own search-suggestion API for the Kindle Store.

This is Amazon's public autocomplete endpoint, the same one that fills the drop
down under the search box. It is evidence of what shoppers actually type. It is
NOT volume data: the API returns an ordered list, not counts, so nothing here
should be reported as a search volume.
"""
import json, sys, time, urllib.parse, urllib.request

SEEDS = sys.argv[1:] or ["declutter"]
BASE = ("https://completion.amazon.com/api/2017/suggestions?"
        "limit=11&prefix={p}&suggestion-type=KEYWORD&page-type=Gateway"
        "&alias=digital-text&site-variant=desktop&mid=ATVPDKIKX0DER"
        "&client-info=amazon-search-ui&lop=en_US")

out = {}
for s in SEEDS:
    url = BASE.format(p=urllib.parse.quote(s))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        data = json.load(urllib.request.urlopen(req, timeout=20))
        out[s] = [x.get("value") for x in data.get("suggestions", [])]
    except Exception as e:
        out[s] = ["ERROR: %s" % e]
    time.sleep(0.4)

for s, v in out.items():
    print("%-28s %s" % (s, " | ".join(v)))
