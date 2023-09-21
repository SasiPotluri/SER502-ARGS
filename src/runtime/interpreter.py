###########
# SER 502 - SPRING 2023 - TEAM 11
# Our Language: ARGS
# args version 1.0
# Last Updated: April 29 2023
# Team: Akansha Reddy Anthireddygari | Girija Rani Nimmagadda | Sairachana Paladugu | Sasikanth Potluri 
# Implementation of Lexer
###########
import sys
sys.path.append("src/compiler")

import required.errorhandling as errorclass
import required.nodes as nodes
import required.values as values
import compiler.Parser as parser
#from Parser import Parser
import compiler.lexer as lexer
#from lexer import Lexer


# Runtime Result

class RTResult:
	def __init__(self):
		self.reset()
	
	def reset(self):
		self.value = None
		self.error = None
		self.func_return_value = None
		self.loop_should_continue = False
		self.loop_should_break = False

	def register(self, res):
		self.error = res.error
		self.func_return_value = res.func_return_value
		self.loop_should_continue = res.loop_should_continue
		self.loop_should_break = res.loop_should_break
		return res.value

	def success(self, value):
		self.reset()
		self.value = value
		return self

	def success_return(self, value):
		self.reset()
		self.func_return_value = value
		return self
  
	def success_continue(self):
		self.reset()
		self.loop_should_continue = True
		return self

	def success_break(self):
		self.reset()
		self.loop_should_break = True
		return self

	def failure(self, error):
		self.reset()
		self.error = error
		return self

	def should_return(self):
    
		return (
			self.error or
			self.func_return_value or
			self.loop_should_continue or
			self.loop_should_break
			)

# Defining Context

class Context:
	def __init__(self, display_name, parent=None, parent_entry_pos=None):
		self.display_name = display_name
		self.parent = parent
		self.parent_entry_pos = parent_entry_pos
		self.symbol_table = None

# Defining SymbolTable

class SymbolTable:
	def __init__(self, parent=None):
		self.symbols = {}
		self.parent = parent

	def get(self, name):
		value = self.symbols.get(name, None)
		if value == None and self.parent:
			return self.parent.get(name)
		return value

	def set(self, name, value):
		self.symbols[name] = value

	def remove(self, name):
		del self.symbols[name]

#-------------------------------IMPLEMENTATION-------------------------------------#
#-------------------------------------OF-------------------------------------------#
#--------------------------------INTERPRETER---------------------------------------#

