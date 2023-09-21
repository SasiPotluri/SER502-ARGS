###########
# SER 502 - SPRING 2023 - TEAM 11
# Our Language: ARGS
# args version 1.0
# Last Updated: April 29 2023
# Team: Akansha Reddy Anthireddygari | Girija Rani Nimmagadda | Sairachana Paladugu | Sasikanth Potluri 
# Implementation of Lexer
###########
import sys
sys.path.append("src/interpreter")
import runtime.interpreter

while True:
	text = input('args > ')
	if text.strip() == "": continue
	result, error = runtime.interpreter.run('<stdin>', text)

	if error: 
		print(error.as_string())
	elif result: 
		if len(result.elements) == 1:
			print(repr(result.elements[0]))
		else:
			print(repr(result))