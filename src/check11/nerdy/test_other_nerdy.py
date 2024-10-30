from ..base_test import BaseTest

class SingleFileTest(BaseTest):
	def __init__(self, gituser: str, mod_path: str, no_trace: bool, errors_only: bool):
		super().__init__()
		self.gitname = gituser
		self.modpath = mod_path
		self.aname = 'nerdy'  # assignmentname
		self.modname = 'other_nerdy'
		self.no_trace = no_trace
		self.errors_only = errors_only
		self.check_user_mod()
		self.set_functions(['exit_hello']) # 'bestaat_niet'])

	def test_exit(self):
		funcname = 'exit_hello'
		pars = '():'
		testname = 'for proper sys.exit message'
		self.sys_exit(
			funcname,
			pars,
			testname,
			'Hello World',
			[],
			[],
		)

