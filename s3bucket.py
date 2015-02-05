#!/usr/bin/env python

#
#	Author: historypeats <iam.historypeats@gmail.com>
#	Description: This tool can be used to audit your S3 Buckets
#	To find out what buckets and files have publicly exposed read permissions
#
#	Requirements: 
#		- boto 
#		- blessings
#

from boto.s3.connection import S3Connection, S3ResponseError
from blessings import Terminal
from Queue import Queue
from threading import Thread
import sys

def usage():
	print 'usage: {0} bucket_name'.format(sys.argv[0])


def getKeys(bucket):
	try:
		t = Terminal()
		keys = list()
		
		print '[+] Getting keys for bucket {0}'.format(bucket)
		
		conn = S3Connection()
		bucket = conn.get_bucket(bucket)
		kObject = bucket.list()

		for key in kObject:
			keys.append(key)

		return keys
	except KeyboardInterrupt:
		print t.red + '[!] ^C entered. Exiting.' + t.normal
		sys.exit(-1)
	except:
		
		print t.red + '[!] Unknown error in getKeys()' + t.normal
		sys.exit(-1)


def find_public(q, resultsQ):
	while True:
		try:
			t = Terminal()
			key = q.get()

			for auth in key.get_acl().acl.grants :
					if auth.permission == 'READ' :
						print 'public: {0}'.format(str(key.name))
						resultsQ.put('public: {0}'.format(str(key.name)))
			
			q.task_done()

		except S3ResponseError:
			print t.red + 'error: Key does not exist: {0}'.format(str(key.name)) + t.normal
			resultsQ.put('error: Key does not exist: {0}'.format(str(key.name)))

			q.task_done()

		except:
			print t.red + '[!] Unknown error in find_public() with key: {0}'.format(str(key.name)) + t.normal
			resultsQ.put('unknown: Uknown error in find_public() with key: {0}'.format(str(key.name)))

			q.task_done()
		

def writeResults(resultsQ):
	fd = open('test.results', 'a')
	while not resultsQ.empty():
		fd.write(resultsQ.get() + "\n")
		resultsQ.task_done()
	
	fd.close()

def main():
	if len(sys.argv) < 2:
		usage()
		t = Terminal()
		print t.red + '[+] Missing bucket name' + t.normal
		sys.exit(-1)

	rbucket = sys.argv[1]

	num_threads = 10
	q = Queue(maxsize=0)

	# For storing results and printing
	resultsQ = Queue(maxsize=0)

	# Get list of keys from Bucket
	keys = getKeys(rbucket)

	# Put keys into Queue and get length
	for key in keys:
		q.put(key)


	'''
	for i in range(30):
		q.put(keys[i])
		qSize += 1
	'''

	# Start threads
	for i in range(num_threads):
		worker = Thread(target=find_public, args=(q, resultsQ, ))
		worker.setDaemon(True)
		worker.start()

	# Wait for threads to finish
	q.join()
	print 'Q threads finished'

	print 'starting write threads...'
	t = Thread(target=writeResults, args=(resultsQ,))
	t.setDaemon(True)
	t.start()

	resultsQ.join()

	print '[+] {0} keys found.'.format(str(keys))

if __name__ == '__main__':
	main()
