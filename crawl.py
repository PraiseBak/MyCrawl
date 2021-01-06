# -*-coding:utf-8-*-
import dir_proc
import str_proc
import multiprocessing as multiprocs
import time
import logging
import sys
import requests
# import lxml
import os
import alarm_slack
import json
import re
from random import *
from requests.exceptions import ConnectionError
from urllib3.exceptions import NewConnectionError, MaxRetryError
from bs4 import BeautifulSoup as bs



wrong_url_count = 0
wrong_result_count = 0
this_category_got_unless_one_article = False
timeout_count = 0
do_random_sleep = False
url_len = 0
web_name = ""
is_https = True
session = requests.Session()
session.trust_env = False
headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}
format_check_count = 0
crawl_start_time = time.localtime(time.time())
file_count = 0
completed_article = 0
slacker = None
try:
	def get_real_date(date):
		try:
			listsum = ""
			date = re.findall("\d+", date)
			start_year_idx = 0	
			for idx in range(len(date)):
				if len(date[idx]) == 4:
					start_year_idx = idx
					break
			for idx in range(start_year_idx,start_year_idx+5):
				listsum += date[idx]

			listsum = listsum[:4] + '-' + listsum[4:]
			listsum = listsum[:9] + '-' + listsum[9:]
			listsum = listsum[:12] + ':' + listsum[12:14]
			return listsum
		except Exception as e:
			time_renew_prt_msg('잘못된 날짜 데이터 = ' + str(date))
			time_renew_prt_msg('ERROR = ' + str(e))
			prt_line()
			return None



	# only for better looking list
	def pretty_print_list(print_list, text):
		print("\n".join(map(str, print_list)))


	def is_html_tag_right(html_tag):
		if html_tag['menu_list'] == '' or html_tag['article'] == '' or html_tag['content'] == '':
			return False
		return True


	def do_random_time_sleep():
		rand_value = randint(0, 2)
		if rand_value == 0:
			rand_value = uniform(1, 3)
		else:
			rand_value = uniform(0.0, 0.5)

		time_renew_prt_msg("sleep {} sec".format(rand_value))
		time.sleep(rand_value)


	def get_html(url):
		global do_random_sleep
		global timeout_count
		try:
			if timeout_count == 10:
				timeout_count = 0
				time_renew_prt_msg("타임아웃 횟수 초과로 60초 휴식합니다")
				time.sleep(60)
			#if do_random_sleep:
				#do_random_time_sleep()

			html = requests.get(url, headers=headers, timeout=30)
			if not html.status_code == 200:
				False, -1
			soup = bs(html.text, 'lxml')
			if soup == None:
				raise Exception("html 가져오는데 문제 발생")
			return True, soup
		except (NewConnectionError, MaxRetryError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,
		        requests.exceptions.Timeout) as e:
			do_random_sleep = True
			timeout_count += 1
			write_error(url, str(e))
			time_renew_prt_msg(url)
			time_renew_prt_msg(str(e))
			prt_line()
			return False, None


	def get_category_list(html_tag, url, mode):
		global is_https
		global url_len
		global web_name
		success = False
		count_repeat = 0
		try:
			while (not success):
				success, soup = get_html(url)
				if not success:
					if count_repeat == 3:
						time_renew_prt_msg('접근 불가한 url')
						return
					count_repeat += 1
					continue
				newslist = list()
				for link in soup.select(html_tag[mode]):
					if link.has_attr('href'):
						newslist.append(link['href'])
					else:
						time_renew_prt_msg("url = " + url + "\nconfig의 " + mode + "의 태그에 문제가 있습니다")
						write_error(url, "config의 " + mode + "의 태그에 문제가 있습니다")
						prt_line()
			# 링크 제대로 처리
			url_origin = url
			if not len(newslist) == 0:
				url_origin = get_original_url(newslist[0])
			#print('오리진 = ',url_origin)
			newslist = str_proc.return_right_link_list(newslist, is_https, url_len, url_origin)
			###이거 테스트용임..서버에서는 하면안되요
			# return_url_format(url, newslist)

			# pretty_print_list(newslist, '')
			return newslist


		except AttributeError as e:
			print(e)
			time_renew_prt_msg('mode에 맞는 내용이 없습니다')
			write_error(url, str(e))
			prt_line()


	def prt_line():
		global web_name
		_, _, tb = sys.exc_info()
		time_renew_prt_msg('error line no = {}'.format(tb.tb_lineno))


	def write_error(url, error):
		global web_name
		logging.info("cur process = " + web_name)
		if not url == None:
			logging.info('\nurl = ' + url)
		logging.info('\nerror = ' + str(error))


	def time_renew_prt_msg(msg):
		global web_name
		tm = time.localtime(time.time())
		now = '%04d/%02d/%02d %02d:%02d:%02d   ' % (tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec)
		print(now, '' + web_name + ' ' + msg)
		logging.info(str(now)+' ' + web_name + ' ' + msg)


	def logging_init():
		global web_name
		cur_dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
		log_path = os.path.join(cur_dir_path, 'log', web_name + '.log')
		if not os.path.exists(os.path.join(cur_dir_path, 'log')):
			os.makedirs(os.path.join(cur_dir_path, 'log'))
		logging.basicConfig(format="Time : %(asctime)s Cur line : %(lineno)d \n%(message)s", datefmt='%m/%d/%Y %I:%M:%S %p',
		                    filename=log_path, level=logging.INFO)


	def is_dupli_subcategory(temp, low_cate_list):
		if is_list_duplicate(temp, low_cate_list):
			time_renew_prt_msg("하위 카테고리가 중복된 카테고리를 가지므로 종료")
			write_error("", "하위 카테고리가 중복된 카테고리를 가지므로 종료")
			return True
		return False


	def return_key_to_list(article_dict):
		return list(article_dict.keys())


	def list_append(article_list, all_article_list):
		for i in range(len(article_list)):
			all_article_list.append(article_list[i])
		return all_article_list


	def is_list_duplicate(temp, low_cate_list):
		global web_name
		count = 0
		limit = len(low_cate_list)
		if not len(temp) > len(low_cate_list):
			limit = len(temp)
		for i in range(0, limit):
			if count + 1 >= len(temp) // 2 + 1:
				time_renew_prt_msg("리스트 중복\n")
				return True

			if temp[i].rstrip('/') == low_cate_list[i].rstrip('/'):
				count += 1

		return False


	# 상위 카테고리 가져옴

	def return_log_dict(website_name):
		log_path = dir_proc.return_path_of_log(website_name)
		with open(log_path, 'r') as log_f:
			tmp = log_f.read().split('\n')
			tmp.remove('')
		log_dict = {}
		for i in range(len(tmp)):
			log_dict[tmp[i]] = "Value not to use"
		return log_dict


	def get_html_no_parse(url):
		try:
			html = requests.get(url, headers=headers, timeout=10)
			html.encoding = None
			return True, html
		except (NewConnectionError, MaxRetryError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,
		        requests.exceptions.Timeout, ConnectionResetError) as e:

			write_error(url, str(e))
			time_renew_prt_msg("get_html_no_parse ERROR url =" + url + "ERROR = " + str(e))
			prt_line()
			return False, None


	def html_to_soup_list(html_list):
		soup_list = list()
		if not len(html_list) == 0:
			time_renew_prt_msg(str(len(html_list)) + "개의 html_list가 있습니다")
		for i in range(0, len(html_list)):
			html_text = bs(html_list[i].text, 'lxml')
			soup_list.append(html_text)
		return soup_list


	def get_result(soup, html_tag, url):
		try:
			title = soup.select_one(html_tag['title'])
			if title == None or title == []:
				#time_renew_prt_msg("타이틀이 없는 기사이거나 태그가 잘못되었습니다 url:" + url)
				return False
			content = soup.select_one(html_tag['content'])
			if content == None or content == []:
				time_renew_prt_msg("내용이 없는 기사이거나 태그가 잘못되었습니다 url:" + url)
				return False

			date = soup.select_one(html_tag['date'])
			# field=soup.select_one(html_tag['article_field']).text
			# print(field)
			result = dict()
			result['url'] = url
			result['title'] = title.text
			# select면 [] select_one이면 None
			if not date == None:
				result['date'] = get_real_date(str(date))
				if result['date'] == None:
					print('날짜에러 발생')
					raise ('날짜 에러발생\nURL = ', url)
			result['content'] = content.text
			return result

		except Exception as e:
			time_renew_prt_msg(str(e) + '\nurl = ' + url)
			write_error(url, str(e))
			prt_line()
			return False


	def write_files(soup_list, website, html_tag, article_list):
		global slacker
		global file_count
		global this_category_got_unless_one_article
		global wrong_result_count
		result_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'result', website)
		file_name = os.path.join(result_path, 'json_result',
		                         website + '_{}{:02d}{:02d}'.format(crawl_start_time.tm_year, crawl_start_time.tm_mon,
		                                                            crawl_start_time.tm_mday))
		html_name = os.path.join(result_path, 'html',
		                         website + '_{}{:02d}{:02d}'.format(crawl_start_time.tm_year, crawl_start_time.tm_mon,
		                                                            crawl_start_time.tm_mday))

		if not os.path.exists(os.path.join(result_path, 'json_result')):
			os.makedirs(os.path.join(result_path, 'json_result'))

		if not os.path.exists(os.path.join(result_path, 'html')):
			os.makedirs(os.path.join(result_path, 'html'))

		with open(file_name + '.json', 'a', -1, 'utf-8') as json_f:
			for idx in range(len(soup_list)):
				result = get_result(soup_list[idx], html_tag, article_list[idx])
				if not result == False:
					wrong_result_count = 0
					this_category_got_unless_one_article = True
					json.dump(result, json_f, ensure_ascii=False)
					json_f.write('\n')
				else:
					#Todo 슬랙 알람 처리 중
					wrong_result_count += 1
					if wrong_result_count == 30:
						#Todo 슬랙 알람.
						slack_send_msg(slacker,"기사의 결과를 가져올 수 없습니다 {}의 점검을 요합니다. - 알람 기능 수정버전 테스트".format(website))





		for i in range(len(soup_list)):
			html_name = os.path.join(result_path, 'html', website + '_{}{:02d}{:02d}{:05d}'.format(crawl_start_time.tm_year,
			                                                                                       crawl_start_time.tm_mon,
			                                                                                       crawl_start_time.tm_mday,
			                                                                                       file_count))
			with open(html_name + '.html', 'w', -1, 'utf-8') as html_f:
				html_f.write(str(soup_list[i]))
				file_count += 1
		if not len(soup_list) == 0:
			time_renew_prt_msg('html 출력 성공')


	def crawling_check(crawled_url_list, website):
		with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log', website + "_crawl_log.txt"), 'a') as f:
			for idx in range(len(crawled_url_list)):
				f.write(crawled_url_list[idx] + '\n')


	def get_article(paged_low_cate, article_tag, soup):
		global format_check_count
		global page_limit
		article_list = list()
		if soup.select(article_tag) == []:
			page_limit += 1
		for link in soup.select(article_tag):
			article_list.append(link['href'])
		return article_list


	def output_process(article_list, html_tag, website):
		global web_name
		global process_num
		global completed_article
		html_list = list()
		# 테스트
		for idx in range(0, len(article_list)):
			try:
				success = False
				fail_count = 0
				while not success:
					success, html = get_html_no_parse(article_list[idx])
					if not success:
						time_renew_prt_msg("접근 실패")
						fail_count += 1
						time.sleep(0.3)
						if fail_count == 2:
							time_renew_prt_msg("접근 실패로 인해 다음 기사로 넘어갑니다")
							break
						continue
					html_list.append(html)

			except Exception as e:
				time_renew_prt_msg("output_process error = " + str(e))
				time_renew_prt_msg("URL =" + article_list[idx])
				time.sleep(2)
				prt_line()
				continue
		soup_list = html_to_soup_list(html_list)
		crawling_check(article_list, website)
		write_files(soup_list, website, html_tag, article_list)
		completed_article += len(soup_list)


	# 여기로
	def return_list_to_process(article_list, website_name):
		# processing_list는 아예 겹치지 않아야함
		crawling_dupli_count = 0
		log_dict = return_log_dict(website_name)
		result_dict = {}
		for i in range(len(article_list)):
			if crawling_dupli_count >= len(article_list) - 3:
				time_renew_prt_msg("로그와 중복되어 리스트 반환됨 URL = " + article_list[i])
				return list(result_dict.keys()), False
			if log_dict.get(article_list[i]) == None:
				# 로그와 중복하지 않은 리스트
				result_dict[article_list[i]] = "Value not to use"
				crawling_dupli_count = 0
			else:
				crawling_dupli_count += 1
		# pretty_print_list(double_checked_list, '완성된 리스트')

		return list(result_dict.keys()), True


	def get_original_url(exam_url):
		exam_url = exam_url.replace("https://", '')
		exam_url = exam_url.lstrip('/')
		cut_part = exam_url.find('/')
		exam_url = exam_url[0:cut_part]
		if is_https:
			exam_url = 'https://' + exam_url
		else:
			exam_url = 'http://' + exam_url
		return exam_url


	def double_check_url(completed_list, origin_url):

		origin_url = origin_url.rstrip('/')
		result_list = list()
		for i in range(len(completed_list)):
			if not completed_list[i].find(origin_url) == -1:

				result_list.append(completed_list[i])
		return result_list


	def set_url_access(set_key, value, config, web_name):
		config['url_access'][set_key] = value
		dir_proc.write_config(config, web_name)


	def third_check(article_list, origin_url):
		origin_url_slash_count = origin_url.count('/')
		result_list = list()
		for i in range(len(article_list)):
			if origin_url_slash_count +1 <= article_list[i].count('/'):
				result_list.append(article_list[i])
		return result_list


	def get_article_list(low_cate_list, html_tag, website_name, url_original, config, all_page_mode):
		global url_name
		global is_https
		global url_len
		global page_limit
		global this_category_got_unless_one_article
		global wrong_url_count
		global slacker
		url_access = config['url_access']
		page_limit = 0
		paged_low_cate = ""
		dupli_check_list = list()
		all_article_count = 0
		page_arbitary_unit = 1000
		low_start_index = 0
		if all_page_mode:
			low_start_index = int(url_access["low_cate_idx"])
		origin_url = get_original_url(low_cate_list[0])
		if all_page_mode:
			page_count_limit = -1
		else:
			page_count_limit = page_arbitary_unit
		try:

			for cate_idx in range(low_start_index, len(low_cate_list)):
				#한 하위 카테고리 마다 구분해줌
				this_category_got_unless_one_article = False
				#Todo 하위 카테고리 페이지 기록
				
				if all_page_mode:
					set_url_access("low_cate_idx", str(cate_idx), config, website_name)

				#TODO Start Page
				start_page = 1
				if all_page_mode:
					start_page = int(url_access["Start page"])
				article_count = 0
				get_html_fail = 0
				page_limit = 0
				page_count = 1
				dupli_check_pass = 0
				dupli_check = False
				there_is_no_article_on_page = 0
				print()
				time_renew_prt_msg("현재 하위 카테고리 = " + str(low_cate_list[cate_idx]))

				while not page_limit >= 5:
					low_cate_start_time = time.time()
					success = False
					while not success:
						try:
							if page_count >= page_count_limit and page_count_limit != -1:
								print("\n제한 초과\n")
								page_limit = 5
							if dupli_check_pass >= 5 and not all_page_mode:
								time_renew_prt_msg("중복된 페이지이므로 다음 하위 카테고리로 넘어갑니다")
								page_limit = 5
								break

							if page_limit == 5:
								break

							if page_count % 10 == 0:
								time_renew_prt_msg("페이지 = " + str(start_page))
								# TODO 하위 카테고리 페이지 처리할 부분
								if all_page_mode:
									set_url_access("Start page",str(start_page),config,website_name)

							if get_html_fail >= 10 and not all_page_mode:
								page_limit = 5
								time_renew_prt_msg('접근 실패 횟수 초과')
								break

							paged_low_cate = low_cate_list[cate_idx].format(page=str(start_page))
							start_page += 1
							page_count += 1
							if website_name == "DONGA":
								start_page += 19
								if start_page % 200 + 1 == 0:
									time_renew_prt_msg("페이지 = " + str(start_page/20))

							success, soup = get_html(paged_low_cate)

							if not success:
								if this_category_got_unless_one_article and soup == -1:
									wrong_url_count += 1
									if wrong_url_count == 30:
										#Todo 슬랙알람 점검 2
										slack_send_msg(slacker,"URL의 페이지 응답을 받지 못했습니다. {}의 점검을 요합니다".format(website_name))
										break
								page_count -= 1
								get_html_fail += 1
								continue
							wrong_url_count = 0

							article_list = get_article(paged_low_cate, html_tag['article'], soup)



							if dupli_check_list == article_list:
								time_renew_prt_msg("모든 페이지를 긁었거나 잘못된 페이지이므로 다음 하위 카테고리로 넘어갑니다")
								url_access["Start page"] = "1"
								page_limit = 5
								break
							dupli_check_list = article_list
							article_list = str_proc.return_right_link_list(article_list, is_https, url_len, origin_url)
							completed_list = double_check_url(article_list, origin_url)
							completed_list, dupli_check = return_list_to_process(completed_list, website_name)
							if not dupli_check:
								dupli_check_pass += 1
			
			
							article_count += len(completed_list)
							completed_list = third_check(completed_list, origin_url)
							#TODO UM
								
							if this_category_got_unless_one_article:
								if there_is_no_article_on_page == 30:
									time_renew_prt_msg("현재 카테고리에 기사가 없습니다.")
									sys.exit(0)
								if len(completed_list) == 0:
									there_is_no_article_on_page += 1
								else:
									there_is_no_article_on_page = 0



							output_process(completed_list, html_tag, website_name)


						except Exception as e:
							time_renew_prt_msg('get_article_list problem = ' + str(e))
							if type(e) == KeyError:
								page_limit = 5
							write_error(paged_low_cate, e)
							prt_line()

				time_renew_prt_msg("한 하위 카테고리 기사 개수 = " + str(article_count))
				all_article_count += article_count
			# output_process(completed_list, html_tag, website_name)

			time_renew_prt_msg("모든 기사 모음 리스트 갯수 = " + str(all_article_count))
			# pretty_print_list(all_article_list,'')
			return page_arbitary_unit
		except Exception as e:
			time_renew_prt_msg(str(e) + '\n기사 리스트 가져오는 함수에서 발생한 에러')
			prt_line()


	def list_to_dict(list_obj):
		result_dict = {}
		for i in range(len(list_obj)):
			result_dict[list_obj[i]] = "Value not to use"
		return result_dict


	def slack_send_msg(slack, msg):
		global web_name
		if not web_name == "MK":
			slack.send_msg(msg)
			time_renew_prt_msg("웹 페이지가 변경된 것으로 판단되어 크롤링을 종료합니다")
		sys.exit(0)


	# mode 0 로그 없을 시 mode 1 로그 있을 시
	def crawl(website_name, url, all_page_mode):
		global web_name
		global url_len
		global format_check_count
		global completed_article
		global slacker
		mode = "menu_list"
		temp = ""
		slack = alarm_slack.SlackAPI()
		slacker = slack
		try:
			web_name = website_name
			logging_init()
			time_renew_prt_msg(website_name + " 시작")
			completed_article = 0
			# 시간측정
			start_time = time.time()
			url_len = len(url)
			if url.find('https') == -1: is_https = False
			is_files_dir_ok = dir_proc.setting_dir(website_name)

			if not is_files_dir_ok:
				time_renew_prt_msg("필요한 파일이 없습니다")
				sys.exit(0)
			config = dir_proc.return_config(website_name)
			url_access, html_tag = dir_proc.return_config_instance(config)
			if url_access['Start page'] == "end" and all_page_mode:
				time_renew_prt_msg("이미 모든 페이지 크롤링이 끝난 웹페이지 입니다. 새로운 페이지 크롤링 모드로 실행하여주세요")
				sys.exit(0)
			format_original_url = url_access["url"]
			format_check_count = format_original_url.rstrip('/').count('/')

			if not is_html_tag_right(html_tag):
				time_renew_prt_msg(website_name + '_config 파일을 입력해 주세요')
				sys.exit(0)
			#상위 카테고리 가져옴
			high_cate_list = get_category_list(html_tag, url, mode)
			if high_cate_list == None or high_cate_list == []:
				# 웹사이트별로 프로세스 돌리면 raise하면 되겠지만
				# 지금은 아니니까 일단 일일이 print
				time_renew_prt_msg("error = 상위 카테고리를 가져오는데 실패하였습니다")
				write_error(url, "상위 카테고리를 가져오는데 실패하였습니다")
				slack_send_msg(slack,"상위 카테고리를 가져오는데 실패하였습니다 {}의 점검을 요합니다 ".format(web_name))
			#Todo 상위 카테고리 페이지 부분
			if  all_page_mode:
				
				high_cate_start = int(url_access["high_cate_idx"])
			else:
				high_cate_start = 0
			for high_cate_idx in range(high_cate_start, len(high_cate_list)):
				if all_page_mode:
					set_url_access("high_cate_idx",str(high_cate_idx),config, website_name)
				# time_renew_prt_msg('현재 상위 = ' + str(high_cate_list[high_cate_idx]))
				if html_tag["sitemap"] == "":
					low_cate_list = high_cate_list
				else:
					mode = "sitemap"
					low_cate_list = get_category_list(html_tag, high_cate_list[high_cate_idx], mode)

				if high_cate_idx == 0: temp = low_cate_list
				
				if low_cate_list is None or low_cate_list == []:
					time_renew_prt_msg(" URL=  " + high_cate_list[high_cate_idx] + "\n하위 카테고리 리스트를 가져오는데 실패하였습니다")
					write_error(url, high_cate_list[high_cate_idx] + "\n하위 카테고리 리스트를 가져오는데 실패하였습니다")
					continue
				# 하위 카테고리가 중복 카테고리를 가지는지 체크
				if high_cate_idx == 1:
					if is_dupli_subcategory(temp, low_cate_list):
						break
				low_standard_list = str_proc.return_standard_list(low_cate_list, format_original_url)
				# 각 하위카테고리 별 처리
				page_count = get_article_list(low_standard_list, html_tag, website_name, url, config, all_page_mode)

			if all_page_mode and not completed_article == 0:
				ended_page = str("end")
				config['url_access']['Start page'] = ended_page
				dir_proc.write_config(config, web_name)
			if completed_article <= 0:
				slack_send_msg(slack, "크롤링 된 기사의 개수가 {}개로 {}의 점검을 요합니다 ".format(completed_article,website_name))

			print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
			time_renew_prt_msg(str(time.time() - start_time) + "시간 경과")
			time_renew_prt_msg(str(completed_article) + "개의 페이지 크롤링 완료")
			write_error(None, "cur process = " + web_name + " 종료")
			sys.exit(0)

		except Exception as e:
			write_error(url, str(e))
			time_renew_prt_msg('error = ' + str(e))
			prt_line()
			sys.exit(0)

