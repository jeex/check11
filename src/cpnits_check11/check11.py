#!/usr/bin/env python

import requests
import os
import sys
import subprocess
import re
import time
from colorama import Fore
from colorama import Style

# paths and mods
# PARENT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append(PARENT)
import importlib

from cpnits_check11.base_test import ApiTest, BaseTest

VERSION = '0.1.0'
APP_NAME = 'cpnits_check11'

def help(short=True):
	if short:
		print(f"Type {Fore.BLUE}{Style.BRIGHT}check11 -h{Style.NORMAL}{Fore.RESET} for a brief howto.{Style.RESET_ALL}")
	else:
		print(f"How to use check11: \n\t{Fore.LIGHTRED_EX}{Style.BRIGHT}check11 /absolute/path/to/dir/with/assignment/ {Style.RESET_ALL}")
		print(f"\tor {Fore.LIGHTRED_EX}{Style.BRIGHT}check11 relative/path/with/assignment/ {Style.RESET_ALL}")
		print(f"\tor in current working directory: {Fore.LIGHTRED_EX}{Style.BRIGHT}check11 -c {Style.RESET_ALL}")
		print()
		print(f"For help: {Fore.LIGHTRED_EX}{Style.BRIGHT}check11 -h {Style.RESET_ALL}")
		print(f"Additional arg for no traceback: {Fore.LIGHTRED_EX}{Style.BRIGHT} --t{Style.RESET_ALL}")
		print(f"Additional arg for errors only: {Fore.LIGHTRED_EX}{Style.BRIGHT} --e{Style.RESET_ALL}")
		print(f"Additional arg for clearing prompt: {Fore.LIGHTRED_EX}{Style.BRIGHT} --p{Style.RESET_ALL}")
		print(f"Combined args for no traceback and errors only: {Fore.LIGHTRED_EX}{Style.BRIGHT} --te{Style.RESET_ALL}")
		print()
		print(f"Example (assignment in current dir, errors only, no traceback, clear prompt): \n\t{Fore.LIGHTRED_EX}{Style.BRIGHT}check11 --etp -c{Style.RESET_ALL}")
		print(f"Example (assignment in relative dir assignment, clear prompt): \n\t{Fore.LIGHTRED_EX}{Style.BRIGHT}check11 --p assignment/{Style.RESET_ALL}")


def read_cmd() -> dict:
	# read the commands in versatile way:
	# check11 assignmentname -c or -C or -current ==> for assignment == current working dir
	# check11 assignmentname-h or -H or -help ==> for help
	# check11 assignmentname /abs/path/to/assignment/dir
	# check11 assignmentname --t /abs/path/to/assignment/dir ==> no traceback 
	# check11 assignmentname --e /abs/path/to/assignment/dir ==> errors only
	no_trace = False
	errors_only = False
	clear_prompt = False
	apath = None
	counter = 0
	aname = None
	
	for i in range(len(sys.argv)):
		a = sys.argv[i].strip()
		
		# skip program call
		if i == 0:
			counter += 1
			continue
		
		# name of the assignment
		if i == 1:
			aname = sys.argv[i].strip()
			counter += 1
			continue

		## The rest of the args can come in any order
		
		# help, ignore the rest
		if a.lower() in ['-h', '-help']:
			help(short=False)
			sys.exit()
		# abs path 
		
		if a.startswith('/') and os.path.isabs(a):
			if not apath is None:
				# two paths?
				help()
				sys.exit()				
			apath = a
			counter += 1
			continue	
		
		# relative path can be any word not...
		if not a.startswith(("-", "/",)) and not a.endswith(("check11", "check11.py",)):
			if not apath is None:
				# two paths?
				help()
				sys.exit()
			tpath = os.path.abspath(a)
			if os.path.isdir(tpath):
				apath = tpath
				counter += 1
				continue
			else:
				help()
				sys.exit()
				
		# -c current directory path
		if a.lower() in ['-c', '-current']:
			if not apath is None:
				# paths and cwd?
				help()
				sys.exit()				
			apath = os.getcwd()
			counter += 1
			continue

		if a.startswith('--'):
			try:
				extra_args = a.split('--')[1]
			except:
				# no args after --
				help()
				sys.exit()
			if not extra_args.isalpha():
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
	if apath is None or aname is None:
		help()
		sys.exit()	

	return apath, aname, no_trace, errors_only, clear_prompt
	

