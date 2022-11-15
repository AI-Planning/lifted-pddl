from lifted_pddl.parser import Parser

p = Parser()
p.parse_domain('lifted_pddl/data/logistics-domain-exists.pddl')
p.parse_problem('lifted_pddl/data/logistics-problem.pddl')
print(p.get_applicable_actions())