except KeyboardInterrupt:
	print('키보드 인터럽트')
	sys.exit(0)




def procs_management(procs):
	# check process.
	# if process dead than set next process to work
	time.sleep(3)
	for i in range(0, len(procs)):
		if not procs[i].is_alive():
			procs[i].join()
			del (procs[i])
			break


# check per 5 min
def init_config(website):
	config = dir_proc.return_config(website)
	url_access = config['url_access']
	url_access["high_cate_idx"] = "0"
	url_access["low_cate_idx"] = "0"
	url_access["Start page"] = "1"
	config["url_access"] = url_access

	dir_proc.write_config(config,website)


def start_proc_per_website(all_page_mode):
	procs = list()
	urlfile, no_use = dir_proc.set_url_dir()
	cur_dir = dir_proc.return_dir_path()
	for website in urlfile:
		if all_page_mode == "init":
			init_config(website)
			continue
		process = multiprocs.Process(target=crawl, args=(website, urlfile[website],all_page_mode))
		process.start()
		procs.append(process)
		while len(procs) >= 4:
			procs_management(procs)
	while len(procs) > 0:
		procs_management(procs)
	sys.exit(0)


if __name__ == '__main__':

	all_page_mode = False

	if len(sys.argv) > 1:
		if sys.argv[1] =="init":
			print("init mode")
		if sys.argv[1] =="all":
			print('Its For all pages mode')
			all_page_mode = True
		elif sys.argv[1] == "New":
			print("Its New page only mode")
			all_page_mode = False
		else:
			print("Its wrong command but execute as a New page mode")
			all_page_mode = False
	else:
		print("Its New page only mode")

	if len(sys.argv) > 1:
		if sys.argv[1] =="init":
			all_page_mode = "init"
	start_proc_per_website(all_page_mode)
