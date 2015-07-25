#coding=utf-8
import os
import time
import urllib2
import sys
from bs4 import BeautifulSoup
import socket
from Indexbuild import IndexBuilder

class crawl:
	baseurl=''
	req_header = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
	req_timeout = 5
	urlqueue=[]
	urls=[]
	indegree=[]
	outdegree=[]
	length = []
	head=[]
	totalcount=0
	count=0
	read_web=set()
	
	def __init__(self,baseurl):#将主网址加入集合
		self.baseurl=baseurl
		self.indexbuilder = IndexBuilder()

	
	def user_agent(self,url): #宽度优先遍历网页
		while self.count < 1000:
			try:
				if(url in self.read_web):
					try:
						self.indegree[self.urls.index(url)]+=1
					except:
						pass
				else:
					self.read_web.add(url)
					tmpoutdegree=0
					print("it's the %d time"%(self.count))
					self.count=self.count+1#搜索网页数
					req = urllib2.Request(url,None,self.req_header)
					page = urllib2.urlopen(req,None,self.req_timeout)
					html = page.read()
					page.close()
					soup = BeautifulSoup(html)			
					self.urls.append(url)
					self.indegree.append(1)

					self.length.append(self.indexbuilder.process(soup,len(self.urls)-1))

					a = soup.find_all(['a'])
					for i in a:
						tmpurl=i.get('href')
						if(tmpurl is not None and tmpurl.find('javascript')==-1):
							if(tmpurl.find('http')==-1):
								tmpurl=self.baseurl+'/'+tmpurl
							if(tmpurl.find('www.cc98.org')!=-1):
								# print(tmpurl)
								self.urlqueue.append(tmpurl)
								tmpurl=''
								tmpoutdegree=tmpoutdegree+1
					#c=raw_input()
					self.outdegree.append(tmpoutdegree)
					time.sleep(0.2)
			except urllib2.URLError as e:
				print type(e), e.message, e.args
				print url
			except socket.timeout as e:
				print type(e), e.message, e.args
				print url
			except Exception as e:
				print e
				print url
			if(len(self.urlqueue)>0):
				url=self.urlqueue.pop(0);
			#结束了
		self.indexbuilder.save()
		with open('queue','w') as qq:
			print('Writing queue back into file...')
			for item in self.urlqueue:
				try:
					if(item is not None):
						qq.write(item+'\n')
				except:
					print ('queue wrong but things well')
					pass
	
		with open('urllist','w') as uu:
			uu.write('%d\n'%(len(self.urls)))
			i=0
			print('Writing urllist back into file...')
			for item in self.urls:
				try:
					uu.write('%d %s %d %d %d\n'%(i, item, self.indegree[i], self.outdegree[i], self.length[i]))
					i+=1
				except:
					print('%d %s %d %d %d\n'%(i, item, self.indegree[i], self.outdegree[i], self.length[i]))
					print ('urls output wrong')
					pass
			#return html

	def fillset(self,urllist,queue):#将以前访问过的网站加入set，重新获取queue
		with open(urllist,'r') as FILE:
			totalcount=FILE.readline()
			for item in FILE.readlines():
				try:
					(tmpid,tmpurl,tmpind,tmpoud,tmplen)=(item.strip('\n').split(' '))
					self.urls.append(tmpurl)
					self.read_web.add(tmpurl)
					self.indegree.append(int(tmpind))
					self.outdegree.append(int(tmpoud))
					self.length.append(int(tmplen))
				except:
					print('read in data error')

		with open(queue,'r') as FILE1:
			for item in FILE1.readlines():
				try:
					self.urlqueue.append(item.strip('\n'))
				except:
					print('read queue in error but well')
		self.baseurl=self.urlqueue.pop(0)#重设主网址

#main
if __name__ == '__main__':
		baseurl="http://www.cc98.org"
		cc=crawl(baseurl)
		if(os.path.exists('urllist') and os.path.exists('queue')):
			cc.fillset('urllist','queue') #检查是否继续上次爬取
			cc.user_agent(cc.baseurl)
		else:
			cc.user_agent(baseurl)
