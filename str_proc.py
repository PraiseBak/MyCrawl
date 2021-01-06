#-*-coding:utf-8-*-
import sys
import time
import crawl
def return_right_link_list(link_list,is_https,url_len,url_original):
	is_https = True
	http_or_https = "https://"
	if is_https == False:
		http_or_https = "http://"
	if url_original.find('https') == -1:
		is_https = False
	right_link_list = list()
	for list_idx in range(0,len(link_list)):
		check_is_https = False
		link=link_list[list_idx]
		you_can_go = False
		#케이스 1 url 주 부분이 있을 시 일단 통과
		if link.find(url_original) != -1:
			if link.find('https') != -1:
				check_is_https = True
			if check_is_https == is_https:
				you_can_go = True
			else:
				continue
		if you_can_go:
			right_link_list.append(link)
			continue
		#TODO
		#케이스 1.5 //www.yna.co.kr/news
		#걍 http나 https 붙여서 url_origin찾아지면 ㅇㅋ 할까
		link = link.lstrip('/')
		case_2 =http_or_https + link
		if case_2.find(url_original) != -1:
			right_link_list.append(case_2)

			continue
		#케이스 2 url 주 부분이 없음 즉 아마 http나 https도 없을것 예상
		#ex - //article/1234 -> article/1234
		#TODO 동작 체크 
		else:			
			link = url_original + '/' + link
			right_link_list.append(link)
	return right_link_list


def get_format_part(format_url,mode):
	if mode == 'high':
		high_start_idx=format_url.find('{')
		high_end_idx=format_url.find('}')
		high_end_char=format_url[high_end_idx+1]
		return high_start_idx,high_end_char
	else:
		low_start_idx=format_url.find('{')
		low_end_idx=format_url.find('}',low_start_idx)
		low_end_char=format_url[low_end_idx+1]
		return low_start_idx,low_end_char


def get_end_idx(low_cate_url,start_idx,end_char):
	end_idx=low_cate_url.find(end_char,start_idx+1)
	return end_idx

def is_there_low(low_cate_url,high_end_idx,high_end_char):
	if not low_cate_url.find(high_end_char,high_end_idx+1) == -1: return True
def get_part(start_idx,end_idx,low_cate_url):
	return low_cate_url[start_idx:end_idx]

def is_format_got_low(format_url):
	if not format_url.find('{cate') == -1 :
		return True

def return_low_start_char(format_url):
	start_idx=format_url.find("{cate")
	return format_url[start_idx-1]

def return_is_list_has_low(format_url,low_cate_url):

	format_url=format_url[0:format_url.find('{cate}')+6]
	low_cate_url=low_cate_url.strip('/')

	if format_url.count('/') == low_cate_url.count('/') -1 or format_url.count('/') == low_cate_url.count('/'):
		return True

def return_standard_list(low_cate_url_list,format_original_url):
	standard_list=list()
	try:
		format_original_url=format_original_url.rstrip('/')
		format_has_low=is_format_got_low(format_original_url)

		for cate_idx in range(0,len(low_cate_url_list)):
			low_cate_url_list[cate_idx]+="/"
			is_list_has_low=return_is_list_has_low(format_original_url,low_cate_url_list[cate_idx])
			format_url=format_original_url
			high_start_idx,high_end_char=get_format_part(format_original_url,'high')
			high_end_idx=get_end_idx(low_cate_url_list[cate_idx],high_start_idx,high_end_char)
			high_part=get_part(high_start_idx,high_end_idx,low_cate_url_list[cate_idx])
			
			format_url=format_original_url.format(high_cate=high_part,cate="{cate}",page="{page}")
			if format_has_low and is_list_has_low:
				low_start_idx,low_end_char=get_format_part(format_url,'low')
				low_end_idx=get_end_idx(low_cate_url_list[cate_idx],low_start_idx,low_end_char)
				low_part=get_part(low_start_idx,low_end_idx,low_cate_url_list[cate_idx])
				format_url=format_url.format(cate=low_part,page="{page}")
			else:
				format_url=str(format_url).replace('{cate}/','')
			standard_list.append(format_url)
		return standard_list
	except Exception as e:
		crawl.write_error('None',str(e))
		crawl.time_renew_prt_msg('error = '+str(e))
		crawl.prt_line()





	