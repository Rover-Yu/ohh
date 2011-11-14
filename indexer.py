#! /usr/bin/env python
#
#    Ohh! -- A handy cscope & ctags GUI shell.
#
#    Copyright (C) 2010  Li Yu
#
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
#

import os

C_KEYWORDS = (
	"if",
	"else",
	"for",
	"while",
	"return",

	"extern",
	"static",
	"volatile",

	"unsigned",
	"signed",

	"char",
	"short",
	"int",
	"long",
	"float",
	"double",
	"void",

	"struct",
)

class NotImplementedYet(BaseException):
	pass

class Indexer(object):
	def __init__(self, cwd):
		self.cwd = cwd
	
	def search_def(self, sym):
		"""
			in progress, return 0-100
			found, return [("filename", "caller", lineno, {attributes-dict}), ....]
			not found, return None

			attributes-dict likes (see also file format section in ctags manpage)
			{
				"language":"C",
				"kind":"function",
				"access":"public",
				"struct":"XXX",
				....
			}
		"""
		raise NotImplementedYet
	
	def search_ref(self, sym):
		""" API, same as search_ref()"""
		raise NotImplementedYet

	def search_regex(self, sym):
		""" API, same as search_ref()"""
		raise NotImplementedYet

	def search_caller(self, sym):
		""" API, same as search_def()"""
		raise NotImplementedYet
	
	def search_callee(self, sym):
		""" API, same as search_def()"""
		raise NotImplementedYet
	
	def outline_file(self, fn):
		""" API, same as search_def()"""
		raise NotImplementedYet

	def local_find(self, args):
		""" args is (target, fn) """
		""" API, same as search_def()"""
		raise NotImplementedYet

	def symbol_list(self, prefix):
		""" return a symbol list, eachone in this list starts with prefix[IN]"""
		raise NotImplementedYet

	def runCommand(self, args): # such names means private methods
		import subprocess as sp
		if self.cwd:
			cwd = os.getcwd()
			os.chdir(self.cwd)
			p = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE, cwd=self.cwd)
			os.chdir(cwd)
		else:
			p = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
		stdout, stderr = p.communicate()
		if stderr:
			if not stdout:
				raise IOError, "failed to run '%s':%s" % (args, stderr)
			else:
				print "%s said below words at stderr:" % args[0]
				print stderr
		return stdout

class Cscope(Indexer):
	def __init__(self, cwd):
        	Indexer.__init__(self, cwd)

	def handleCscopeOutput(self, output):
		lines = output.split("\n")
		results = []
		result_start = False
		i = 0
		nr_lines = len(lines)
		while i < nr_lines:
			line = lines[i]
			if not result_start:
				if line.startswith("cscope:"):
					result_start = True
				i += 1
				continue
			if not line.strip():
				i += 1
				continue
			try:
				#fs/btrfs/extent_io.c alloc_extent_state 130 spin_lock_irqsave(&leak_lock, flags);
				fn,caller,lineno,line = line.split(" ", 3)
				if caller in ("<global>", "<unknown>"):
					caller = ""
				results.append((fn, caller, int(lineno), {}))
			except ValueError:
				print "cscope said '%s' try to fix by merge with next line '%s'" % (line, lines[i+1].strip())
				lines[i+1] = line + " " + lines[i+1].strip()
			i += 1
		return results

	def search_ref(self, sym):
		"""
		in progress, return 0-100
		found, return [("filename", "caller", lineno), ....]
		not found, return None
		"""
		out = self.runCommand(("cscope", "-q", "-L", "-v", "-0", sym))
		return self.handleCscopeOutput(out)
	
	def search_regex(self, sym):
		out = self.runCommand(("cscope", "-q", "-L", "-v", "-6", sym))
		return self.handleCscopeOutput(out)

	###############
	# cscope caller search feature is not enough exact, we do not depend on it,
	# alternatively, we will guess caller tree from search_regex() + ctags.
	# this is a TODO yet.
	###############

class Grep(Indexer):
        def __init__(self, cwd = None):
                Indexer.__init__(self, cwd)

	def local_find(self, args):
		target = args[0]
		fn = args[1]
		out = self.runCommand(("grep", "-E", "-n" ,"-e", target, fn))
		lines = out.split("\n")
		results = []
		for l in lines:
			l = l.strip()
			if not l:	continue
			lineno, content = l.split(":", 1)
			results.append((fn, "", int(lineno), {}))
		return results

class Global(Indexer):
        def __init__(self, cwd):
                Indexer.__init__(self, cwd)

	def symbol_list(self, prefix):
		"""
			this feature of GNU global isn't reliable, so we do not use this default.
		"""
		out = self.runCommand(("global", "-c", prefix))
		if out:
			out = out.strip()
		return out.split("\n")

