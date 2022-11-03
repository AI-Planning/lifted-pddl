# __main__.py

import argparse
import sys
import os

from lifted_pddl.parser import Parser

# Execute the following code if the script is called from the command-line, i.e.,
# python -m lifted_parser
def main():
	# Parse command-line arguments with module argparse
	# Different options of use:
	#	> help: we show how to use this script from the command-line
	# 	> example: we show an example of use, for the logistics domain
	#	> print_planning_task domain_file problem_file: 
	#		we print the information encoded in the PDDL domain and problem, according to the format used in Parser.__str__()
	#		problem_file is an optional parameter. If not used, we assume there is no PDDL problem.
	# 	> get_applicable_actions domain_file problem_file: 
	#		we print the list of applicable actions at the init state of the planning task given by (domain_file, problem_file)
	#	> is_action_applicable domain_file problem_file action:
	#		we print 'True' if action @action is applicable at the init state of the planning task given by (domain_file, problem_file).
	#		@action must correspond to a string in standard PDDL form (e.g., '(drive t1 l1 l2 c1)')
	#	> get_next_state domain_file problem_file action:
	#		we print the next state resulting from applying the action @action at the current state (i.e., the init state of the 
	#       planning task given by (domain_file, problem_file)). The state is printed as a list of its atoms in PDDL format
	#		(e.g., (at p1 l2) (in-city l1 c5) ...)

	cli_parser = argparse.ArgumentParser(prog='Lifted Parser',
										 description='This program makes possible to parse PDDL domains and problems to obtain their information, \
										 			  obtain the applicable actions in an efficient manner (without grounding), and obtain the state \
										 			  resulting from applying an action at the current state (successor function).')

	cli_parser.add_argument('execution_mode', choices=('example', 'print_planning_task', 'get_applicable_actions', 'is_action_applicable', 'get_next_state'),
							help="Execution mode, i.e., what this program will do. There are several options: example -> shows an example of use for the logistics domain, \
							print_planning_task -> prints the information encoded in the PDDL domain (and also the PDDL problem if it's passed as an argument), \
							get_applicable_actions -> prints the ground actions applicable at the init state of the problem passed as an argument, \
							is_action_applicable -> prints whether the action passed as an argument is applicable at the init state of the problem, \
							get_next_state -> prints the next state (as a list of atoms) obtained by applying the action to the init state of the problem.")
	cli_parser.add_argument('-d', '--domain', required=False, help='Path to the domain file')
	cli_parser.add_argument('-p', '--problem', required=False, help='Path to the problem file')
	cli_parser.add_argument('-a', '--action', required=False, help='Action in PDDL format (e.g., "(unload t1 p11 l1)" )')

	args = cli_parser.parse_args()
	execution_mode = args.execution_mode
	domain_path = args.domain
	problem_path = args.problem
	action = args.action

	# --- Example of use ---
	if execution_mode == 'example':
		# Change working directory to this file's location
		os.chdir(os.path.realpath(os.path.dirname(__file__)))

		# Parse logistics domain
		parser = Parser()
		parser.parse_domain('data/logistics-domain.pddl')
		print("Parser information after parsing the domain\n", parser)

		# Parse logistics problem
		parser.parse_problem('data/logistics-problem.pddl')
		print("\nParser information after parsing the domain AND problem\n", parser)

		# Obtain actions applicable at the current state (given by logistics-problem.pddl)
		print("\nApplicable actions:\n", parser.get_applicable_actions()) # Average execution time: 0.0007s
		print("\nApplicable actions in PDDL format:\n", parser.encode_ground_actions_as_pddl(parser.get_applicable_actions(), 'str'))

		# Check if individual actions are applicable
		print("\nIs ('drive', (44, 15, 12, 1)) applicable?:", parser.is_action_applicable('drive', (44, 15, 12, 1)))
		print("Is ('drive', (44, 15, 18, 1)) applicable?:", parser.is_action_applicable('drive', (44, 15, 18, 1)))
		print("Is ('unload', (37, 64, 8)) applicable?:", parser.is_action_applicable('unload', (37, 64, 8)))

		# Apply an action at the current state (given by logistics-problem.pddl) and obtain the next state
		print("\nApply action ('drive', (44, 15, 12, 1)) and get next state:\n", parser.get_next_state('drive', (44, 15, 12, 1)))
		print("\nApply action ('drive', (44, 15, 12, 1)) and get next state in PDDL format:\n", parser.encode_atoms_as_pddl(parser.get_next_state('drive', (44, 15, 12, 1)), 'str'))

	# --- Print the information of the PDDL domain (and problem if given as argument) ---
	elif execution_mode == 'print_planning_task':
		if domain_path is None:
			raise Exception('No domain provided')

		parser = Parser()
		parser.parse_domain(domain_path)
		if problem_path is not None:
			parser.parse_problem(problem_path)

		print(parser)

	# --- Print the ground actions which are applicable at the init state of the planning task ---
	elif execution_mode == 'get_applicable_actions':
		if domain_path is None:
			raise Exception('No domain provided')
		if problem_path is None:
			raise Exception('No problem provided')

		parser = Parser()
		parser.parse_domain(domain_path)
		parser.parse_problem(problem_path)

		applicable_actions = parser.encode_ground_actions_as_pddl(parser.get_applicable_actions(), 'str')

		# Print the applicable ground actions (in PDDL format)
		for a in applicable_actions:
			print(a)

	# --- Print whether the action given as a parameter is applicable at the init state of the planning task ---
	elif execution_mode == 'is_action_applicable':
		if domain_path is None:
			raise Exception('No domain provided')
		if problem_path is None:
			raise Exception('No problem provided')
		if action is None:
			raise Exception('No action provided')

		parser = Parser()
		parser.parse_domain(domain_path)
		parser.parse_problem(problem_path)

		action = action.strip('(').strip(')').split()

		if len(action) == 0: # Action with no parameters
			action_name = action[0]
			action_params = tuple()
		else:
			action_name = action[0]
			action_params = action[1:]

		# Encode each object as an index (e.g., loc1 -> 2)
		object_names = parser.object_names
		action_params = tuple([object_names.index(param) for param in action_params])

		# Print whether the actions is applicable ('True' or 'False')
		print(parser.is_action_applicable(action_name, action_params))

	# --- execution_mode == get_next_state ---
	# --- Print the next state (as a list of atoms) resulting from applying the action given as a parameter to the init state of the planning task ---
	else:
		if domain_path is None:
			raise Exception('No domain provided')
		if problem_path is None:
			raise Exception('No problem provided')
		if action is None:
			raise Exception('No action provided')

		parser = Parser()
		parser.parse_domain(domain_path)
		parser.parse_problem(problem_path)

		action = action.strip('(').strip(')').split()

		if len(action) == 0: # Action with no parameters
			raise Exception('Actions with no parameters (variables) are not supported')

		action_name = action[0]
		action_params = action[1:]

		# Encode each object as an index (e.g., loc1 -> 2)
		object_names = parser.object_names
		action_params = tuple([object_names.index(param) for param in action_params])

		next_state_atoms = parser.encode_atoms_as_pddl(parser.get_next_state(action_name, action_params), 'str')

		# Print the atoms of the next state
		for atom in next_state_atoms:
			print(atom)


if __name__ == '__main__':
	main()
	
