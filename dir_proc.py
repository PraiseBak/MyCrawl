# -*-coding:utf-8-*-
import os
import json
import sys
import crawl


def config_form(text_list):
    config = dict()

    html_tag = dict()
    url_access = dict()
    if not text_list == []:

        print(text_list)
        print(len(text_list))
        html_tag["menu_list"] = text_list[0]
        html_tag["sitemap"] = text_list[1]
        html_tag["article"] = text_list[2]
        html_tag["title"] = text_list[3]
        html_tag["content"] = text_list[4]
        html_tag["date"] = text_list[5]
        if not len(text_list) == 6:
            url_access["url"] = text_list[6]
    else:
        html_tag["menu_list"] = ""
        html_tag["sitemap"] = ""
        html_tag["article"] = ""
        html_tag["title"] = ""
        html_tag["content"] = ""
        html_tag["date"] = ""
        url_access["url"] = ""

    url_access["paging_mode"] = "All Page"
    url_access["high_cate_idx"] = "0"
    url_access["low_cate_idx"] = "0"
    url_access["Start page"] = "1"
    config["html_tag"] = html_tag
    config["url_access"] = url_access
    return config


def url_form():
    website_name = dict()
    website_name["enter_website_name"] = "enter_url"

    return website_name


def setting_dir(website_name):
    dir = website_name
    abs_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    result_dir = os.path.join(abs_path, 'result', website_name)
    json_path = os.path.join(abs_path, 'config', website_name + '_config.json')
    if not os.path.exists(os.path.join(abs_path, 'config')):
        os.makedirs(os.path.join(abs_path, 'config'))
    if not website_name == "enter_website_name":
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        if not os.path.exists(os.path.join(abs_path, 'log')):
            os.makedirs(os.path.join(abs_path, 'log'))

        if not os.path.exists(os.path.join(abs_path, 'log', website_name + "_crawl_log.txt")):
            with open(os.path.join(abs_path, 'log', website_name + "_crawl_log.txt"), 'w') as f:
                f.write("")
    else:
        print(website_name)
        print('Wrong urlfile !')
        sys.exit(0)

    if not os.path.exists(json_path):
        text_list = list()
        with open(json_path, 'w', -1, "utf-8") as f:
            json.dump(config_form(text_list), f, indent="\t")
            print('config안의' + website_name + '_config.json', '를 입력해주세요')
            crawl.write_error('None', website_name + '_config problem occur. \npass to new config')
            return False
    return True


def set_url_dir():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(os.path.join(dir_path, 'urlfile.json')):
        with open(os.path.join(dir_path, "urlfile.json"), 'w') as f:
            json.dump(url_form(), f, indent="\t")
            print('urlfile.json을 입력해주세요')
            print('입력이 비정상적일 경우 제대로 동작하지 않습니다')
            crawl.write_error('None', 'urlfile.json need check\nprogram exit')
            sys.exit(0)

    with open(os.path.join(dir_path, "urlfile.json"), 'r') as json_file:
        urlfile = json.load(json_file)
        try:
            url_list = list(urlfile.keys())
        except AttributeError as e:
            crawl.write_error('None",urlfile.json need check\nprogram exit')
            print('urlfile.json을 양식에 맞춰 입력해주세요')
            sys.exit(0)
        return urlfile, url_list


def return_config(website_name):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config', website_name + '_config.json'),
              'r') as config_file:
        return json.load(config_file)


def return_config_instance(config):
    return config['url_access'], config['html_tag']

def return_path_of_log(website_name):
    return os.path.join(return_dir_path(),'log', website_name+"_crawl_log.txt")


def return_dir_path():
    return os.path.dirname(os.path.realpath(__file__))

def write_config(config, website):
    config_dir = os.path.join(return_dir_path(),'config',website+'_config.json')
    with open(os.path.join(config_dir), 'w') as f:
        json.dump(config, f, indent="\t")