class Ctags(Indexer):
	def __init__(self, cwd):
		Indexer.__init__(self, cwd)
		self.tags = file(cwd + "/tags")

	def current_line(self, offset):
		tags = self.tags
		tags.seek(offset)
		c = tags.read(1)
		post = c
		while c and post and post[-1] != "\n":
			c = tags.read(1)
			post += c
		line_end = tags.tell()
		pre = ""
		while True:
			offset -= 1
			if offset <= 0:
				break
			tags.seek(offset)
			pre = tags.read(1) + pre
			if not pre or pre[0] == "\n":
				break
		line_start = offset - 1
		if line_start < 0:
			line_start = 0
		return pre[1:] + post, line_start, line_end

	def is_match(self, line, symbol):
		fields = line.split("\t", 1)
		cur = fields[0]
		if cur == symbol:
			return 0
		if symbol < cur:
			return -1
		return 1

	def search_symbol(self, symbol):
		tags = self.tags
		tags.seek(0, 2)
		end = tags.tell() - 1
		start = 0
		previous_line = ""
		while start < end:
			mid = int(start + end) / 2
			line, line_start, line_end = self.current_line(mid)
			if line_start>0 and line == previous_line: # try last line in file
				line, line_start, line_end = self.current_line(line_start - 1)
			result = self.is_match(line, symbol)
			if result == 0:
				return line, line_start, line_end
			if result < 0:
	#			print `line`, start, mid, end, "end=", mid - 1
				end = mid - 1
			else:
	#			print `line`, start, mid, end, "start=", mid + 1
				start = mid + 1
			previous_line = line
		return "", -1, -1

	def search_def(self, symbol):
		tags = self.tags
		line, line_start, line_end = self.search_symbol(symbol)
		if not line:
			return []
		if line_start > 0:
			prev_line, prev_start, unused = self.current_line(line_start - 1)
		else:
			prev_start = 0
		next_line, unused, next_end = self.current_line(line_end + 1)
		results = [line.strip()]
		while prev_start > 0 and 0 == self.is_match(prev_line, symbol):
			results.append(prev_line.strip())
			prev_line, prev_start, unused = self.current_line(prev_start - 1)
		while next_line and 0 == self.is_match(next_line, symbol):
			results.append(next_line.strip())
			next_line, unused, next_end = self.current_line(next_end + 1)
		return self.line2def(results)

	def line2def(self, lines):
		results = []
		for l in lines:
			if not l:	continue
			#######################
			# ctags bug?! it seem that it could not handle two continous 
			# doulbe quota charaecters ("")rightly in Exuberant Ctags 5.6, at least.
			# so here we resume "\xd3" to "", workaround :(
			######
			l = l.replace("\xd3", '""')
			fields = l.split("\t")
			filename = fields[1]
			caller = ""
			lineno = fields[2][:-2] # remove ';"'
			attrtab = {}
			for f in fields[3:]:
				try:
					k, v = f.split(":", 1)
					attrtab[k] = v
				except ValueError:
					print "abnormal attrtab", f
					print "abnormal lines:"
					for t in lines:
						print `t`
					print 'abnormal line', `l`
					import traceback
					traceback.print_stack()
					continue
			attrtab["name"] = fields[0]
			try:
				results.append((filename, caller, int(lineno), attrtab))
			except ValueError:
				print "bug here #1"
				print l
		return results

	def result_cmp(self, a, b):
		attrtab_a = a[3]
		attrtab_b = b[3]
		# first, sort by symbol kind
		kind_a = attrtab_a.get("kind")
		kind_b = attrtab_b.get("kind")
		if kind_a and kind_b:
			if kind_a < kind_b:
				return -1
			elif kind_a > kind_b:
				return 1
		#then, sort by name
		name_a = attrtab_a.get("name")
		name_b = attrtab_b.get("name")
		if name_a and name_b:
			if name_a < name_b:
				return -1
			else:
				return 1
		#otherwise, sort by lineno
		if a[2] < b[2]:
			return -1
		elif a[2] == b[2]:
			return 0
		else:
			return 1

	def outline_file(self, fn):
		outline = self.runCommand(("ctags", "-o", "-", "--excmd=number", "--fields=afiKlmnSzt", fn))
		lines = outline.split("\n")
		results = self.line2def(lines)
		results.sort(self.result_cmp)
		return results

	def symbol_list(self, prefix):
		outline = self.runCommand(("grep", "-E" ,"-e", "^[~]?%s.*" % prefix, "tags"))
		lines = outline.split("\n")
		results = [None]
		n = 0
		for l in lines:
			l = l.strip()
			if not l:
				continue
			fields = l.split("\t", 1)
			if results[-1] != fields[0]:
				results.append(fields[0])
			if n > 1000:
				print "Symbol list results are too *MANY*, truncated !!!"
				break
		del results[0]
		return results

	def search_all(self):
		"""
			Just for testing, this may take long time.
		"""
		import time
		tags = self.tags
		lines = tags.readlines()
		total = len(lines)
		i = 0
		start_sec = time.time()
		for xline in lines[6:]:
			sym = xline.split("\t")[0]
			if not sym:
				print xline, "none symbol"
				break
			line = xline.strip()
			this_def = self.line2def([line])
			got = self.search_def(sym)
			if not got:
				print line, "empty result"
				print
				break
			if this_def[0] not in got:
				print got, "is an incompleted result"
				print this_def
				break
		end_sec = time.time()
		print "%.2fQPS" % (total/(end_sec - start_sec))

