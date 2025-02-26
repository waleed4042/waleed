import os
import requests
url=requests.get('https://www.youtube.com/watch?v=47ed1664-0d1e-43b7-8440-a14c7fcc5a0a')
r=open('static/waleed.mp4','wb')
r.write(url.content)
r.close()