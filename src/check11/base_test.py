import math
import re
import sys
import os
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
import io
import traceback
import importlib
import importlib.util
from math import isclose

from unittest.mock import patch, Mock
import contextlib
import pytest

APP_NAME = 'check11'

class TestItem:
	def __init__(self):
		self._msg = None
		self._trace = None
		self._result = None

	def passed(self, b: bool):
		self._result = b

	def set_msg(self, msg):
		self._msg = msg

	def set_trace(self, trace):
		self._trace = trace

	def get_msg(self):
		return self._msg

	def get_trace(self):
		return self._trace

	def is_passed(self):
		return self._result

class TestSingle:
	def __init__(self, description: str):
		self.desc = description
		self.items = list()
		self.current_item = None

	def get_desc(self):
		return self.desc

	def get_items(self):
		return self.items

	def has_items(self):
		return len(self.items) > 0

	def new_item(self) -> TestItem:
		self.current_item = TestItem()
		self.items.append(self.current_item)
		return self.current_item

	def current(self):
		return self.current_item

class BaseTest: # for a complete module with more functions and tests

	def __init__(self):
		# super().__init__()
		# self.check_file()
		# self.set_functions(['keer', 'reverse', 'argss', 'multi', 'raise_an_error', 'eruut', 'main'])		
		self.gitname = None
		self.modpath = ""
		self.aname = ''  # assignmentname
		self.modname = ''
		self.functions = dict()
		self.tests = list()
		self.mod = None
		self.no_trace = True
		self.errors_only = True

	def runrun(self):
		method_list = [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith("__")]
		for method in method_list:
			if not method.startswith('test_'):
				continue
			func = getattr(self, method)
			func()

	def make_testname(self, testname, funcname):
		return f"{Style.BRIGHT}{funcname}{Style.NORMAL}() {testname}"

	def get_linux_path(self, s: str) -> str|None:
		# returns a list with paths if found in string
		pattern = '\"/(.*?)\"'
		res = re.findall(pattern, s, re.I|re.M)
		if len(res) == 0:
			return None
		return '/'+res[0]

	def traceback_on_exception(self) -> list:
		# moet de output beperken tot relevante regels
		myFile = io.StringIO()
		traceback.print_exc(file=myFile)
		# foutmelding
		lines = myFile.getvalue()
		lines = lines.split('\n')
		lines.reverse()
		relevant = True
		rlines = list()
		for i in range(len(lines)):
			if not relevant:
				continue

			lpath = self.get_linux_path(lines[i])
			if lpath is None:
				# houd line in lijst
				rlines.append(lines[i])
				continue

			# na eerste linux-path, relevance stopt
			if not 'utest.py' in lpath and not 'base_test.py' in lpath and not 'assert' in lpath and not 'AssertionError' in lpath:
				# laatste relevante regel
				shortpath = lpath.split('/')[-1]
				line = lines[i].replace(lpath, f"/{shortpath}").strip()
				line = line.replace("\t", "").replace("  ", " ").replace("\n", "")
				if line.isspace():
					continue
				rlines.append(line)
				relevant = False
		rlines.reverse()
		return rlines

	def caught_exception(self) -> str:
		e = traceback.format_exc()
		lines = e.splitlines()
		return lines[-1].strip()

	def set_functions(self, fnames: list):
		if self.mod is None:
			return
		pad = f"check11.{self.gitname}.{self.aname}.{self.modname}"
		for f in fnames:
			if not self.exists_function(f):
				continue
			try:
				self.functions[f] = getattr(self.mod, f)
			except:
				continue

	def set_argv(self, args: list):
		sys.argv = args

	def comargs_params_text(self, comargs: list, params: list, promptin: str|None) -> str:
		withwhat = ""
		withand = "with"
		if len(comargs) > 0:
			withwhat = f"with command line arguments {Style.BRIGHT}{comargs}{Style.NORMAL}"
			withand = " and"
		if len(params) > 0:
			withwhat = f"{withwhat}{withand} parameters {Style.BRIGHT}{params}{Style.NORMAL}"
			withand = " and"
		if not promptin is None:
			withwhat = f"{withwhat}{withand} prompt input {Style.BRIGHT}{promptin}{Style.NORMAL}"
			withand = " and"
		return withwhat

	def get_report(self) -> list:
		def all_passed(test):
			ap = True
			for testitem in test.get_items():
				ap = ap and testitem.is_passed()
			return ap

		u_on = "\033[4m"
		u_off = "\033[0m"
		newline = ""
		lines = [newline]
		count_passed = 0
		count_failed = 0

		line = f"{Style.BRIGHT}{Fore.BLUE}••••••••••••••• testing {self.modname}.py •••••••••••••••{Style.RESET_ALL}"
		lines.append(line)
		first = True
		for test in self.tests:
			ap = all_passed(test) or not self.errors_only
			if not test.has_items():
				continue
			if not first and not ap:
				lines.append(newline)
			first = False

			if not ap:
				lines.append(f"Tested: {test.get_desc()}")

			for testitem in test.get_items():
				if testitem.get_msg() is None:
					continue
				if testitem.get_msg() == '':
					continue

				if testitem.is_passed():
					count_passed += 1
					if not self.errors_only:
						lines.append(f"\t{Fore.GREEN}PASSED::{Style.RESET_ALL} {testitem.get_msg()}")
				else:
					count_failed += 1
					lines.append(f"\t{Fore.RED}FAILED:: {testitem.get_msg()}{Style.RESET_ALL}")

				if self.no_trace:
					continue
				if testitem.get_trace() is None:
					continue
				if len(testitem.get_trace()) == 0:
					continue

				lines.append(newline)
				lines.append(f"\t------------ traceback ------------")
				for line in testitem.get_trace():
					lines.append(f"\t{line}")
				lines.append(f"\t------------ end traceback --------")
				lines.append(newline)
			# end per testitem
		# end per test

		lines.append(f"{Fore.BLUE}••••••••••••••• finished {Fore.GREEN}tests passed: {count_passed}{Fore.RED} tests failed: {count_failed} {Fore.BLUE} •••••••••••••••{Style.RESET_ALL}")
		lines.append(newline)
		return lines

	def import_module_test_prompt(self, pad):
		with patch('builtins.input', lambda _: '--asked for input--'):
			try:
				mod = importlib.import_module(pad, package=None)
				return mod
			except:
				testname_plus = "testing for inchorent code"
				test = TestSingle(testname_plus)
				current_test = test.new_item()
				self.tests.append(test)
				m = f"{Fore.RED}file {Style.BRIGHT}{self.modname}.py{Style.NORMAL} has code that is not part of a function. Fix that by using the {Style.BRIGHT}main():{Style.NORMAL} function!{Style.NORMAL}"
				current_test.passed(False)
				current_test.set_msg(m)
				current_test.set_trace(self.traceback_on_exception())
				return None

	# ======== actual testing ============
	# SIMPLE test if value in, value out of function match, with single parameter
	def exists_function(self, fname: str) -> bool:
		testname_plus = f"function {fname} exists"
		test = TestSingle(testname_plus)
		self.tests.append(test)
		try:
			if not hasattr(self.mod, fname):
				current_test = test.new_item()
				current_test.passed(False)
				current_test.set_msg(f"function {Style.BRIGHT}{fname}(){Style.NORMAL} does not exist")
				return False
		except:
			current_test = test.new_item()
			current_test.passed(False)
			current_test.set_msg(f"function {Style.BRIGHT}{fname}(){Style.NORMAL} does not exist")
			return False
		return True

	def check_user_mod(self):
		# path to module
		path = os.path.join(self.modpath, f"{self.modname}.py")
		testname_plus = f"file {self.modname} exists"
		test = TestSingle(testname_plus)
		self.tests.append(test)
		
		# check if module file exists
		try:
			umodspec = importlib.util.spec_from_file_location(self.modname, path)
		except:
			current_test = test.new_item()
			current_test.passed(False)
			current_test.set_msg(f"file {Style.BRIGHT}{self.modname}.py{Style.NORMAL} is not available for testing")			
			current_test.set_trace(self.traceback_on_exception())
			self.mod = None
			return

		# check if syntax errors in module file
		try:
			umod = importlib.util.module_from_spec(umodspec)
			umodspec.loader.exec_module(umod)			
		except:
			current_test = test.new_item()
			current_test.passed(False)
			current_test.set_msg(f"file {self.aname}.{self.modname}.py has syntax error(s).")
			current_test.set_trace(self.traceback_on_exception())
			self.mod = None
			return
		# only apply if no errors
		self.mod = umod

	def assert_params_multi(self, funcname: str, pars: str, testvals: dict):
		if self.mod is None:
			return
		if not funcname in self.functions.keys():
			return
		modpy = f"{self.mod}.py"

		for testname in testvals:
			testname_plus = self.make_testname(testname, funcname)
			thistest = TestSingle(testname_plus)
			self.tests.append(thistest)

			for test in testvals[testname]:
				current_test = thistest.new_item()
				# first run function for runtime errors
				try:
					func = self.functions[funcname]
					r = func(test[0])
				except:
					m = f"runtime error in {Style.BRIGHT}{funcname}{pars}{Style.NORMAL} with parameter(s) {Style.BRIGHT}{test[0]}"
					current_test.passed(False)
					current_test.set_msg(m)
					current_test.set_trace(self.traceback_on_exception())
					return

				# assert output if no errors
				try:
					assert r == test[1]
				except AssertionError:
					m = f"{Style.BRIGHT}{funcname}{pars}{Style.NORMAL} with parameter(s) {Style.BRIGHT}{test[0]}{Style.NORMAL} EXPECTED output {Style.BRIGHT}{test[1]}{Style.NORMAL}, but RECEIVED {Style.BRIGHT}{r}{Style.NORMAL}"
					current_test.passed(False)
					current_test.set_msg(m)
					# current_test.set_trace(self.traceback_on_exception())
					return
				except:
					m = f"{Style.BRIGHT}{funcname}{pars}{Style.NORMAL} \n\twith parameter(s) {Style.BRIGHT}{test[0]}{Style.NORMAL} -- some other error occured, see traceback for details"
					current_test.passed(False)
					current_test.set_msg(m)
					current_test.set_trace(self.traceback_on_exception())
					return

				# show green test results
				m = f"{Style.BRIGHT}{funcname}{pars}{Style.NORMAL} with parameter(s) {Style.BRIGHT}{test[0]}{Style.NORMAL} RECEIVED {Style.BRIGHT}{r}{Style.NORMAL}"
				current_test.passed(True)
				current_test.set_trace(None)
				current_test.set_msg(m)

	# COMPLEX test with parameters, command line args
	def assert_params_comargs(self, funcname: str, pars: str, testname, expected, parameters, comargs, howclose=0.0):
		if self.mod is None:
			return
		if not funcname in self.functions.keys():
			return
		modpy = f"{self.mod}.py"

		testname_plus = self.make_testname(testname, funcname)
		test = TestSingle(testname_plus)
		current_test = test.new_item()
		self.tests.append(test)

		try:
			func = self.functions[funcname]
			r = func(*parameters)
		except:
			m = f"{Style.BRIGHT}{funcname}{pars}{Style.NORMAL} -- see traceback for details"
			current_test.passed(False)
			current_test.set_msg(m)
			current_test.set_trace(self.traceback_on_exception())
			return

		withwhat = self.comargs_params_text(comargs, parameters, None)

		try:
			if howclose > 0.0 :
				assert isclose(r, expected, rel_tol=howclose, abs_tol=0.0)
			else:
				assert r == expected
		except AssertionError:
			m = f"{Style.BRIGHT}{funcname}{pars}{Style.NORMAL} {withwhat} EXPECTED output {Style.BRIGHT}{expected}{Style.NORMAL}, but RECEIVED {Style.BRIGHT}{r}{Style.NORMAL}"
			current_test.passed(False)
			current_test.set_msg(m)
			# current_test.set_trace(self.traceback_on_exception())
			return

		except:
			m = f"{Style.BRIGHT}{funcname}{pars}{Style.NORMAL} -- some other error occurred, see traceback for details"
			current_test.passed(False)
			current_test.set_msg(m)
			current_test.set_trace(self.traceback_on_exception())
			return

		# test passed
		m = f"{Style.BRIGHT}{funcname}{pars}{Style.NORMAL} {withwhat} RECEIVED {Style.BRIGHT}{r}{Style.NORMAL}"

		# test passed
		current_test.passed(True)
		current_test.set_msg(m)
		return

	# test for raised errors in code
	def raise_error(self, funcname: str, pars: str, testname, expected, parameters, comargs):
		if self.mod is None:
			return
		if not funcname in self.functions.keys():
			return
		modpy = f"{self.mod}.py"

		testname_plus = self.make_testname(testname, funcname)
		test = TestSingle(testname_plus)
		current_test = test.new_item()
		self.tests.append(test)

		func = self.functions[funcname]
		try:
			r = func(*parameters)
			caught_exception = 'no error'
		except:
			caught_exception = self.caught_exception()

		withwhat = self.comargs_params_text(comargs, parameters, None)
		# test received error
		try:
			assert expected.lower() == caught_exception.lower()
			# passed test
		except AssertionError:
			# failed test
			m = f"raise error {Style.BRIGHT}{funcname}{pars}{Style.NORMAL} {withwhat} EXPECTED {Style.BRIGHT}{expected}{Style.NORMAL}, but RECEIVED {Style.BRIGHT}{caught_exception}{Style.NORMAL}"
			current_test.passed(False)
			current_test.set_msg(m)
			return
		except:
			m = f"{Style.BRIGHT}{funcname}{pars}{Style.NORMAL} {withwhat} -- some other error occurred, see traceback for details"
			current_test.passed(False)
			current_test.set_msg(m)
			current_test.set_trace(self.traceback_on_exception())
			return

		# passed
		m = f"raise error {Style.BRIGHT}{funcname}{pars}{Style.NORMAL} {withwhat} RECEIVED {Style.BRIGHT}{caught_exception}{Style.NORMAL}"
		current_test.passed(True)
		current_test.set_msg(m)
		return

	# test for proper exit message or value
	def sys_exit(self, funcname: str, pars: str, testname, expected, parameters, comargs):
		# test if program has sys.exit with proper exit value
		import contextlib
		if self.mod is None:
			return
		if not funcname in self.functions.keys():
			return
		modpy = f"{self.mod}.py"

		withwhat = self.comargs_params_text(comargs, parameters, None)

		func = self.functions[funcname]
		testname_plus = self.make_testname(testname, funcname)
		test = TestSingle(testname_plus)
		current_test = test.new_item()
		self.tests.append(test)

		try:
			with pytest.raises(SystemExit) as excinfo:
				func(*parameters)
			r = excinfo.value.code
		except AssertionError:
			# catch other errors
			m = f"{Style.BRIGHT}{funcname}{pars}{Style.NORMAL} {withwhat} -- see traceback for details"
			current_test.passed(False)
			current_test.set_msg(m)
			current_test.set_trace(self.traceback_on_exception())
			return
		except:
			m = f"{Style.BRIGHT}{funcname}{pars}{Style.NORMAL} {withwhat} -- some other error occurred, see traceback for details"
			current_test.passed(False)
			current_test.set_msg(m)
			current_test.set_trace(self.traceback_on_exception())
			return

		#  now test it with expected exit msg
		try:
			assert r == expected
		except AssertionError:
			m = f"{Style.BRIGHT}{funcname}{pars}{Style.NORMAL} {withwhat} EXPECTED exit message {Style.BRIGHT}{expected}{Style.NORMAL}, but RECEIVED exit message {Style.BRIGHT}{r}{Style.NORMAL}"
			current_test.passed(False)
			current_test.set_msg(m)
			return
		except:
			m = f"{Style.BRIGHT}{funcname}{pars}{Style.NORMAL} {withwhat} -- some other error occurred, see traceback for details"
			current_test.passed(False)
			current_test.set_msg(m)
			current_test.set_trace(self.traceback_on_exception())
			return

		m = f"{Style.BRIGHT}{funcname}{pars}{Style.NORMAL} {withwhat} has EXIT MESSAGE {Style.BRIGHT}{r}{Style.NORMAL}"
		current_test.passed(True)
		current_test.set_msg(m)
		return

	# test with possible prompt input output
	def input_and_or_output(self, funcname: str, pars: str, testname, expected, parameters, comargs, erin: str|None=None, eruit: str|None=None):
		if self.mod is None:
			return
		if not funcname in self.functions.keys():
			return
		modpy = f"{self.mod}.py"

		func = self.functions[funcname]
		testname_plus = self.make_testname(testname, funcname)
		test = TestSingle(testname_plus)
		current_test = test.new_item()
		self.tests.append(test)

		# erin PROMPT or not
		try:
			func = self.functions[funcname]
			if erin is None:
				if not eruit is None:
					f = io.StringIO()
					with contextlib.redirect_stdout(f):
						func(*parameters)
					r = f.getvalue()
					expected = eruit
					hoeuit = f"prompt output"
				else:
					r = func(*parameters)
					hoeuit = f"output"
			else:
				with patch('builtins.input', lambda _: erin):
					if not eruit is None:
						f = io.StringIO()
						with contextlib.redirect_stdout(f):
							func(*parameters)
						r = f.getvalue()
						expected = eruit
						hoeuit = f"prompt output"
					else:
						r = func(*parameters)
						hoeuit = f"output"
		except:
			m = f"{Style.BRIGHT}{funcname}{pars}{Style.NORMAL} -- see traceback for details"
			current_test.passed(False)
			current_test.set_msg(m)
			current_test.set_trace(self.traceback_on_exception())
			return

		withwhat = self.comargs_params_text(comargs, parameters, erin)
		#  now test it with expected exit msg
		try:
			r = str(r)
			r = r.replace("\n", "")
			expected = str(expected)
			assert r.strip().lower() == expected.strip().lower()
		except AssertionError:
			m = f"{Style.BRIGHT}{funcname}{pars}{Style.NORMAL} {withwhat} EXPECTED {hoeuit} {Style.BRIGHT}{expected}{Style.NORMAL}, but RECEIVED exit message {Style.BRIGHT}{r}{Style.NORMAL}"
			current_test.passed(False)
			current_test.set_msg(m)
			return
		except:
			m = f"{Style.BRIGHT}{funcname}{pars}{Style.NORMAL} {withwhat} -- some other error occurred, see traceback for details"
			current_test.passed(False)
			current_test.set_msg(m)
			current_test.set_trace(self.traceback_on_exception())
			return

		m = f"{Style.BRIGHT}{funcname}{pars}{Style.NORMAL} {withwhat} has {hoeuit} {Style.BRIGHT}{expected}{Style.NORMAL}"
		current_test.passed(True)
		current_test.set_msg(m)
		return


