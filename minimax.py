# determiner comment evaluer un node terminal
def evaluate(node):
	return 1


# Initialement appele minimax(origin, depth, True)
def minimax(node, depth, isMaximizing):
	if depth == 0 or node is terminal_node:
		return evaluate(node)
	if isMaximizing:
		value = float('-inf')
		for child in node:
			value = max(value, minimax(child, depth - 1, False))
	else:
		value = float('inf')
		for child in node:
			value = min(value, minimax(child, depth - 1, True))
	return value