class TestAssignment:
	_BASEURL = 'https://cpnits.com/check11'
	# 'https://cpnits.com/check11' 
	# 'http://127.0.0.1:5000' #
	_MAXSIZE = 1024 * 1024

	def __init__(self, path: str, aname: str, no_trace: bool, errors_only: bool, clear_prompt: bool):
		self._git_alias = self.get_git_alias()
		if self._git_alias is None:
			print("No valid GIT account.")
			return False
		self._no_trace = no_trace
		self._errors_only = errors_only
		self._clear_prompt = clear_prompt
		self._this_path = path
		self._assignment = aname


	def safename(self, erin: str):
		erin = str(erin)
		return re.sub(r'[^a-zA-Z0-9_\.]', '', erin, flags=re.I|re.M).lower()


	# gets the user module that needs to be tested
	def get_user_mod(self, filename):
		umodspec = importlib.util.spec_from_file_location(filename, os.path.join(self._this_path, f"{filename}.py"))
		umod = importlib.util.module_from_spec(umodspec)
		umodspec.loader.exec_module(umod)
		return umod

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

	
	# get permission for testing AND VERSION
	def remote_get_permission(self) -> int:
		url = f"{self._BASEURL}/permission/{self._git_alias}/{self._assignment}"
		try:
			r = requests.get(url)
			code = int(r.status_code)
			rj = r.json()
			version = rj['r']['version']
			permission = rj['r']['permission']
		except:
			print(f"{Fore.LIGHTRED_EX}{self._assignment} is not a testable assignment --status [211].{Style.RESET_ALL}")
			return False
		
		if code == 200:
			if version != VERSION:
				print(f"{Fore.LIGHTRED_EX}{self._assignment} download a new version TODO.{Style.RESET_ALL}")
				return False
			
			if permission != self._git_alias:
				print(f"{Fore.LIGHTRED_EX}Your github alias {self._git_alias} does not have access to Check11 --status [{code}].{Style.RESET_ALL}")
				return False
			
			return True
			
		elif code == 401:
			print(f"{Fore.LIGHTRED_EX}Your github alias {self._git_alias} does not have access to Check11 --status [{code}].{Style.RESET_ALL}")
			return False
		elif code == 403:
			print(f"{Fore.LIGHTRED_EX}It looks like the Check11 server is down. Try again later --status [{code}].{Style.RESET_ALL}")
			return False
		else:
			print(f"{Fore.LIGHTRED_EX}{self._assignment} is not a testable assignment --status [{code}].{Style.RESET_ALL}")
			return False		
	
	
	# retreive info about assignment and testable files
	def get_about_assignment(self) -> bool:
		about_path = f"{APP_NAME}.{self._assignment}.about"
		try:
			aboutmod = importlib.import_module(about_path, package=None)
		except Exception as e:
			print(f"{e} = {about_path}")
			return False	
		self._allowed_filenames = aboutmod.allowed_filenames()	
	
	
	# find the user files for testing
	def get_local_filenames(self):
		files = list()
		for f in os.listdir(self._this_path):
			fpath = os.path.join(self._this_path, f)
			if not os.path.isfile(fpath):
				continue
			if not f in self._allowed_filenames:
				continue
			files.append(f)
		self._found_filenames = files
	
	
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
		if not self.remote_get_permission():
			return False
		
		self.get_about_assignment()
		print(f"{Fore.CYAN}Looking for python files {Style.BRIGHT}{self._allowed_filenames}{Style.NORMAL}.{Style.RESET_ALL}")

		# find filenames for testing at user dir
		self.get_local_filenames()
		print(f"{Fore.CYAN}Python files ready for testing: {Style.BRIGHT}[{', '.join(self._found_filenames)}]{Style.NORMAL}.{Style.RESET_ALL}")
		
		for fn in self._found_filenames:
			fname = fn.replace('.py', '')
			api = ApiTest(self._git_alias, self._this_path, self._assignment, fname, self._no_trace, self._errors_only)
			if api.utestmod is None or api.test_o is None:
				print(f"{Fore.CYAN}Testing : {Style.BRIGHT}{self._assignment}.{fname}{Style.NORMAL} failed.{Style.RESET_ALL}")
				continue
			self.results = api.run_utest()
			self.print_report()
			
		return True
	
def run():
	path, an, nt, eo, cp = read_cmd()
	# TODO check version online
	check11 = TestAssignment(path, an, nt, eo, cp)
	check11.run()
