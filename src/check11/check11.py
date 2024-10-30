#!/usr/bin/env python

import requests
import os
import sys
import subprocess
import re
import time
from colorama import Fore
from colorama import Style

def help():
	print(f"{Fore.GREEN}How to use check11: {Fore.BLUE}{Style.BRIGHT}check11 /absolute/path/to/dir/with/assignments/ {Style.RESET_ALL}")
	print(f"{Fore.GREEN}Use check11 in current working directory: {Fore.BLUE}{Style.BRIGHT}check11 -c {Style.RESET_ALL}")
	print(f"{Fore.GREEN}For help: {Fore.BLUE}{Style.BRIGHT}check11 -h {Style.RESET_ALL}")
	print(f"{Fore.GREEN}Additional, for no traceback: {Fore.BLUE} --t{Style.RESET_ALL}")
	print(f"{Fore.GREEN}Additional, for errors only: {Fore.BLUE} --e{Style.RESET_ALL}")
	print(f"{Fore.GREEN}Additional, for clearing prompt: {Fore.BLUE} --p{Style.RESET_ALL}")
	print(f"{Fore.GREEN}Additional, for no traceback and errors only: {Fore.BLUE} --te{Style.RESET_ALL}")
	print(f"{Fore.GREEN}Example: {Fore.BLUE}check11 --etp -c{Style.RESET_ALL}")
	print(f"{Fore.GREEN}Example: {Fore.BLUE}check11 --pt /absolute/path/to/dir/with/assignments/{Style.RESET_ALL}")

def read_cmd() -> dict:
	# read the commands in versatile way:
	# check11 -c or -C or -current ==> for assignment == current working dir
	# check11 -h or -H or -help ==> for help
	# check11 /abs/path/to/assignment/dir
	# check11 --t /abs/path/to/assignment/dir ==> no traceback 
	# check11 --e /abs/path/to/assignment/dir ==> errors only
	no_trace = False
	errors_only = False
	clear_prompt = False
	apath = None
	counter = 0
	
	for a in sys.argv:
		a = a.strip()
		if a == "":
			continue
		if a.endswith("check11"):
			counter += 1
			continue
		if a.lower() in ['-h', '-help']:
			help()
			sys.exit()
		if a.startswith('/') and os.path.isabs(a):
			if apath is None:
				apath = a
				counter += 1
				continue
			else:
				# two paths?
				help()
				sys.exit()
		if a.lower() in ['-c', '-current']:
			if apath is None:
				apath = os.getcwd()
				counter += 1
				continue
			else:
				# paths and cwd?
				help()
				sys.exit()
		if a.startswith('--'):
			try:
				extra_args = a.split('--')[1]
			except:
				# no args after --
				help()
				sys.exit()
			if 't' in extra_args:
				no_trace = True
			if 'e' in extra_args:
				errors_only = True
			if 'p' in extra_args:
				clear_prompt = True
			counter += 1
				
	# end sys.argv for
	if len(sys.argv) != counter:
		help()
		sys.exit()
	if apath is None:
		help()
		sys.exit()	

	return apath, no_trace, errors_only, clear_prompt
	

