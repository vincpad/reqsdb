#%%
from bs4 import BeautifulSoup
import requests

url = 'https://icons.getbootstrap.com/'
r = requests.get(url, allow_redirects=True)
# %%
soup = BeautifulSoup(r.text)

def getSvgCode(link):
    r2 = requests.get(url, allow_redirects=True)
    soup2 = BeautifulSoup(r.text)
    


# %%
links = [l.get("href") for l in soup.findAll('a')]
iconLinks = []
for link in links:
    if link.startswith("/icons/"):
        print(link)



# %%
r2 = requests.get("https://icons.getbootstrap.com/icons/0-circle/", allow_redirects=True)
soup2 = BeautifulSoup(r.text)
# %%
elems = soup2.select('div.highlight:nth-of-type(13) > pre:nth-of-type(1) > code:nth-of-type(1)')
# %%
