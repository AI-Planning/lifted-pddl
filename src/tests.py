from lifted_pddl.parser import Parser

p = Parser()
p.parse_domain('lifted_pddl/data/logistics-domain-exists.pddl')
p.parse_problem('lifted_pddl/data/logistics-problem.pddl')


print("\nIs ('drive', (44, 15, 12)) applicable?:", p.is_action_applicable('drive', (44, 15, 12)))
print("Is ('drive', (44, 15, 18)) applicable?:", p.is_action_applicable('drive', (44, 15, 18)))
print("Is ('unload', (37, 64, 8)) applicable?:", p.is_action_applicable('unload', (37, 64, 8)))