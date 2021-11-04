import numpy as np
import operator
import re
from pprint import pprint
import pint
import math
from copy import deepcopy
ureg = pint.UnitRegistry(system='mks', autoconvert_offset_to_baseunit=True)
ureg.load_definitions('./units.txt')

def compile_fp(context, p):
    var = {
        'num_fact_score': []
    }
    answer_to_fact = {}
    match_number = re.compile('-?\ *[0-9]+\.*[0-9]*(?:[Ee]\ *[-+]?\ *[0-9]+)*')
    context = context.split('=')[1:]
    for fact in context:
        if fact == '':
            continue
        try:
            var[fact[:fact.index(':')]] = float(re.findall(match_number, fact[fact.index(':')+1: ])[0])
        except:
            try:
                var[fact[:fact.index(':')]] = None
            except:
                pass

    p = p.split('=')[1:]
    funcs = {'Mul':operator.mul, 'Div':operator.truediv, 'Add':operator.add, 'Sub': operator.sub, 'Pow': operator.pow, 'Min': lambda *a: min(*a), 'Log': lambda *a: math.log(*a), 'Fac': lambda a: math.factorial(a)}
    paren_match = re.compile('\(([^()]+)\)')
    for line in p:
        # print(line)
        if line[0] == 'Q' or line[0] == 'P':
            try:
                lhs, rhs = line.split('->')
                lhs = lhs.strip()
                rhs = rhs.strip()
                new = False
            except:
                try:
                    lhs, rhs = line.split('—>')
                    lhs = lhs.strip()
                    rhs = rhs.strip()
                    new = False
                except:
                    lhs, rhs = line.split(':')
                    lhs = lhs.strip()
                    rhs = rhs.strip()
                    new = True
            if (lhs not in var and not new) or (lhs in var and new):
                raise ValueError('Improper assignment notation')
            if '-> A' in line and line[0] == 'Q' and new:
                raise ValueError('Question must be defined first')
            if '-> A' in line and line[0] == 'P' and new:
                raise ValueError('Output must be in terms of question identifiers')
            if '|' in rhs:
                answer, fact = rhs.split('|')
                answer = answer.strip()
                fact = fact.strip()
                try:
                    var['num_fact_score'].append(accuracy_metric(var[answer], var[fact]))
                except:
                    var['num_fact_score'].append(0)
                answer_to_fact[answer] = fact[1]
                var[lhs] = var[answer]
            elif any(re.search(r'\b' + func + r'\b', line) for func in funcs):
                for func in funcs:
                    if func in line:
                        break
                parens = [i.strip() for i in re.findall(paren_match, line)[0].split(',')]
                in_parens = []
                for i in parens:
                    if i in var and 'Q' not in i:
                        raise ValueError('Only question identifiers allowed in functions')
                    if i in var:
                        in_parens.append(var[i])
                    else:
                        in_parens.append(float(i))
                var[lhs] = funcs[func](*in_parens)
            else:
                var[lhs] = rhs
        elif line[0] == 'A':
            # var[line[:line.index(':')]] = float(re.findall(match_number, line[line.index(':')+1: ])[0])
            ureg_conv = ureg(line[line.index(':')+1: ])
            # if type(ureg_conv) not in [float, int, np.float64] and 'kelvin' in str(ureg_conv.units):
            #     print(str(ureg_conv.units), ',', str(ureg_conv.units).replace('kelvin', 'celsius'))
            #     print(ureg_conv)
            #     ureg_conv = ureg_conv.to(str(ureg_conv.units).replace('kelvin', 'celsius'))
            #     print(ureg_conv)
            #     print()
            var[line[:line.index(':')]] = ureg_conv
        else:
            raise ValueError('Line must begin with question identifier, answer identifier, or final output identifier')
    var['answer_to_fact'] = answer_to_fact
    var['num_fact_score'] = np.mean(var['num_fact_score'])
    # pprint(var)
    return var

def parse_program(cur):
    if cur[0] == 'answer':
        cur = cur[1]
    if len(cur) == 1:
        cur = cur[0]
    if type(cur) == str and cur.isdigit():
        return float(cur)
    if cur[0] == '':
        return float(cur[1][0])
    elif cur[0] == '.':
        return kb[kb.name == cur[1][0]][cur[1][1]].values[0]
    elif cur[0] in MATH_OPS:
        cur_left = parse_program(cur[1][0])
        cur_right = parse_program(cur[1][1])
        if cur[0] == '/' and cur_right == 0:
            return np.inf
        return MATH_OPS[cur[0]](cur_left, cur_right)

def accuracy_metric(y, y_hat):
    if type(y) not in [int, float, np.float64] or type(y_hat) not in [int, float, np.float64]:
        return 0
    if y is None or y_hat is None:
        return 0
    if y < 0 or y_hat < 0:
        return 0
    if y == 0 and y_hat == 0:
        return 1
    elif y == 0 or y_hat == 0:
        return max(0, 1-np.abs(np.log10(np.abs(y - y_hat))))
    # elif y/y_hat == 0:
    #     return 0
    try:
        return max(0, 3-np.abs(np.log10(y/y_hat)))/3
    except:
        return 0

def convert_units(answer):
    if type(answer) == str:
        original_pint = ureg(answer)
    else:
        original_pint = answer
    if original_pint is None:
        return None, None
    if type(original_pint) not in [float, int]:
        original_unit = original_pint.units
        try:
            converted_pint = original_pint.to_base_units()
        except:
            converted_pint = deepcopy(original_pint)
        standard_unit = converted_pint.units
        return converted_pint.magnitude, converted_pint.units
    else:
        return original_pint, None
