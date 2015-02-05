#!/usr/bin/env python

#
#		Author: historypeats <iam.historypeats@gmail.com>
#	Description: This tool can be used to audit your S3 Buckets
#	To find out what buckets and files have publicly exposed read permissions
#
#	Requirements: 
#		- boto - pip install boto
#		- blessings - pip install blessings
#

from boto.s3.connection import S3Connection, S3ResponseError
from blessings import Terminal
from Queue import Queue
from threading import Thread
import sys
import argparse


# 
#	Threading Classes
#
class WriteThread(Thread):
	''' This class handles threading for writing the results to a file '''

	def __init__(self, resultsQueue, filename='s3audit.results'):
		''' Constructor '''
		Thread.__init__(self)
		self.results = resultsQueue
		self.filename = filename


	def writeResult(self, result):
		with open(self.filename, 'a') as fd:
			fd.write('{0}\n'.format(result))


	def run(self):
		while True:
			self.result = self.results.get()
			self.writeResult(self.result)
			self.results.task_done()



class S3Thread(Thread):
	''' This class handles threading for retrieving S3 information '''

	def __init__(self, keyQueue, resultsQueue):
		''' Constructor '''
		Thread.__init__(self)
		self.keys = keyQueue
		self.results = resultsQueue


	def findPerms(self, key):
		try:
			t = Terminal()
			message = ''
			wmessage = ''

			for auth in key.get_acl().acl.grants:
				if auth.permission == 'READ':
					message = 'public: {0}'.format(str(key.name))
					wmessage = message

		except S3ResponseError:
			message = t.red +'error: Key does not exist: {0}'.format(str(key.name)) + t.normal
			wmessage = 'error: Key does not exist: {0}'.format(str(key.name))

		except:
			message = t.red + 'unknown: Uknown error in find_public() with key: {0}'.format(str(key.name)) + t.normal
			wmessage = 'unknown: Uknown error in find_public() with key: {0}'.format(str(key.name))

		finally:
			print message
			self.results.put(wmessage)


	def run(self):
		while True:
			self.key = self.keys.get()
			self.findPerms(self.key)
			self.keys.task_done()


#
#	Utility
#
def usage():
	''' Print usage '''
	print 'usage: {0} bucket_name'.format(sys.argv[0])


#
#	Functions
#
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
		sys.exit(t.red + '[!] ^C entered. Exiting.' + t.normal)
	except:
		sys.exit(t.red + '[!] Unknown error in getKeys()' + t.normal)


#
#	Main
#
def main():
	''' Main '''

	if len(sys.argv) < 2:
		usage()
		t = Terminal()
		print t.red + '[+] Missing bucket name' + t.normal
		sys.exit(-1)

	rbucket = sys.argv[1]

	num_threads = 10
	keyQueue = Queue(maxsize=0)

	# For storing results and printing
	resultsQueue = Queue(maxsize=0)

	# Get list of keys from Bucket
	keys = getKeys(rbucket)

	# Put keys into Queue and get length
	'''
	for key in keys:
		keyQueue.put(key)

	'''
	
	# Remove this... for DEBUG 30 keys
	for i in xrange(30):
		keyQueue.put(keys[i])
	

	# Start S3 threads
	for t in xrange(num_threads):
		worker = S3Thread(keyQueue, resultsQueue)
		worker.setDaemon(True)
		worker.start()

	# Wait for threads to finish
	keyQueue.join()

	# Start Write Thread
	worker = WriteThread(resultsQueue)
	worker.setDaemon(True)
	worker.start()

	# Wait for threads to finish
	resultsQueue.join()

	print '[+] {0} keys found.'.format(str(len(keys)))


if __name__ == '__main__':
	main()