class Caller(Indexer):
	def __init__(self, cwd):
		Indexer.__init__(self, cwd)
		self.cscope = Cscope(cwd)
		self.ctags = Ctags(cwd)

	def search_caller(self, sym):
		callers = []
		ref_results = self.cscope.search_ref(sym)
		ol_results = {}
		for ref in ref_results:
			ref_fn = ref[0]
			ref_lineno = ref[2]
			if ref_fn not in ol_results: # avoid outline one file multi-times
				ol_results[ref_fn] = self.ctags.outline_file(ref_fn)
			ol_result = ol_results[ref_fn]
			diff = -1
			ol_caller = None
			for ol in ol_result: # find nearest symbol before this "ref" in ctags outline result 
				ol_fn = ol[0]
				ol_lineno = ol[2]
				ol_kind = ol[3].get("kind")
				if ol_kind not in ("function", "macro", "variable"):
					continue
				if ol_lineno > ref_lineno:
					continue
				valid = True
				if ol_kind == "macro":
					#
					# if this sym may occur in a macro, then:
					#  1) it just occured in first line of macro definitation.
					#  2) this is a multilines macro, thus every line must ends with '\', 
					#     otherwise, we guess this call is a "global" call
					#
					lines = file(self.cwd + "/" + ol_fn).readlines()
					lines = lines[ol_lineno:ref_lineno+1]
					if lines and sym not in lines[0]:
						for l in lines[1:]:
							l = l.strip()
							if not l:	continue
							if l[-1] != "\\":
								valid = False
								break
				elif ol_kind == "variable":
					# if sym may occurs in a variable, then it must be either
					# 1) occured in first line
					# 2) it must be contained within some braces.
					lines = file(self.cwd + "/" + ol_fn).readlines()
					lines = lines[ol_lineno:ref_lineno+1]
					braces = []
					if sym not in lines[0]:
						for l in lines:
							n = l.count("{")
							braces += ["}"] * n
							n = l.count("}") # a rather rough stack implementation here!
							del braces[-n:]
							if sym in l and not braces:
								valid = False
								break
				if ref_lineno - ol_lineno < diff or diff == -1:
					ol_caller = ol
					diff = ref_lineno - ol_lineno
			if ol_caller:
				caller_fn = ol_caller[0]
				caller_lineno = ol_caller[2]
				caller_kind = ol_caller[3].get("kind")
				caller_name = ol_caller[3].get("name")
				if ref_lineno == caller_lineno and ref_fn == caller_fn: 
					continue
			else:
				caller_kind = "<global>"
				caller_name = ""				
			callers.append((ref_fn, caller_name, ref_lineno, {"kind":caller_kind}))
		return callers

def testCscope():
	indexer = Cscope("/data/sources/kernels/linux-2.6.26")
	print indexer.search_ref("io_schedule")

def testCtags():
	indexer = Ctags("/data/sources/kernels/linux-2.6.26")
	print indexer.search_def("io_schedule")
	print indexer.search_def("io_schedule")
	print indexer.outline_file("fs/read_write.c")
	print indexer.search_def("dentry")
	indexer.search_all()
	#results = indexer.outline_file("/data/sources/kernels/linux-2.6.26/kernel/sched.c")
	#indexer = Ctags("/home/li/src/apsara")
	#results = indexer.outline_file("/home/li/src/apsara/kuafu/kuafu2/kuafu2.cpp")
	#results = indexer.search_def("AsyncCall")
	#for r in results:
	#	print r

def testGrep():
	indexer = Grep()
	results = indexer.local_find(("mThread", "/home/sailor/src/apsara/kuafu/kuafu2/kuafu2.cpp"))
	print results

def testGlobal():
	indexer = Global("/home/li/src/apsara")
	results = indexer.symbol_list("Kuafu")
	print results

def testCaller():
	caller = Caller("/home/li/src/apsara")
	#results = caller.search_caller("AsyncCall")
	results = caller.search_caller("Push")
	for r in results:
		print r

if __name__ == "__main__":
#	testCscope()
	testCtags()
#	testGrep()
#	testGlobal()
#	testCaller()
