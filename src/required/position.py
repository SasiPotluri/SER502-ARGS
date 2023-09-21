###########
# SER 502 - SPRING 2023 - TEAM 11
# Our Language: ARGS
# args version 1.0
# Last Updated: April 29 2023
# Team: Akansha Reddy Anthireddygari | Girija Rani Nimmagadda | Sairachana Paladugu | Sasikanth Potluri 
# Implementation of Lexer
###########
class Position:
	def __init__(self, idx, ln, col, fn, ftxt):
		self.idx = idx
		self.ln = ln
		self.col = col
		self.fn = fn
		self.ftxt = ftxt

	def advance(self, current_char=None):
		self.idx += 1
		self.col += 1

		if current_char == '\n':
			self.ln += 1
			self.col = 0

		return self

	def copy(self):
		return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)
	








	