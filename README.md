[![PyPI version](https://badge.fury.io/py/lifted-pddl.svg)](https://badge.fury.io/py/lifted-pddl) [![Downloads](https://static.pepy.tech/badge/lifted-pddl)](https://pepy.tech/project/lifted-pddl)

# Lifted PDDL
A lightweight framework for the efficient parsing and manipulation of PDDL. 
It achieves this by working on the PDDL description in its lifted form, i.e., without grounding it first. Lifted PDDL is heavily inspired by the [Powerlifted Planner](https://github.com/abcorrea/powerlifted) but encodes PDDL elements as in [Planning Problem Generation](https://github.com/ari-dasci/S-PlanningProblemGeneration). It provides the following functionality:

 - **Parsing** PDDL domain and problem files and inspecting their information (actions, predicates, types, atoms, objects, etc.)
 - Obtaining the list of **applicable actions** at a given state. It also makes possible to check the applicability of a single ground action.
 - Obtaining the next state resulting from applying an action to the current state (**successor function**).

## Installation

You can install Lifted PDDL as a python package from [PyPI](https://pypi.org):

    pip install lifted-pddl

## Requirements

The only external depency is the `tarski` Python package, which is used to initially parse the PDDL files. It was tested on version number `0.8.2`.

Lifted PDDL was tested on Python 3.8, but should support any version of Python 3. Additionally, it was tested on Windows, but should also work on Linux, Mac and other OS.

## How to use

Lifted PDDL can be used in two different ways.

Firstly, it can be imported as any other Python module and be used within Python:

    from lifted_pddl import Parser
    
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

Secondly, it can be called from the command line. It supports different modes of execution:

- See an example of use (it executes the script above):

		lifted_pddl example

- Parse a planning task and print its information:

		lifted_pddl print_planning_task -d path_to_domain -p path_to_problem

- Get applicable actions:

		lifted_pddl get_applicable_actions -d path_to_domain -p path_to_problem

- Check action applicability:

		lifted_pddl is_action_applicable -d path_to_domain -p path_to_problem -a action_to_apply

- Get next state:

		lifted_pddl get_next_state -d path_to_domain -p path_to_problem -a action_to_apply

## Limitations

At the moment, Lifted PDDL supports the following PDDL extensions:

- Types (`:typing`).

- Existential preconditions (`:existential-preconditions`), i.e., `(exists ...)` constructions in action preconditions.

- Limited support for negative preconditions (`:negative-preconditions`), i.e., `(not ...)` constructions in action preconditions. However,
  negative compound formulas are not supported, i.e., constructions like `(exists (not ...))` and `(not (and ...))`. At the moment, we only support
  negated atoms in preconditions.

In the future, Lifted PDDL will be extended to support ADL and, maybe, other PDDL requirements. We also welcome contributions. The code is brief, simple to understand and has many comments, so I encourage you to implement any functionality you need and submit a pull request to the [Github](https://github.com/AI-Planning/lifted-pddl)! 😄

## Authors

 - [Carlos Núñez Molina](https://github.com/TheAeryan)
