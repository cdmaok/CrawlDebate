#coding=utf-8

'''this code is to check debate org'''

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time,random
from multiprocessing import Pool

path = '/home/cdmaok/phantomjs-2.1.1-linux-x86_64/bin/phantomjs'

domain = 'http://www.debate.org/'

'''
browser = webdriver.PhantomJS('../path_to/phantomjs',service_args=service_args)
'''


def getTopicVote(url):
	c = TopicCrawl(url)
	c.crawl()

class TopicCrawl:

	def __init__(self,url):
		service_args = ['--proxy=127.0.0.1:1080','--proxy-type=socks5']
		self.topic = url.split('/')[-1]
		self.url = domain + url
		self.driver = webdriver.PhantomJS(executable_path = path,service_args=service_args)

	def crawl(self):
		self.driver.get(self.url)		
		self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		a = self.driver.find_element_by_class_name('debate-more-holder')
		size = len(self.driver.page_source)
		times = 0
		while times < 2:
			a.click()
			time.sleep(3)
			tmp = len(self.driver.page_source)
			if tmp != size: 
				size = tmp
			else:
				times += 1
		self.analyse(self.driver.page_source)
		self.driver.close()

	def analyse(self,string):
		bs = BeautifulSoup(string,"html.parser")
		yes_list = bs.find('div',{'class':'arguments args-yes'})
		self.parse_list(yes_list,'Yes')
		no_list = bs.find('div',{'class':'arguments args-no'})
		self.parse_list(no_list,'No')
	
		
	def parse_list(self,content,flag):
		for vote in BeautifulSoup(str(content),"html.parser").find_all('li',{'class':'hasData'}):
			cite = vote.div.cite
			user = None
			if cite.a != None:
				user = cite.a.text
				print self.topic,flag,user
				continue
			

def main():
	size = 862
	service_args = ['--proxy=127.0.0.1:1080','--proxy-type=socks5']
	driver = webdriver.PhantomJS(executable_path=path,service_args= service_args)
	for i in range(size)[:]:
		url = 'http://www.debate.org/opinions/politics/?sort=popular&p='+str(i+1)
		driver.get(url)
		gettopic(driver.page_source.encode('utf-8'))
		time.sleep(random.randint(0,30))
		print 'sleeping for ',i
	#print bs

def gettopic(string):
	bs = BeautifulSoup(string,'lxml')
	output = open('topiclist','a+')
	for a in bs.find_all('a',{'class':'a-image-contain'}):
		output.write(a['href'].encode('utf-8')+'\n')
	output.close()



if __name__ == '__main__':
	
	#main()
	#content = ''.join(open('log2').readlines())
	#gettopic(content)
	#title = '/opinions/should-donald-trump-be-the-president'
	#c.analyse(content)
	#getTopicVote(title)
	
	topics = [line.strip() for line in open('./topiclist').readlines()]
	#map(getTopicVote,topics[:3])
	pool = Pool(1)
	for t in topics[:5]:
		pool.apply_async(getTopicVote,(t,))
	pool.close()
	pool.join()