# the test per file in ass-name (nerdy i.e.)
class ApiTest:
	def __init__(self, gituser: str, mod_path: str, ass_name: str, mod_name: str, no_trace: bool, errors_only: bool):
		self.gituser = gituser
		self.ass_name = ass_name
		self.mod_name = mod_name
		self.no_trace = no_trace
		self.errors_only = errors_only
		self.mod_path = mod_path

		# set path and check if exists testing module of assignment
		self.ass_path = f"{APP_NAME}.{self.ass_name}.test_{self.mod_name}"
		
		try:
			if not importlib.util.find_spec(self.ass_path):
				self.utestmod = None
				return
			else:
				# hier wordt geimporteerd
				self.utestmod = importlib.import_module(self.ass_path, package=None)
				
		except Exception as e:
			self.utestmod = None
			return

		# check for single file test class
		if not hasattr(self.utestmod, 'SingleFileTest'):
			self.test_o = None
			return
		else:
			try:
				self.test_o = self.utestmod.SingleFileTest(self.gituser, self.mod_path, self.no_trace, self.errors_only)
			except:
				self.test_o = None
				return

	def run_utest(self) -> list:
		self.test_o.runrun()
		r = self.test_o.get_report()
		return r

# Api loads the specific assignment test module (test_nerdy.py)
# this is a child of base_test.BaseTest
# then returns report as list()