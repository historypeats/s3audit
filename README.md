#S3audit

This is a tool to help audit your AWS S3 bucket permissions. It uses the boto framework to authenticate to AWS and enumerate all keys (files/directories). After accumulating a list of keys, it checks the permissions of each one, displaying keys that allow read acess to the public.

##Installation
1. First download or clone the repo.
```bash
git clone https://github.com/historypeats/s3audit.git
```
2. Next install the requirements with pip.
```bash
pip install -r requirements.txt
```
Note: You may need to use sudo if you are not using virtualenv.
3. Finally, invoke the s3audit script.
```bash
./s3audit -h
```

##Usage
```bash
usage: s3audit [-h] [-o OUTFILE] [-t THREADS] bucket

S3 Auditing Tool

positional arguments:
  bucket      The S3 bucket to audit.

optional arguments:
  -h, --help  show this help message and exit
  -o OUTFILE  The output file.
  -t THREADS  How many threads to use.
```
Note: The only required argument is the bucket to scan. The outfile, by default, will produce a file called s3audit.results. This file is grepable. Additionally, the default amount of threads is set to 10.