class CheckAssignment:
	_BASEURL = 'http://127.0.0.1:5000' #'https://cpnits.com/check11' 
    # 'http://127.0.0.1:5000' #
	_MAXSIZE = 1024 * 1024

	def __init__(self, path: str, no_trace: bool, errors_only: bool, clear_prompt: bool):
		self._git_alias = self.get_git_alias()
		if self._git_alias is None:
			print("No valid GIT account.")
			return False
		self._no_trace = no_trace
		self._errors_only = errors_only
		self._clear_prompt = clear_prompt
		self._this_path = path
		self._assignment = os.path.basename(self._this_path)

	def safename(self, erin: str):
		erin = str(erin)
		return re.sub(r'[^a-zA-Z0-9_\.]', '', erin, flags=re.I|re.M).lower()

	def sleepdot(self, n: int):
		print(f"{Fore.CYAN}.{Style.RESET_ALL}", end='', flush=True)
		for i in range(n*10):
			print(f"{Fore.CYAN}.{Style.RESET_ALL}", end='', flush=True)
			time.sleep(0.1)
		print()

	# prints report to prompt
	def print_report(self):
		for line in self.results:
			print(line)

	# get git info from project
	def get_git_alias(self) -> str|None:
		try:
			res = subprocess.run(["git", "config", "user.email"], stdout=subprocess.PIPE)
			git_data = res.stdout.strip().decode()
			git_alias = git_data.split('@')[0].strip()
			# print('GET GIT DATA', git_alias)
			return git_alias
		except:
			return None

	# get about data with filenames for upload
	def get_filenames(self) -> list|int:
		url = f"{self._BASEURL}/about/{self._git_alias}/{self._assignment}"
		r = requests.get(url)
		# print(url)
		if not r.status_code == 200:
			return r.status_code
		try:
			fn = r.json()['filenames']
			# print('GET FILENAMES', fn)
			return fn
		except:
			return 1

	# collect local files in dict of binaries
	def get_local_files(self, this_path: str, allowed_filenames: list) -> dict:
		files = dict()
		for f in os.listdir(this_path):
			fpath = os.path.join(this_path, f)

			if not os.path.isfile(fpath):
				continue
			if not f in allowed_filenames:
				continue

			# print(f, os.stat(fpath).st_size)
			if os.stat(fpath).st_size > self._MAXSIZE:
				print(f"Skipping {f}: too large")
				continue

			# open and upload
			target_fp = open(fpath, 'rb')
			files[f] = target_fp
		# print('GET FILES', files)
		return files

	# upload files to remote
	def upload_files(self, files: dict) -> bool:
		target_url = f"{self._BASEURL}/upload/{self._git_alias}/{self._assignment}"
		response = requests.post(
			target_url,
			files=files,
		)
		# print('UPLOAD FILES', response.status_code)
		return response.status_code == 200

	# starts remote testing, gets back results
	def remote_testing(self) -> list|None:
		target_url = f"{self._BASEURL}/test/{self._git_alias}/{self._assignment}"
		data = dict(
			no_trace=self._no_trace,
			errors_only=self._errors_only		
		)
		try:
			response = requests.post(target_url, json=data)
		except:
			print(f"Error with remote testing. Bad luck, or bad code.")
			return None
		try:
			return response.json()['test_results']
		except:
			print(f"{self._assignment}: no test results available. Try again later.")
			return None

	def run(self) -> bool:
		# get GIT alias from email address
		if self._git_alias is None:
			print("No valid GIT account")
			return False
		
		if self._clear_prompt:
			os.system('cls' if os.name == 'nt' else 'clear')

		# name of project, part of path
		print(f"{Fore.CYAN}Building test for {Style.BRIGHT}{self._assignment}{Style.NORMAL}.{Style.RESET_ALL}")

		# send request to check11 for requested files for this assignment
		allowed_filenames = self.get_filenames()
		if isinstance(allowed_filenames, int):
			# foutcode terug
			if allowed_filenames == 401:
				print(f"{Fore.LIGHTRED_EX}Your github alias {self._git_alias} does not have access to Check11 --error [{allowed_filenames}] --status [{allowed_filenames}].{Style.RESET_ALL}")
			elif allowed_filenames == 403:
				print(
					f"{Fore.LIGHTRED_EX}It looks like the Check11 server is down. Try again later --error [{allowed_filenames}] --status [{allowed_filenames}].{Style.RESET_ALL}")
			else:
				print(f"{Fore.LIGHTRED_EX}{self._assignment} is not a testable assignment --error [{allowed_filenames}] --status [{allowed_filenames}].{Style.RESET_ALL}")
			return False
		print(f"{Fore.CYAN}Looking for python files {Style.BRIGHT}{allowed_filenames}{Style.NORMAL}.{Style.RESET_ALL}")

		# find python files in path
		files = self.get_local_files(self._this_path, allowed_filenames)
		if len(files) == 0:
			print(f"{self._assignment}: no files here valid for uploading. Are you working from the right directory?")
			return False
		print(f"{Fore.CYAN}Found python files {Style.BRIGHT}[{', '.join(files.keys())}]{Style.NORMAL}.{Style.RESET_ALL}")

		# ready for uploading files
		if not self.upload_files(files):
			print(f"{self._assignment}: no files were uploaded. Check your internet connection.")
			return False
		print(f"{Fore.CYAN}Uploading files for {Style.BRIGHT}{self._assignment}{Style.NORMAL} to Check11.{Style.RESET_ALL}")

		# pause for API-server needs to process files
		self.sleepdot(5)
		self.results = self.remote_testing()
		if self.results is None:
			return False

		self.print_report()
		return True
	
def run():
	path, nt, eo, cp = read_cmd()
	check11 = CheckAssignment(path, nt, eo, cp)
	check11.run()
