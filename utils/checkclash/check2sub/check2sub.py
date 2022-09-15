import re, yaml
import time, os
from sub_convert import sub_convert
from ip_update import geoip_update  #将此行放入需要引用的文件里

# 已测速转url,base64,clash
input_check_file = './sub/check/check.yaml'    # 需要查看checkclash文件夹里面config配置文件设置的地址
output_url_path = './sub/check/rx'
output_base64_path =  './sub/check/rx64'
output_clash_path = './sub/check/rxClash.yml' 

#转clash用的provider
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
        if line != 'proxies:':
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
    all_provider = 'proxies:\n' + '\n'.join(all_proxy)
    hk_provider = 'proxies:\n' + '\n'.join(hk_proxy)
    jp_provider = 'proxies:\n' + '\n'.join(jp_proxy)
    sg_provider = 'proxies:\n' + '\n'.join(sg_proxy)
    others_provider = 'proxies:\n' + '\n'.join(others_proxy)
    
        
    eternity_providers = {
            'all': all_provider,
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

if __name__ == '__main__':
    #更新IP库
    geoip_update()

    # 将测速完的check内容转成url节点内容
    input_check_file_path = os.path.abspath(input_check_file)   #python获取绝对路径https://www.jianshu.com/p/1563374e279a
    subContent = sub_convert.convert_remote(input_check_file_path, 'url', 'http://127.0.0.1:25500')
    # 写入url 订阅文件
    print('write rx url sub content!')
    file = open(output_url_path, 'w+', encoding= 'utf-8')
    file.write(subContent)
    file.close()
    # 写入base64 订阅文件
    subContent = sub_convert.base64_encode(subContent)
    print('write rx64 sub content!')
    file = open(output_base64_path, 'w+', encoding= 'utf-8')
    file.write(subContent)
    file.close()
   # 写入Clash 订阅文件
    print('write RXClash begin!')
    eternity_convert(output_base64_path, config_file, output=output_clash_path)
    print('write RXClash Over!')
