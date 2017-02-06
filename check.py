#coding=utf-8

'''this code is to check debate org'''

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time,random,sys
from multiprocessing import Pool
import signal

path = '/home/yangying/phantomjs-2.1.1-linux-x86_64/bin/phantomjs'
domain = 'http://www.debate.org/'


def getTopicVote(index,url):
	c = TopicCrawl(index,url)
	c.crawl()

class TopicCrawl:

	def __init__(self,index,url):
		self.index = index
		service_args = ['--proxy=127.0.0.1:1080','--proxy-type=socks5']
		self.topic = url.split('/')[-1]
		self.url = domain + url
		self.driver = webdriver.PhantomJS(executable_path = path,service_args=service_args)

	def crawl(self):
		self.driver.get(self.url)		
		self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		a = None
		try:
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
		except NoSuchElementException:
			pass
		finally:
			self.analyse(self.driver.page_source)
			self.driver.close()
			print 'finish crawling with topic',self.index,self.topic

	def analyse(self,string):
		bs = BeautifulSoup(string,"html.parser")
		yes_list = bs.find('div',{'class':'arguments args-yes'})
		no_list = bs.find('div',{'class':'arguments args-no'})
		yesvote = self.parse_list(yes_list,'Yes') 
		novote = self.parse_list(no_list,'No')
		if len(yesvote) == 0 or len(novote) == 0:
			print 'nothing to save' 
		else:
			self.save(yesvote + novote)

	def save(self,votes):
		output = open('./votes','a+')
		output.write('\n'.join(votes)+'\n')
		output.close()
	
		
	def parse_list(self,content,flag):
		ans = []
		for vote in BeautifulSoup(str(content),"html.parser").find_all('li',{'class':'hasData'}):
			cite = vote.div.cite
			user = None
			if cite.a != None:
				user = cite.a.text
				ans.append(' '.join([self.topic,flag,str(user).strip()]))
				continue
		return ans
			

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

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

if __name__ == '__main__':
	
	#main()
	#content = ''.join(open('log2').readlines())
	#gettopic(content)
	#title = '/opinions/should-donald-trump-be-the-president'
	#c.analyse(content)
	#getTopicVote(title)
	
	topics = [line.strip() for line in open('./topiclist').readlines()]

	'''
	for index,t in enumerate(topics[1:3]):
		getTopicVote(index,t)

	
	'''
	pool = Pool(5,init_worker)
	try:
		threads = [pool.apply_async(getTopicVote,(index,t,)) for index,t in enumerate(topics[11215:])]
		pool.close()
		
		while True:
			if all(r.ready() for r in threads):
				print 'All processes completed' 
				sys.exit()
			time.sleep(1)

	except KeyboardInterrupt:
		print "Caught KeyboardInterrupt, terminating workers"
        	pool.terminate()
        	pool.join()
	pool.join()
