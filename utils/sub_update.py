#!/usr/bin/env python3

from datetime import datetime
import json
import re
import requests

class update():
    def __init__(self,config={'list_file': './sub/sub_list.json'}):
        self.list_file = config['list_file']
        with open(self.list_file, 'r', encoding='utf-8') as f: # 载入订阅链接
            raw_list = json.load(f)
            self.raw_list = raw_list
        self.update_main()

    #def url_updated(url):  # 判断远程远程链接是否已经更新
     ## s = requests.Session()
      #  s.mount('http://', HTTPAdapter(max_retries=2))
       # s.mount('https://', HTTPAdapter(max_retries=2))
        #try:
         #   resp = s.get(url, timeout=4)
          #  status = resp.status_code
        #except Exception:
         #   status = 404
        #if status == 200:
         #   url_updated = True
        #else:
         #   url_updated = False
        #return url_updated
    
    def url_updated(self,url):
        url_updated = True 
        return url_updated
        
    def update_main(self):
        for sub in self.raw_list:
            id = sub['id']
            current_url = sub['url']
            try:
                if sub['update_method'] != 'auto' and sub['enabled'] == True:
                    print(f'Finding available update for ID{id}')
                    if sub['update_method'] == 'change_date':
                        new_url = self.change_date(id,current_url)
                        if new_url == current_url:
                            print(f'No available update for ID{id}\n')
                        else:
                            sub['url'] = new_url
                            print(f'ID{id} url updated to {new_url}\n')
                    elif sub['update_method'] == 'page_release':
                        new_url = self.find_link(id,current_url)
                        if new_url == current_url:
                            print(f'No available update for ID{id}\n')
                        else:
                            sub['url'] = new_url
                            print(f'ID{id} url updated to {new_url}\n')      
            except KeyError:
                print(f'{id} Url not changed! Please define update method.')
            
            updated_list = json.dumps(self.raw_list, sort_keys=False, indent=2, ensure_ascii=False)
            file = open(self.list_file, 'w', encoding='utf-8')
            file.write(updated_list)
            file.close()


    def change_date(self,id,current_url):
        if id == 36:
            new_url = datetime.today().strftime('https://nodefree.githubrowcontent.com/%Y/%m/%Y%m%d.txt')
        if id == 0:
            new_url = datetime.today().strftime('https://v2rayshare.githubrowcontent.com/%Y/%m/%Y%m%d.txt')
        if id == 1:
            new_url = datetime.today().strftime('https://freenode.me/wp-content/uploads/%Y/%m/%m%d.txt')
        if id == 7:
            new_url = datetime.today().strftime('https://freenode.openrunner.net/uploads/%Y%m%d-v2ray.txt')
        if id == 13:
            new_url = datetime.today().strftime('https://hiclash.com/wp-content/uploads/%Y/%m/%Y%m%d.txt')
        if id == 12:
            new_url = datetime.today().strftime('https://oneclash.githubrowcontent.com/%Y/%m/%Y%m%d.txt')
        if id == 40:
            new_url = datetime.today().strftime('https://www.freeclashnode.com/uploads/%Y/%m/3-%Y%m%d.txt')
        if id == 10:
            new_url = datetime.today().strftime('https://github.com/sharkDoor/vpn-free-nodes/blob/master/node-list/%Y-%m/%d*.md')
        
        if self.url_updated(new_url):
            return new_url
        else:
            return current_url

    def find_link(self,id,current_url):
        if id == 38:
            try:
                res_json = requests.get('https://api.github.com/repos/mianfeifq/share/contents/').json()
                for file in res_json:
                    if file['name'].startswith('data'):
                        return file['download_url'] 
                else:
                    return current_url
            except Exception:
                return current_url
        if id == 33:
            url_update = 'https://v2cross.com/archives/1884'

            if self.url_updated(url_update):
                try:
                    resp = requests.get(url_update, timeout=5)
                    raw_content = resp.text

                    raw_content = raw_content.replace('amp;', '')
                    pattern = re.compile(r'https://shadowshare.v2cross.com/publicserver/servers/temp/\w{16}')
                    
                    new_url = re.findall(pattern, raw_content)[0]
                    return new_url
                except Exception:
                    return current_url
            else:
                return current_url

if __name__ == '__main__':
    update()
