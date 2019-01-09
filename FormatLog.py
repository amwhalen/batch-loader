import inspect
from datetime import datetime
from filelock import FileLock

#decorator functions 
def format_arguments(func):
	""" formate many args into one string, then calls decorated function with string formatted together
	I.E. func("I love ",johnny.fullname,"because he is",100,"years old",**kwargs)
		might look like func("I love Jonnathan because he is 100 years old",**kwargs)
	"""

	from functools import wraps
	@wraps(func)
	def format_args_and_call(self,*args,**kwargs):
		# from pudb import set_trace;set_trace()

		args = list(args)
		if args:
			first = args[0]
			args = args[1:]
			formatter = ""
			for arg in args:
				formatter += ' ' + str(arg)
			first = str(first) + formatter
		else:
			first = ""
		return func(self,first,**kwargs)
	return format_args_and_call

def get_context_wrapper(func):
	"""
	passes in the context in which the wrapped function was called 
	"""
	from functools import wraps
	@wraps(func)
	def context_call(self,*args,**kwargs):
		# from pudb import set_trace;set_trace()
		args = list(args)
		stack = inspect.stack()
		if len(stack) <= 2:
			cont = "main scope - "+str(stack[1].file)+':'+str(stack[1].lineno)
		if len(stack) == 3:
			cont = "- Main Scope"
		elif len(stack) >= 4:
			cont = stack[len(stack) - 2].function
		cont = str(cont).strip()
		args.append(cont)
		return func(self,*args,**kwargs)
	return context_call

class FormatLogger():
	"""
	singleton, in order to make everything log to the same files in the right order with out passing in the log class 
	"""
	_instance=None
	def __new__(cls,logfile = None,failure_file = None,proccess_status = None, truncate = False, prints = 1): 
		if cls._instance is None:
			cls._instance = object.__new__(cls)
			logfile = 			FormatLogger.logfile	 	 = logfile
			failure_file = 		FormatLogger.failure_file	 	 = failure_file
			proccess_status = 	FormatLogger.proccess_status = proccess_status
			truncate = 			FormatLogger.truncate	 	 = truncate
			files = 			FormatLogger.files			 = [proccess_status,logfile,failure_file]
			prints = 			FormatLogger.prints	 		 = prints
			num_success = 		FormatLogger.num_success	 = 0
			num_fail = 			FormatLogger.num_fail		 = 0
			if truncate:
				truncate_file(logfile)
			if truncate:
				truncate_file(failure_file)
			if truncate:
				truncate_file(proccess_status)
		return cls._instance
	def __init__(self,logfile=None,failure_file=None,proccess_status=None, truncate = False, prints = 1):
		self.truncate = self._instance.truncate
		self.logfile = self._instance.logfile
		self.failure_file = self._instance.failure_file
		self.proccess_status = self._instance.proccess_status
		self.files = self._instance.files
		self.prints = self._instance.prints
		self.num_success = self._instance.num_success
		self.num_fail = self._instance.num_fail
	def set_print_level(self,n):
		self.prints = self._instance.prints = n
	@format_arguments
	def write(self,desc,level = 1):
		if level >=3:
			level = 3
		for n,file in enumerate(self.files):
			if n == level:
				break
			write_line_to_file(file,desc)
	
	@format_arguments
	@get_context_wrapper
	def status(self,desc,cont):
		string = "Status: in {} - {}".format(cont,desc)
		if self.prints <=1:
			print(string)
		for file in [self.proccess_status]:
			write_line_to_file(file,string)
	#alias
	info = status

	@format_arguments
	@get_context_wrapper
	def warning(self,desc,cont,context = False):
		if context:
			string = "Warning: in {} - {}".format(cont,desc)
		else:
			string = "Warning: {} ".format(desc)
		if self.prints<=2:
			print(string)
		for file in [self.logfile,self.proccess_status]:
			write_line_to_file(file,string)
	@format_arguments
	def error(self,desc):
		if self.prints <=2:
			print(desc)
		for file in [self.proccess_status]:
			write_line_to_file(file,desc)
	@format_arguments
	@get_context_wrapper
	def critical(self,desc,cont):# pylint: disable=E1120
		string = "\n-- CRITIICAL FAILURE in {} --:{}\n".format(cont,desc)
		print(string)
		for file in self.files:
			write_line_to_file(file,string)
	@format_arguments
	def success(self,desc):
		self.num_success += 1
		if self.prints <=3:
			print("SUCCESS: " + desc)
		for file in [self.logfile,self.proccess_status]:
			write_line_to_file(file,"SUCCESS: " + desc)
	
	@format_arguments
	def failure(self,desc):
		self.num_fail += 1
		if self.prints <=3:
			print("FAILURE: " + desc)
		for file in self.files:
			write_line_to_file(file,"FAILURE: " + desc)

	def close(self):
		suc = "Succeded on {} out of {} total".format(self.num_success,self.num_fail+self.num_success)
		if self.prints <=3:
			print(suc)
		write_line_to_file(self.failure_file,"Failed {} out of {} total".format(self.num_fail,self.num_fail+self.num_success))
		write_line_to_file(self.logfile,suc)
		for fn in self.files:
			close_up(fn)


def write_line_to_file(file,line=None):
	if line is None:
		line = ''
	# with FileLock(file):
	with open(file,'a') as logfile:
		logfile.write(str(line)+'\n')

def truncate_file(path):
	# with FileLock(path):
	with open(path,'w') as logfile:
		logfile.write('---- logging on {} ----\n'.format(datetime.now()))

def close_up(path):
	# with FileLock(path):
	with open(path,'a') as logfile:
		logfile.write('\n---- end of logging session {} ----\n\n'.format(datetime.now()))
	pass

def get_context():
	stack = inspect.stack()
	if len(stack) <= 2:
		return "main scope - "+str(stack[1].code_context[0])
	if len(stack) == 3:
		return "- Main Scope"
	elif len(stack) > 3:
		return stack[3].code_context[0]


