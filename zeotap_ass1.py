import re

class Node:
    def __init__(self, node_type, left=None, right=None, value=None):
        self.type = node_type  
        self.left = left  
        self.right = right  
        self.value = value  

def parse_condition(condition):
    """ Parses a condition string into an operand node """
    condition = condition.strip()
    condition = condition.replace(")", "").replace("(", "")  
    
    if ">" in condition:
        left, right = condition.split(">")
        return Node("operand", value=(left.strip(), ">", int(right.strip())))
    elif "<" in condition:
        left, right = condition.split("<")
        return Node("operand", value=(left.strip(), "<", int(right.strip())))
    elif "=" in condition:
        left, right = condition.split("=")
        return Node("operand", value=(left.strip(), "=", right.strip()))


def create_rule(rule_string):
    """ Creates an AST from a rule string """
    tokens = re.split(r'\s(AND|OR)\s', rule_string)  
    stack = []

    for token in tokens:
        if token.strip() in ["AND", "OR"]:
            stack.append(Node("operator", value=token.strip()))
        else:
            condition_node = parse_condition(token)
            if stack and stack[-1].type == "operator":
                operator_node = stack.pop()
                operator_node.right = condition_node
                if stack:
                    operator_node.left = stack.pop()
                stack.append(operator_node)
            else:
                stack.append(condition_node)

    return stack[-1]  


def combine_rules(rules):
    
    if len(rules) == 1:
        return rules[0]

    combined = rules[0]
    for rule in rules[1:]:
        combined = Node("operator", left=combined, right=rule, value="AND")

    return combined


def evaluate_node(node, data):

    if node.type == "operand":
        key, operator, value = node.value
        if operator == ">":
            return data.get(key, 0) > value
        elif operator == "<":
            return data.get(key, 0) < value
        elif operator == "=":
            return data.get(key) == value
    elif node.type == "operator":
        left_result = evaluate_node(node.left, data)
        right_result = evaluate_node(node.right, data)
        if node.value == "AND":
            return left_result and right_result
        elif node.value == "OR":
            return left_result or right_result

def evaluate_rule(ast, data):
    """ Evaluates the entire AST """
    return evaluate_node(ast, data)
rule1 = create_rule("((age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')) AND (salary > 50000 OR experience > 5)")
rule2 = create_rule("((age > 30 AND department = 'Marketing')) AND (salary > 20000 OR experience > 5)")
combined_rule = combine_rules([rule1, rule2])
sample_data = {"age": 35, "department": "Marketing", "salary": 20000, "experience": 3}
result = evaluate_rule(combined_rule, sample_data)
print(result)