class Interpreter:
	def visit(self, node, context):
		method_name = f'visit_{type(node).__name__}'
		method = getattr(self, method_name, self.no_visit_method)
		return method(node, context)

	def no_visit_method(self, node, context):
		raise Exception(f'No visit_{type(node).__name__} method defined')

	#------INTERPRET------#

	def visit_NumberNode(self, node, context):
		return RTResult().success(
			values.Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
		)
	def visit_StringNode(self, node, context):
		return RTResult().success(
			values.String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
		)
	def visit_BoolNode(self, node, context):
		return RTResult().success(
			values.Boolean(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
		)
	
	def visit_ListNode(self, node, context):
		res = RTResult()
		elements = []

		for element_node in node.element_nodes:
			elements.append(res.register(self.visit(element_node, context)))
			if res.should_return(): return res

		return res.success(
			values.List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
		)


	def visit_VarAccessNode(self, node, context):
		res = RTResult()
		var_name = node.var_name_tok.value
		value = context.symbol_table.get(var_name)

		if not value:
			return res.failure(errorclass.RTError(
				node.pos_start, node.pos_end,
				f"'{var_name}' is not defined",
				context
			))

		value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
		return res.success(value)

	def visit_VarAssignNode(self, node, context):
		res = RTResult()
		var_name = node.var_name_tok.value
		value = res.register(self.visit(node.value_node, context))
		if res.should_return(): return res

		context.symbol_table.set(var_name, value)
		return res.success(value)

	def visit_BinOpNode(self, node, context):
		res = RTResult()
		left = res.register(self.visit(node.left_node, context))
		if res.should_return(): return res
		right = res.register(self.visit(node.right_node, context))
		if res.should_return(): return res

		if node.op_tok.type == lexer.TT_PLUS:
			result, error = left.added_to(right)
		elif node.op_tok.type == lexer.TT_MINUS:
			result, error = left.subbed_by(right)
		elif node.op_tok.type == lexer.TT_MUL:
			result, error = left.multed_by(right)
		elif node.op_tok.type == lexer.TT_DIV:
			result, error = left.dived_by(right)
		elif node.op_tok.type == lexer.TT_POW:
			result, error = left.powed_by(right)
		elif node.op_tok.type == lexer.TT_MOD:
			result, error = left.moded_by(right)
		elif node.op_tok.type == lexer.TT_EE:
			result, error = left.get_comparison_eq(right)
		elif node.op_tok.type == lexer.TT_NE:
			result, error = left.get_comparison_ne(right)
		elif node.op_tok.type == lexer.TT_LT:
			result, error = left.get_comparison_lt(right)
		elif node.op_tok.type == lexer.TT_GT:
			result, error = left.get_comparison_gt(right)
		elif node.op_tok.type == lexer.TT_LTE:
			result, error = left.get_comparison_lte(right)
		elif node.op_tok.type == lexer.TT_GTE:
			result, error = left.get_comparison_gte(right)
		elif node.op_tok.matches(lexer.TT_KEYWORD, '&&'):
			result, error = left.anded_by(right)
		elif node.op_tok.matches(lexer.TT_KEYWORD, '||'):
			result, error = left.ored_by(right)

		if error:
			return res.failure(error)
		else:
			return res.success(result.set_pos(node.pos_start, node.pos_end))

	def visit_UnaryOpNode(self, node, context):
		res = RTResult()
		number = res.register(self.visit(node.node, context))
		if res.should_return(): return res

		error = None

		if node.op_tok.type == lexer.TT_MINUS:
			number, error = number.multed_by(values.Number(-1))
		elif node.op_tok.matches(lexer.TT_KEYWORD, '##'):
			number, error = number.notted()

		if error:
			return res.failure(error)
		else:
			return res.success(number.set_pos(node.pos_start, node.pos_end))

	def visit_IfNode(self, node, context):
		res = RTResult()

		for condition, expr, should_return_null in node.cases:
			condition_value = res.register(self.visit(condition, context))
			if res.should_return(): return res

			if condition_value.is_true():
				expr_value = res.register(self.visit(expr, context))
				if res.should_return(): return res
				return res.success(values.Number.null if should_return_null else expr_value)

		if node.else_case:
			expr, should_return_null = node.else_case
			expr_value = res.register(self.visit(expr, context))
			if res.should_return(): return res
			return res.success(values.Number.null if should_return_null else expr_value)
		return res.success(values.Number.null)

	def visit_TernaryNode(self, node, context):
		res = RTResult()

		for condition, expr in node.cases:
			condition_value = res.register(self.visit(condition, context))
			if res.error: return res

			if condition_value.is_true():
				expr_value = res.register(self.visit(expr, context))
				if res.error: return res
				return res.success(expr_value)

		if node.else_case:
			else_value = res.register(self.visit(node.else_case, context))
			if res.error: return res
			return res.success(else_value)

		return res.success(None)

	def visit_ForNode(self, node, context):
		res = RTResult()
		elements = []

		start_value = res.register(self.visit(node.start_value_node, context))
		if res.should_return(): return res

		end_value = res.register(self.visit(node.end_value_node, context))
		if res.should_return(): return res

		if node.step_value_node:
			step_value = res.register(self.visit(node.step_value_node, context))
			if res.should_return(): return res
		else:
			step_value = values.Number(1)

		i = start_value.value

		if step_value.value >= 0:
			condition = lambda: i < end_value.value
		else:
			condition = lambda: i > end_value.value
		
		while condition():
			context.symbol_table.set(node.var_name_tok.value, values.Number(i))
			i += step_value.value

			value = res.register(self.visit(node.body_node, context))
			if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

			if res.loop_should_continue:
				continue
      
			if res.loop_should_break:
				break
			elements.append(value)

		return res.success(
			values.Number.null if node.should_return_null else
			values.List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)

		)

	def visit_WhenNode(self, node, context):
		res = RTResult()
		elements = []

		while True:
			condition = res.register(self.visit(node.condition_node, context))
			if res.should_return(): return res

			if not condition.is_true(): break

			value = res.register(self.visit(node.body_node, context))
			if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

			if res.loop_should_continue:
				continue
      
			if res.loop_should_break:
				break

			elements.append(value)

		return res.success(
			values.Number.null if node.should_return_null else
      		values.List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
			
		)
	
	def visit_FuncDefNode(self, node, context):
		res = RTResult()

		func_name = node.var_name_tok.value if node.var_name_tok else None
		body_node = node.body_node
		arg_names = [arg_name.value for arg_name in node.arg_name_toks]
		func_value = values.Function(func_name, body_node, arg_names, node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)
		
		if node.var_name_tok:
			context.symbol_table.set(func_name, func_value)

		return res.success(func_value)

	def visit_CallNode(self, node, context):
		res = RTResult()
		args = []

		value_to_call = res.register(self.visit(node.node_to_call, context))
		if res.should_return(): return res
		value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

		for arg_node in node.arg_nodes:
			args.append(res.register(self.visit(arg_node, context)))
			if res.should_return(): return res

		return_value = res.register(value_to_call.execute(args))
		if res.should_return(): return res
		return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
		return res.success(return_value)
	
	def visit_ReturnNode(self, node, context):
		res = RTResult()

		if node.node_to_return:
			value = res.register(self.visit(node.node_to_return, context))
			if res.should_return(): return res
		else:
			value = values.Number.null
    
		return res.success_return(value)

	def visit_ContinueNode(self, node, context):
		return RTResult().success_continue()

	def visit_BreakNode(self, node, context):
		return RTResult().success_break()
	

