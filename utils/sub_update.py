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
     # s = requests.Session()
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
                    elif sub['update_method'] == 'update_airports':
                                new_url = update_url.update_airports(
                                    id, current_url)
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


    def update_airports(id, current_url):
        if id == 17:
            # try:
            s = requests.Session()
            s.mount('http://', HTTPAdapter(max_retries=2))
            s.mount('https://', HTTPAdapter(max_retries=2))
            # sublist = list(set(list(filter(lambda x: x != "" and str(x).startswith("http"), s.get(
            #     'https://raw.githubusercontent.com/RenaLio/Mux2sub/main/sub_list', timeout=4).text.split("\n")))))

            # air_free = list(set(list(filter(lambda x: x != "" and str(x).startswith("http"), s.get(
            #     'https://raw.githubusercontent.com/rxsweet/proxies/main/sub/sources/sublist_mining.txt', timeout=4).text.split("\n")))))
            # air_mining = list(set(list(filter(lambda x: x != "" and str(x).startswith("http"), s.get(
            #     'https://raw.githubusercontent.com/rxsweet/proxies/main/sub/sources/subList_dynamic.txt', timeout=4).text.split("\n")))))

            # air_free1 = list(set(list(filter(lambda x: x != "" and str(x).startswith("http"), s.get(
            #     'https://raw.githubusercontent.com/cdddbc/getAirport/main/config/sublist_free', timeout=4).text.split("\n")))))
            # air_mining1 = list(set(list(filter(lambda x: x != "" and str(x).startswith("http"), s.get(
            #     'https://raw.githubusercontent.com/cdddbc/getAirport/main/config/sublist_mining', timeout=4).text.split("\n")))))

            sublist = list(set(list(filter(lambda x: x != "" and str(x).startswith("http"), s.get(
                'https://raw.githubusercontent.com/adafhu/hayiya/master/Others', timeout=4).text.split("\n")))))


            jlist = list(set(list(filter(lambda x: x != "" and str(x).startswith("http"), s.get(
                'https://raw.githubusercontent.com/adafhu/CollectAir/master/sub_list', timeout=4).text.split("\n")))))



            # sublist.extend(air_free)
            # sublist.extend(air_mining)
            # sublist.extend(air_free1)
            sublist.extend(jlist)

            # urllist = list(map(lambda x: quote(x, safe=""), urllist))
            # urllist = list(filter(lambda x: str(x).__contains__(
            #    "getafreenode.com") == False, urllist))
            new_url = "|".join(list(set(sublist)))
            # except Exception as e:
            #     print(e)
        return new_url
    
    
    def change_date(self,id,current_url):
        if id == 40:
            new_url = datetime.today().strftime('https://clashnode.com/wp-content/uploads/%Y/%m/%Y%m%d.txt')
        if id == 36:
            today = datetime.today().strftime('%Y%m%d')
            this_month = datetime.today().strftime('%Y%m')
            url_front = 'https://nodefree.org/dy/'
            url_end = '.txt'
            new_url = url_front + this_month + '/' + today + url_end
        if id == 0:
            new_url = datetime.today().strftime('https://v2rayshare.com/wp-content/uploads/%Y/%m/%Y%m%d.txt')
        if id == 1:
            new_url = datetime.today().strftime('https://freenode.me/wp-content/uploads/%Y/%m/%m%d.txt')
        if id == 13:
            new_url = datetime.today().strftime('https://hiclash.com/wp-content/uploads/%Y/%m/%Y%m%d.txt')
        if id == 12:
            new_url = datetime.today().strftime('https://oneclash.cc/wp-content/uploads/%Y/%m/%Y%m%d.txt')
        #if id == 0:
            #today = datetime.today().strftime('%m%d')
            #url_front = 'https://raw.githubusercontent.com/pojiezhiyuanjun/freev2/master/'
            #url_end = '.txt'
            #new_url = url_front + today + url_end

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
