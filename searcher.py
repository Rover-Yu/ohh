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

import indexer

class History(object):
	def __init__(self):
		self.clear()

	def clear(self):
		self.history = []
		self.pos = -1

	def next(self, move=True):
		if not self.history:
			return
		pos = self.pos - 1
		if pos < 0:
			return
		elif move:
			self.pos = pos
		return self.history[pos]

	def prev(self, move=True):
		if not self.history:
			return
		pos = self.pos + 1
		if pos >= len(self.history):
			return
		elif move:
			self.pos = pos
		return self.history[pos]

	def pos_of(self, item):
		try:
			return self.history.index(item)
		except IndexError:
			return -1

	def current(self, pos = -1):
		if pos != -1:
			self.pos = pos
		return self.history[self.pos]

	def record(self, item):
		if item in self.history:
			self.history.remove(item)
		self.history.insert(0, item)

	def all(self):
		return self.history[:]

	def __str__(self):
		s = ""
		i = 0
		for e in self.history:
			s += "%d. %s\n" % (i, e)
			i += 1
		return s

class Searcher(object):
	def __init__(self, cwd):
		# for "symbol list", GNU global may lost some results, so we do not use it default
		indexers = (indexer.Cscope(cwd), indexer.Ctags(cwd), indexer.Grep(), indexer.Caller(cwd))
		self.indexers = indexers

	def common_impl(self, action, arg):
		if not self.indexers:
			return
		for idx in self.indexers:
			try:
				call = idx.__getattribute__(action)
				if call:
					results = call(arg)
					if results:
						return results
			except indexer.NotImplementedYet:
				pass
		return []

	def search_def(self, sym):
		return self.common_impl("search_def", sym)

	def search_ref(self, sym):
		return self.common_impl("search_ref", sym)

	def search_regex(self, sym):
		return self.common_impl("search_regex", sym)

	def outline_file(self, fn):
		return self.common_impl("outline_file", fn)

	def local_find(self, target, fn):
		return self.common_impl("local_find", (target, fn))

	def symbol_list(self, prefix):
		return self.common_impl("symbol_list", prefix)

	def search_callee(self, sym):
		return self.common_impl("search_callee", sym)

	def search_caller(self, sym):
		return self.common_impl("search_caller", sym)

def test_searcher():
	import sys
	testbed = "/data/sources/kernels/linux-2.6.26"
	s = Searcher(testbed)
	for fn, caller, lineno, attrtab in  s.search_def(sys.argv[1]):
		print "D", fn, caller, lineno, attrtab
	for fn, caller, lineno, attrtab in  s.search_ref(sys.argv[2]):
		print "R", fn, caller, lineno, attrtab

def test_history():
	h = History()
	h.record(("f1", 1))
	h.record(("f2", 2))
	print h.prev()
	print h.next()

if __name__ == "__main__":
	#test_searcher()
	test_history()
