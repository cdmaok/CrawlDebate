#coding=utf-8

## this file to check the miss data

import json
import pandas as pd


def find_miss():
	content = [str(json.loads(line.strip())['Id']) for line in open('./detailuser').readlines()]

	names = [line.strip() for line in open('./user').readlines()]

	print len(content)
	print len(names)
	print [name for name in names if name not in content]


def process():
	def bs2age(x):
		if x != '?':
			x = 2007 - int(x) + 1
		return x	
	df = pd.read_csv('/home/yangying/CrawlDebate/user.csv')
	df['Age'] = df['Birthday'].apply(bs2age)
	cols = df.columns.values.tolist()
	index = cols.index('Birthday')
	del cols[index]
	df = df[cols]
	df = df.ix[df['Party'].isin(['Democratic Party','Republican Party'])]
	df.to_csv('./tt.csv',index=False)
	


if __name__ == '__main__':
	process()