### RUN PROGRAM ###


# global_symbol_table.set("FALSE", values.String.false)
# global_symbol_table.set("TRUE", values.String.true)

global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", values.Number.null)
global_symbol_table.set("FALSE", values.Number.false)
global_symbol_table.set("TRUE", values.Number.true)
global_symbol_table.set("MATH_PI", values.Number.mathPI)
global_symbol_table.set("SHOW", values.BuiltInFunction.print)
global_symbol_table.set("SHOW_RET", values.BuiltInFunction.print_ret)
global_symbol_table.set("INPUT", values.BuiltInFunction.input)
global_symbol_table.set("INPUT_INT", values.BuiltInFunction.input_int)
global_symbol_table.set("CLEAR", values.BuiltInFunction.clear)
global_symbol_table.set("CLS", values.BuiltInFunction.clear)
global_symbol_table.set("IS_NUM", values.BuiltInFunction.is_number)
global_symbol_table.set("IS_STR", values.BuiltInFunction.is_string)
global_symbol_table.set("IS_LIST", values.BuiltInFunction.is_list)
global_symbol_table.set("IS_FUN", values.BuiltInFunction.is_function)
global_symbol_table.set("APPEND", values.BuiltInFunction.append)
global_symbol_table.set("POP", values.BuiltInFunction.pop)
global_symbol_table.set("EXTEND", values.BuiltInFunction.extend)
global_symbol_table.set("LEN", values.BuiltInFunction.len)
global_symbol_table.set("RUN", values.BuiltInFunction.run)


def run(fn, text):
	# Generate tokens
	lex = lexer.Lexer(fn, text)
	tokens, error = lex.make_tokens()
	if error: return None, error
	
	# Generate AST
	par = parser.Parser(tokens)
	ast = par.parse()
	if ast.error: return None, ast.error

	# Run program
	interpreter = Interpreter()
	context = Context('<program>')
	context.symbol_table = global_symbol_table
	result = interpreter.visit(ast.node, context)

	return result.value, result.error
