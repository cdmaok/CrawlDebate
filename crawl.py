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
import signal,json

path = '/home/yangying/phantomjs-2.1.1-linux-x86_64/bin/phantomjs'
domain = 'http://www.debate.org/'


def getTopicVote(index,url):
	c = TopicCrawl(index,url)
	c.crawl()

class UserCrawl:
	def __init__(self,index,name):
		self.index = index
		self.name = name
		self.url = domain + name
		service_args = ['--proxy=127.0.0.1:1080','--proxy-type=socks5']
		self.driver = webdriver.PhantomJS(executable_path = path,service_args=service_args)
	
	def crawl(self):
		self.driver.get(self.url)
		content = self.driver.page_source.encode('utf-8')
		user_str = self.getuser(content)
		self.save(user_str)
		self.driver.close()
		print 'finish fetching ', self.index

	def save(self,string):
		output = open('./detailuser','a+')
		output.write(string+'\n')
		output.close()

	def getuser(self,content):
		bs = BeautifulSoup(content,"html.parser")
		table  = bs.find('tbody')
		user = {"Party": "Not Saying", "Looking": "No Answer", "Updated": "1 Year Ago", "Name": "- Private -", "Relationship": "Not Saying", "Interested": "No Answer", "Gender": "Prefer not to say", "Income": "Not Saying", "Joined": "1 Year Ago", "Ideology": "Not Saying", "Religion": "Not Saying", "Birthday": "- Private -", "Online": "1 Year Ago", "President": "Not Saying", "Education": "Not Saying", "Email": "- Private -", "Ethnicity": "Not Saying", "Occupation": "Not Saying"}
		user['Id'] = str(self.name)
		for tr in BeautifulSoup(str(table),'html.parser').find_all('tr'):
			trbs = BeautifulSoup(str(tr),'html.parser')
			item = trbs.find('td',{'class':'c1'})
			if item == None: break
			item = trbs.find('td',{'class':'c1'}).text.encode('utf-8')[:-1]
			value = trbs.find('td',{'class':'c2'}).text.encode('utf-8')
			user[item] = value
			item = trbs.find('td',{'class':'c4'}).text.encode('utf-8')[:-1]
			value = trbs.find('td',{'class':'c5'}).text.encode('utf-8')
			user[item] = value
		return json.dumps(user)
		

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
		yesvote,yestext = self.parse_list(yes_list,'Yes') 
		novote,notext = self.parse_list(no_list,'No')
		if len(yesvote) == 0 or len(novote) == 0:
			print 'nothing to save',len(yesvote),len(novote) 
		else:
			#self.save(yesvote + novote,'./votes')
			self.save(yestext + notext,'./text')

	def save(self,votes,filename):
		output = open(filename,'a+')
		output.write('\n'.join(votes)+'\n')
		output.close()
	
		
	def parse_list(self,content,flag):
		ans = []
		text = []
		for vote in BeautifulSoup(str(content),"html.parser").find_all('li',{'class':'hasData'}):
			cite = vote.div.cite
			user = None
			if cite.a != None:
				user = cite.a.text
				text.append(self.get_text(vote,flag))
				ans.append(' '.join([self.topic,flag,str(user).strip()]))
				continue
		return ans,text

	def get_text(self,vote,flag):
		cit = {}
		cit['did']=str(vote['did'])
		cit['title']=self.topic
		cit['aid']=str(vote['aid'])
		cit['name']=str(vote.div.cite.a.text).strip()
		cit['point']=flag
		cit['text']=vote.p.text.encode('utf-8')
		return json.dumps(cit)
			

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


def multi_fetch(f,_list):
	pool = Pool(7,init_worker)
	try:
		threads = [pool.apply_async(f,(index,t,)) for index,t in enumerate(_list[:])]
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

def getUserDetail(index,n):
	c = UserCrawl(index,n)
	c.crawl()

if __name__ == '__main__':
	
	#main()
	#content = ''.join(open('tmp').readlines())
	#gettopic(content)
	#title = '/opinions/should-donald-trump-be-the-president'
	#title = '/opinions/are-conservatives-job-killers'
	#c = TopicCrawl(0,title)
	#c.analyse(content)
	#getTopicVote(0,title)
	#topics = ['opinions/'+line.strip() for line in open('./query').readlines()]
	names = [line.strip() for line in open('./user').readlines()]
	
	
	#for index,t in enumerate(topics[1:10]):
	#	getTopicVote(index,t)

	

	#multi_fetch(getTopicVote,topics[:])
	
	c = UserCrawl(1,'addie_prae')
	
	c.crawl()
	#c.getuser(content)
	#for index,t in enumerate(names[:10]):
	#	getUserDetail(index,t)
	#multi_fetch(getUserDetail,names[:])
