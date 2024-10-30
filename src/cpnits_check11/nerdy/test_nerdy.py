from ..base_test import BaseTest

class SingleFileTest(BaseTest):
	def __init__(self, gituser: str, mod_path: str, no_trace: bool, errors_only: bool):
		super().__init__()
		self.gitname = gituser
		self.modpath = mod_path
		self.aname = 'nerdy'  # assignmentname
		self.modname = 'nerdy'
		self.no_trace = no_trace
		self.errors_only = errors_only
		self.check_user_mod()
		self.set_functions(['keer', 'reverse', 'argss', 'multi', 'raise_an_error', 'eruut', 'main'])

	def test_reverse_values(self):
		funcname = 'reverse'
		func = 'reverse'
		pars = '(s: str) -> str:'
		testvals = {
			f'with normal characters': [['ding', 'gnid'], ['lol', 'lol']],
			f'with non-alpha characters': [['!ddd9 ', ' 9ddd!']],
		}
		self.assert_params_multi(funcname, pars, testvals )

	def test_keer(self):
		funcname = 'keer'
		func = 'keer'
		pars = '(n: int) -> int:'
		testvals = {
			'with positive n': [[2, 6], [3, 12]],
			'with negative n': [[-2, 2], [-5, 20]],
			'with zero n': [[0, 0]],
		}
		self.assert_params_multi(funcname, pars, testvals)

	def test_multi(self):
		funcname = 'multi'
		func = 'multi'
		pars = '(n: int, s: str, x) -> (int, str):'
		# --- tests ---
		testname = 'for proper input'
		self.assert_params_comargs(
			funcname,
			pars,
			testname,
			(9, 'negen'),
			(9, 'negen', False),
			()
		)
		self.assert_params_comargs(
			funcname,
			pars,
			testname,
			(11, 'elf'),
			(11, 'elf', False),
			()
		)

	def test_argss(self):
		funcname = 'argss'
		func = 'argss'
		pars = '() -> int:'
		testname = 'with command line args'
		self.set_argv([3, 'a']) # the args in the commandline
		self.assert_params_comargs(
			funcname,
			pars,
			testname,
			22,
			[],
			[3, 'a']
		)

	def test_raise(self):
		funcname = 'raise_an_error'
		func = 'raise_an_error'
		pars = '(p, q) -> float:'
		testname = 'for raising error'
		self.assert_params_comargs(
			funcname,
			pars,
			testname,
			3.5,
			[7, 2],
			[],
		)
		self.raise_error(
			funcname,
			pars,
			testname,
			'ZeroDivisionError',
			[7, 0],
			[],
		)

	def test_exit(self):
		funcname = 'eruut'
		func = 'eruut'
		pars = '(p, q) -> float:'
		testname = 'for proper sys.exit value'
		self.sys_exit(
			funcname,
			pars,
			testname,
			'Cannot divide by zero',
			[7, 0],
			[],
		)

	def test_main(self):
		# with user input output
		funcname = 'main'
		func = 'main'
		pars = '():'
		testname = 'terminal input-output'
		# self.set_argv([3, 'a'])  # the args in the commandline
		self.input_and_or_output(
			funcname,
			pars,
			testname,
			12,
			[],
			[],
			'3',  # erin, if None, params and comargs are used
			'3 keer (3 + 1) = 12',  # eruit, if None expected is used as normal output
		)

