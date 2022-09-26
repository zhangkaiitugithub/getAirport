import re, yaml
import time, os
from tqdm import tqdm   #进度条库
import threading  #线程
from ip_update import geoip_update  # 更新ip库Country.mmdb 
from sub_convert import sub_convert

#源文件
urllistfile = './config/sublist_mining'
#输出订阅文件位置
outputUrlSub_path = './sub/miningUrl'
outputBase64Sub_path =  './sub/miningUrl64'
outputClashSub_path = './sub/miningClash.yml' 
#转YAML需要用到的config.yml文件
config_file = './config/provider/config.yml'

class NoAliasDumper(yaml.SafeDumper): # https://ttl255.com/yaml-anchors-and-aliases-and-how-to-disable-them/
    def ignore_aliases(self, data):
        return True

def eternity_convert(file, config, output, provider_file_enabled=True):
    
    file_eternity = open(file, 'r', encoding='utf-8')
    sub_content = file_eternity.read()
    file_eternity.close()
    all_provider = sub_convert.main(sub_content,'content','YAML',custom_set={'dup_rm_enabled': True,'format_name_enabled': True})

    # 创建并写入 provider 
    lines = re.split(r'\n+', all_provider)
    
    all_proxy = []
    hk_proxy = []
    jp_proxy = []
    sg_proxy = []
    others_proxy = []

    for line in lines:
        if line != 'proxies:'  and 'plugin' not in line:
            line = '  ' + line  
            all_proxy.append(line)
            if 'HK' in line or '香港' in line:
                hk_proxy.append(line)
            elif 'JP' in line or '日本' in line:
                jp_proxy.append(line)
            elif 'SG' in line or '新加坡' in line:
                sg_proxy.append(line)
            else:
                others_proxy.append(line)
    allproxy_provider = 'proxies:\n' + '\n'.join(all_proxy)
    hk_provider = 'proxies:\n' + '\n'.join(hk_proxy)
    jp_provider = 'proxies:\n' + '\n'.join(jp_proxy)
    sg_provider = 'proxies:\n' + '\n'.join(sg_proxy)
    others_provider = 'proxies:\n' + '\n'.join(others_proxy)
     
    eternity_providers = {
            'all': allproxy_provider,
            'hk': hk_provider,
            'jp': jp_provider,
            'sg': sg_provider,
            'others': others_provider
        }

    # 创建完全配置的Eternity.yml
    config_f = open(config_file, 'r', encoding='utf-8')
    config_raw = config_f.read()
    config_f.close()
    
    config = yaml.safe_load(config_raw)
    all_provider_dic = {'proxies': []}
    hk_provider_dic = {'proxies': []}
    jp_provider_dic = {'proxies': []}
    sg_provider_dic = {'proxies': []}
    others_provider_dic = {'proxies': []}
    
    provider_dic = {
        'all': all_provider_dic,
        'hk': hk_provider_dic,
        'jp': jp_provider_dic,
        'sg': sg_provider_dic,
        'others': others_provider_dic
    }
    for key in eternity_providers.keys(): # 将节点转换为字典形式
        provider_load = yaml.safe_load(eternity_providers[key])
        provider_dic[key].update(provider_load)

    # 创建节点名列表
    all_name = []   
    hk_name = []
    jp_name = [] 
    sg_name = []
    others_name = []    
    
    name_dict = {
        'all': all_name,
        'hk': hk_name,
        'jp': jp_name,
        'sg': sg_name,
        'others': others_name     
    }
    for key in provider_dic.keys():
        if not provider_dic[key]['proxies'] is None:
            for proxy in provider_dic[key]['proxies']:
                name_dict[key].append(proxy['name'])
        if provider_dic[key]['proxies'] is None:
            name_dict[key].append('DIRECT')
    # 策略分组添加节点名
    proxy_groups = config['proxy-groups']
    proxy_group_fill = []
    for rule in proxy_groups:
        if rule['proxies'] is None: # 不是空集加入待加入名称列表
            proxy_group_fill.append(rule['name'])
    for rule_name in proxy_group_fill:
        for rule in proxy_groups:
            if rule['name'] == rule_name:
                rule.update({'proxies': all_name})
                
                if '香港' in rule_name:
                    rule.update({'proxies': hk_name})
                elif '日本' in rule_name:
                    rule.update({'proxies': jp_name})
                elif '狮城' in rule_name or '新加坡' in rule_name:
                    rule.update({'proxies': sg_name})
                elif '其他节点' in rule_name:
                    rule.update({'proxies': others_name})
                else:
                    rule.update({'proxies': all_name})
                    
    config.update(all_provider_dic)
    config.update({'proxy-groups': proxy_groups})

    config_yaml = yaml.dump(config, default_flow_style=False, sort_keys=False, allow_unicode=True, width=750, indent=2, Dumper=NoAliasDumper)
    
    Eternity_yml = open(output, 'w+', encoding='utf-8')
    Eternity_yml.write(config_yaml)
    Eternity_yml.close()
#test--begin    
def sub_to_url(url):
    if 'http' in url:
        subContent =sub_convert.convert_remote(url,'url','http://127.0.0.1:25500')        
        allProxy.append(subContent)
    bar.update(1)
#test--over  

def urlListToSub(urllistfile):
    file_urllist = open(urllistfile, 'r', encoding='utf-8')
    urllist_content = file_urllist.read()
    file_urllist.close()
    
    lines = re.split(r'\n+',urllist_content)
    allProxy = []
#test--begin
    lenlines =len(lines)
    thread_max_num =threading.Semaphore(lenlines)
    bar = tqdm(range(total=lenlines),, desc='订阅获取：')
    thread_list = []
    for line in lines:
        t = threading.Thread(target=sub_to_url, args=url)
        thread_list.append(t)
        t.setDaemon(True)
        t.start()
    for t in thread_list:
        t.join()
    bar.close()
    
    ownallProxy = '\n'.join(allProxy)
#test--over  

    """
    #tqdm进度条方式显示fetch节点列表进度
    for index in tqdm(range(int(len(lines))), desc="Fetch:"):
        if 'http' in lines[index]:
            subContent =sub_convert.convert_remote(lines[index],'url','http://127.0.0.1:25500')
            allProxy.append(subContent)
    ownallProxy = '\n'.join(allProxy)
    """
    # 写入url 订阅文件
    print('write miningUrl content!')
    file = open(outputUrlSub_path, 'w', encoding= 'utf-8')
    file.write(ownallProxy)
    file.close()

    # 写入base64 订阅文件
    subContent = sub_convert.base64_encode(ownallProxy)
    print('write miningUrl64 content!')
    file = open(outputBase64Sub_path, 'w', encoding= 'utf-8')
    file.write(subContent)
    file.close()

   # 写入Clash 订阅文件
    print('write miningClash begin!')
    eternity_convert(outputBase64Sub_path, config_file,    output=outputClashSub_path)
    print('write miningClash Over!')

if __name__ == '__main__':
    #更新IP库
    geoip_update('https://raw.githubusercontent.com/Loyalsoldier/geoip/release/Country.mmdb')
    urlListToSub(urllistfile)


