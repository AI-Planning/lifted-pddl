from operator import itemgetter
from collections import deque
from itertools import product, chain
import copy

from tarski.io import PDDLReader
from tarski.syntax.formulas import CompoundFormula, QuantifiedFormula, Atom
from tarski.fstrips.fstrips import AddEffect, DelEffect

import sys

"""
This class implements functionality for:
	- Parsing PDDL domains and problems
	- Obtaining the actions applicable at the init state of the corresponding problem
	- Obtaining the next state resulting from applying an action to the init state (successor function)

<Limitations>: it only supports:
				- types (as in typed STRIPS) 
				- existential preconditions
				- negative preconditions (although only negative atoms and not negative compound formulas)
"""
class Parser:

	def __init__(self):
		self._reader = PDDLReader(raise_on_error=True)

		# Domain information
		self.domain_name = ''
		self.types = set()
		self.type_hierarchy = dict()
		self.predicates = set()
		self.constant_names = tuple()
		self.constant_types = tuple()
		self.actions = set()

		# Problem information
		self.object_names = list()
		self.object_types = list()
		self.atoms = set()
		self.goals = set()
	
	def __str__(self):
		output = ''

		# Domain information
		output += '--- Domain Information ---'
		output += '\n> Domain name: {}'.format(self.domain_name)
		output += '\n> Types: {}'.format(self.types)
		output += '\n> Type hierarchy: {}'.format(self.type_hierarchy)
		output += '\n> Predicates: {}'.format(self.predicates)
		output += '\n> Constant names: {}'.format(self.constant_names)
		output += '\n> Constant types: {}'.format(self.constant_types)
		output += '\n> Actions: {}'.format(self.actions)

		# Problem information
		output += '\n\n--- Problem Information ---'
		output += '\n> Object names (including constants): {}'.format(self.object_names)
		output += '\n> Object types (including constants): {}'.format(self.object_types)
		output += '\n> Atoms in initial state: {}'.format(self.atoms)
		output += '\n> Goals: {}'.format(self.goals)

		return output

	# We use tarski to parse the PDDL domain
	def parse_domain(self, domain_path):
		# <Parse the domain and obtain the domain information in the tarski encoding>
		self._reader.parse_domain(domain_path)
		problem = self._reader.problem
		language = problem.language

		# <Represent the domain information in a different encoding>

		# Domain name
		self.domain_name = problem.domain_name # Example: 'logistics'
		
		# Types
		sorts = language.sorts
		self.types = set([sort.name for sort in sorts]) # Example: {'object', 'city', 'location', 'thing', 'package', 'vehicle', 'truck', 'airplane', 'airport'}

		# Type hierarchy
		ancestor_sorts = language.ancestor_sorts
		# Convert from a dictionary where keys are children types and values are parent types to a dictionary where the keys and values are reversed
		self.type_hierarchy = {parent.name : set([child.name for child in sorts if parent in ancestor_sorts[child]] + [parent.name]) for parent in sorts}
		# Example: {'object': {'object', 'city', 'airplane', 'thing', 'airport', 'location', 'vehicle', 'truck', 'package'}, 'city': {'city'}, 'location': {'airport', 'location'}, 
		# 'thing': {'airplane', 'thing', 'vehicle', 'truck', 'package'}, 'package': {'package'}, 'vehicle': {'vehicle', 'truck', 'airplane'}, 'truck': {'truck'}, 'airplane': {'airplane'}, 'airport': {'airport'}}
		
		# Predicates
		self.predicates = set([(pred.name, tuple([param_type.name for param_type in pred.sort])) for pred in language.predicates if type(pred.name) == str]) # type(pred.name) != str -> the predicate is a built-in (either '=' or '!=')

		# Domain constants
		# Store two lists, containing the name and type of each constant
		constants = language.constants()
		self.constant_names = tuple([const.name for const in constants])
		self.constant_types = tuple([const.sort.name for const in constants])

		# Actions
		"""
		Action representation as a tuple of actions. Each action represented as another tuple (name, action_vars, preconds, effects):
			- name is the action name
			- action_vars is a tuple which contains the type of each action variable, and the class of each variable (either an action parameter or variable introduced
			  by an existential precondition)
			- preconds contains the action preconditions
			- effects contains the action effects
		"""
		self.actions = set()

		for action in problem.actions.items():
			# Variables and var_names correspond to both variables associated with the action parameters and also
			# those associated with existential preconditions (which do not appear in the action parameters)
			
			# Obtain variables in action parameters
			variables = action[1].parameters.vars()
			variables_class = ['param']*len(variables) # Class of each variable: either 'param' (action parameter) or 'exists' (variable introduced by existential precondition)

			# Obtain variables in existential preconditions
			preconds = action[1].precondition
			# preconds = preconds.subformulas if isinstance(preconds, CompoundFormula) else [preconds] # Previous version
			preconds_subformulas = preconds.subformulas if isinstance(preconds, CompoundFormula) else [preconds]
			exist_variables = [var for precond in preconds_subformulas if (isinstance(precond, QuantifiedFormula) and precond.quantifier.name == 'Exists') for var in precond.variables]
			
			# <Note>: It is important that variables corresponding to action parameters go before variables corresponding to existential preconditions
			variables.extend(exist_variables)
			variables_class.extend(['exists']*len(exist_variables))
			variables_class = tuple(variables_class)

			# Obtain variable names
			var_names = [var.symbol for var in variables]

			# Action variables, as a tuple of their types
			# It includes all action variables. Right now, that means it includes action parameters and variables introduced by existential preconditions
			# To see what each variable corresponds to, use is_action_param and has_exist_quantifier.
			# Example: ('truck', 'location', 'location', 'city')
			action_variables = tuple([var.sort.name for var in variables])

			# Action preconditions, as a tuple made up of every precondition
			# Each precondition is represented by a tuple (preffix, predicate_name, vars)
			# Preffix is False if the precondition is a negative precondition, and True otherwise
			# Variables are substituted by their corresponding parameter index
			# Example: ( (True, 'at', (0, 1)), (False, 'in-city', (1, 3)), (True, 'in-city', (2, 3)) )

			# preconds is a negated formula
			if isinstance(preconds, CompoundFormula) and preconds.connective.name.lower() == 'not':
				preconds_list = [(False, preconds)]
			else:
				preconds_list = [(True, preconds)]

			preconds_modified = True
			# Recursively process the formulas and subformulas in preconds_list
			# until we have removed all the nesting levels (i.e., obtained all the subformulas
			# and removed all the existential preconditions)
			while preconds_modified:
				new_preconds_list = []
				preconds_modified = False

				# Remove one nesting level of the formulas in preconds_list
				for preffix, formula in preconds_list:
					# If it is a compoundformula, split it into its subformulas
					if isinstance(formula, CompoundFormula):

						# Negated formula -> we negate the preffix (True -> False, False -> True)
						if formula.connective.name.lower() == 'not':
							subformulas = formula.subformulas

							# If this condition is met, then it means that the negated formula contains
							# several subformulas (i.e., it is in the form of (not (and ...))  )
							# We can't parse compound negated subformulas at the moment
							if len(subformulas) > 1 or not isinstance(subformulas[0], Atom):
								raise Exception("We can't parse negative compound formulas in the preconditions, i.e., '(not (and ...))'")

							subformulas = [(not preffix, f) for f in subformulas]
							new_preconds_list.extend(subformulas)
						
						# Compound formula which is not a negation, but a conjuntion (and ...)
						else:
							subformulas = [(preffix, f) for f in formula.subformulas]
							new_preconds_list.extend(subformulas)

						preconds_modified = True

					# If it has an existential quantifier, just ignore the quantifier
					elif isinstance(formula, QuantifiedFormula):
						
						if preffix == False:
							raise Exception("We can't parse preconditions of the type '(not (exists ... ))'")

						new_preconds_list.append((preffix, formula.formula))
						preconds_modified = True

					# Else, it is a simple formula, so we add it
					else:
						new_preconds_list.append((preffix, formula))

				preconds_list = new_preconds_list


			"""
			# Previous version
			# Decompose QuantifiedFormulas into their subformulas (while ignoring the quantifier)
			preconds_list = []
			for precond in preconds:
				if isinstance(precond, QuantifiedFormula):
					formula = precond.formula

					if isinstance(formula, CompoundFormula):
						preconds_list.extend(formula.subformulas)
					else:
						preconds_list.append(formula)
				else:
					preconds_list.append(precond)
			"""

			preconds_tuple = tuple([(preffix, precond.predicate.name, tuple([var_names.index(var.symbol) for var in precond.subterms])) for preffix, precond in preconds_list])

			# Action effects, as a tuple made up of every effect
			# Each effect is represented as a tuple (is_add_effect, predicate_name, vars)
			# Variables are substituted by their corresponding parameter index
			# Example: ( (False, 'at', (0, 1)), (True, 'at', (0, 2)) ))
			effects = action[1].effects
			effects = tuple([(isinstance(effect, AddEffect), effect.atom.predicate.name, tuple([var_names.index(var.symbol) for var in effect.atom.subterms])) for effect in effects])

			self.actions.add( (action[0], (action_variables, variables_class), preconds_tuple, effects) )

	# We use tarski to parse the PDDL problem
	# <Note>: This method can only be called after parse_domain()
	def parse_problem(self, problem_path):
		problem = self._reader.parse_instance(problem_path)
		language = problem.language

		# Objects
		# Store two lists, containing the name and type of each object
		# <Note>: these list also contain the domain constants. For example, if the domain contains 5 constants and the problem 10 objects,
		#         they will contain 15 different entries.
		objects = language.constants()
		self.object_names = [obj.name for obj in objects]
		self.object_types = [obj.sort.name for obj in objects]

		# Atoms, as a set containing each atom
		# Each atom is represented as a tuple (pred_name, object_indexes), where object_indexes is a tuple containing the index of each object
		# the atom is instantiated on
		# Example: {('in-city', (31, 5)), ('at', (48, 33)), ('in-city', (34, 5)), ('at', (49, 34)), ('at', (41, 12))}
		atoms = problem.init.as_atoms()
		self.atoms = set([(atom.predicate.name, tuple([self.object_names.index(obj.name) for obj in atom.subterms])) for atom in atoms])

		# Goals, as a set containing each goal
		# Each goal is represented as a tuple (is_true, pred_name, object_indexes)
		# object_indexes is a tuple containing the index of each object the atom of the goal is instantiated on
		# is_true equals False if the goal is negative (e.g., (not (at t1 l1)) ) and True otherwise
		
		# The goal contains a single atom (e.g., ( :goal (and (on b2 b1))) )
		if isinstance(problem.goal, Atom):
			self.goals = set([(True, problem.goal.predicate.name, tuple(self.object_names.index(obj.name) for obj in problem.goal.subterms))])			

		else: # The goal contains more than a single atom
			subformulas = problem.goal.subformulas
			self.goals = set([(True, x.predicate.name, tuple(self.object_names.index(obj.name) for obj in x.subterms)) if isinstance(x, Atom) else \
						  (False, x.subformulas[0].predicate.name, tuple(self.object_names.index(obj.name) for obj in x.subformulas[0].subterms)) for x in subformulas])

	# Returns the name of the object whose index is @obj_ind
	def get_object_name(self, obj_ind):
		assert type(obj_ind) == int, "@obj_ind must be an integer"

		return self.object_names[obj_ind]

	# Given a list/tuple of object indexes, it returns a tuple with their names
	def get_object_names(self, obj_ind_list):
		assert type(obj_ind_list) in (list, tuple), "@obj_ind_list must be either a list or a tuple"

		return tuple([self.get_object_name(obj_ind) for obj_ind in obj_ind_list])

	# Returns the type of the object whose index is @obj_ind
	def get_object_type(self, obj_ind):
		assert type(obj_ind) == int, "@obj_ind must be an integer"

		return self.object_types[obj_ind]

	# Given a list/tuple of object indexes, it returns a tuple with their types
	def get_object_types(self, obj_ind_list):
		assert type(obj_ind_list) in (list, tuple), "@obj_ind_list must be either a list or a tuple"

		return tuple([self.get_object_type(obj_ind) for obj_ind in obj_ind_list])

	# Returns the index of the object whose name is @obj_name
	def get_object_index(self, obj_name):
		assert type(obj_name) == str, "@obj_name must be a string"

		return self.object_names.index(obj_name)

	# Given a list/tuple with object names, it returns a tuple with their indexes
	def get_object_indexes(self, obj_name_list):
		assert type(obj_name_list) in (list, tuple), "@obj_name_list must be either a list or a tuple"

		return tuple([self.get_object_index(obj_name) for obj_name in obj_name_list])

	"""
	This method modifies the current state of the problem. More specifically,
	it sets @curr_state_atoms as self.atoms.

	@curr_state_atoms A set with the atoms of the next state, where each atom
					  is in the form ('pred_name', (obj_ind_1, ..., obj_ind_n))					  
	"""
	def set_current_state(self, curr_state_atoms):
		assert type(curr_state_atoms) == set, "@curr_state_atoms must be a set"

		self.atoms = curr_state_atoms.copy() # We copy so that the reference is not shared

	"""
	Auxiliary function used by get_applicable_actions. It receives a set of variable assignments (each one with an arbitrary number of free and bind variables),
	and returns a list with all the full variable assignments obtained from them and which correspond to applicable ground actions.
	The full variable assignments are returned as a tuple of tuples.

	<Note>: @_var_assigns must be a list of lists
	"""
	def _get_applicable_var_assigns_action(self, action, _var_assigns):
		# Obtain information about the domain and problem
		type_hierarchy = self.type_hierarchy
		objects = self.object_types
		atoms = self.atoms # Note: atoms must be a set of tuples and not a set of lists

		action_name, action_var_info, action_preconds, _ = action
		action_vars, vars_class = action_var_info

		# Check nullary preconditions
		# If they are not met, there are no applicable ground actions (and, hence, no valid var assignments)

		# Process action preconditions corresponding to nullary predicates (those of arity 0)
		# Check if each nullary predicate in the preconditions appears in the state atoms.
		# If so, we remove the nullary predicates from the action preconditions and check the rest of the preconditions.
		# If not, the action is not applicable.
		nullary_preconds = [precond for precond in action_preconds if len(precond[2]) == 0]

		nullary_preconds_in_atoms = True
		for nullary_precond in nullary_preconds:
			if nullary_precond[1:] not in atoms: # The nullary precondition does not appear in the atoms
				nullary_preconds_in_atoms = False
				break

		# The current action is not applicable
		if not nullary_preconds_in_atoms:
			return tuple() # empty tuple

		# Remove the nullary predicates from the action preconditions
		action_preconds = [precond for precond in action_preconds if len(precond[2]) > 0]

		# Split the preconditions into positive and negative (i.e., (not ...))
		positive_preconds = [precond for precond in action_preconds if precond[0]==True]
		negative_preconds = [precond for precond in action_preconds if precond[0]==False]

		# List of (possibly partial) variable assignments corresponding to potentially aplicable actions
		var_assigns = copy.deepcopy(_var_assigns) # Deep copy the parameter so that it is not modified
		is_var_bound = [var != -1 for var in var_assigns[0]] # Contains True if the corresponding variable is bound, and False if it's free

		# Process the positive preconditions -> obtain the list of variable assignments which satisfy the positive preconditions
		for precond in positive_preconds:
			_, precond_pred, precond_vars = precond
			new_var_assigns = [] # Will contain the partial variable assignments after we process the current precondition (precond)

			# Obtain mapping from the indexes of the atom's objects to the indexes of the variables in var_assigns
			# Then, select the subset of those indexes which we need to check to see if an atom matches a variable assignment in var_assigns
			# This subset corresponds to those variables which are already bound and also appear at the precondition (precond_vars)
			"""
			Examples:
			- Precondition: ('in-city', (2, 3))
			- Indexes of atom objects: (0, 1)
			- Indexes of variables in var_assigns: (2, 3) -> atom_obj[0] maps to var[2] in var_assigns and atom_obj[1] maps to var[3]

			Let's assume we have var assignments like (6, 8, -1, 5) (vars 0, 1 and 3 are bound, and var 2 is free).
			Then, we only need to check that atom_obj[1] matches var[3] in the var_assignments. Therefore:
			- Indexes of atom objects to check: (1,)
			- Indexes of variables in var_assigns to check: (3,)
			"""
			inds_to_check = [(ind, var) for ind, var in enumerate(precond_vars) if is_var_bound[var]]

			# If len(inds_to_check) == 0, this means that we don't have to check any variable in the assignments for this precondition
			# i.e., as long as an atom is of the correct predicate and its objects of the correct type, all partial variable assignments match the atom
			if len(inds_to_check) == 0:
				no_vars_to_check = True
				atom_obj_inds_to_check, vars_to_check = tuple(), tuple()
			else:
				no_vars_to_check = False	
				atom_obj_inds_to_check, vars_to_check = zip(*inds_to_check)

			for atom in atoms:
				atom_pred, atom_obj_inds = atom

				# Check if the atom's predicate is the same as that of the precondition
				if atom_pred == precond_pred:
					# The types of the objects the atom is instantiated on must inherit from the type of the corresponding parameter type
					types_correct = True
					for atom_obj_ind, precond_var in zip(atom_obj_inds, precond_vars):
						types_correct = types_correct and (objects[atom_obj_ind] in type_hierarchy[action_vars[precond_var]])

					if types_correct:

						for var_assign in var_assigns:
							# Check if the atom matches the current var assignment (var_assign)
							# It is a match if the atom's objects match the objects of the corresponding vars in var_assign for those
							# vars which are bound, i.e., atom_obj_inds[atom_obj_inds_to_check] == var_assign[vars_to_check]
							if no_vars_to_check or itemgetter(*atom_obj_inds_to_check)(atom_obj_inds) == itemgetter(*vars_to_check)(var_assign):
								new_var_assign = var_assign.copy()
								deque(map(new_var_assign.__setitem__, precond_vars, atom_obj_inds), maxlen=0) # The deque is simply to evaluate the map, as in python 3 it has lazy evaluation

								new_var_assigns.append(new_var_assign)


			# Update the partial variable assignments
			var_assigns = new_var_assigns

			# If this happens, then the current precondition is not met for any variable substitution, so the action is not applicable!
			if len(var_assigns) == 0:
				return tuple() # empty tuple (no need to check the remaining preconditions)

			# Bind variables which appear in the precondition
			for var in precond_vars:
				is_var_bound[var] = True


		# Check if there are still partial variable substitutions in var_assigns
		# If there are, the free variables in those variable substitutions can be instantiated
		# on any object of the correct type (they correspond to action parameters which don't appear in any precondition)	
		partial_var_assigns = [var_assign for var_assign in var_assigns if -1 in var_assign]
		full_var_assigns = [var_assign for var_assign in var_assigns if -1 not in var_assign]

		for var_assign in partial_var_assigns:
			# For each var in var_assign, we obtain a tuple with the objects which can be instantiated on it:
			# If var == -1 -> a list with all the obj_inds of the corresponding action parameter type
			# If var != -1 -> simply var
			new_objs_var_assign = [[ind_obj for ind_obj, obj_type in enumerate(objects) if obj_type==action_vars[ind_var]] \
			 					   if var==-1 else (var,) for ind_var, var in enumerate(var_assign)]

			new_var_assigns = product(*new_objs_var_assign) # Cartesian product
			full_var_assigns.extend(new_var_assigns)


		# <Negative preconditions>
		# Remove the variable substitutions which do not satisfy the negative preconditions
		for precond in negative_preconds: 
			_, precond_pred, precond_vars = precond
			new_var_assigns = []

			# Check if each var_assign meets the current negative precondition
			for var_assign in full_var_assigns:
				# Substitute the precondition variables by the objects given by var_assign
				precond_objs = tuple([var_assign[var] for var in precond_vars])
				ground_precond = (precond_pred, precond_objs)

				# Check if the grounded precondition is in the state atoms
				if ground_precond not in atoms:
					new_var_assigns.append(var_assign)

			full_var_assigns = new_var_assigns

			# If there are no var_assigns left, we know that no variable substitution
			# satisfies all the preconditions
			if len(full_var_assigns) == 0:
				return tuple()


		# <Existential preconditions>
		# Remove variables corresponding to existential preconditions from full_var_assigns.
		# We do this because these variables are not action parameters and we know that, for all variable assignments in
		# full_var_assigns, the existential preconditions are met.
		# Example: if the second variable is introduced by an existential precondition, then:
		# 		   full_var_assigns = [[1,2,3], [4,5,6], [1,7,3]] -> [[1,3], [4,6], [1,3]] --- 
		#          -- <remove repeated assignments> ---> [[1,3], [4,6]]
		exists_vars = set([var for var, var_class in enumerate(vars_class) if var_class == 'exists'])

		# Also, convert from list of lists to tuple of tuples
		# set() used to remove repeated assignments
		full_var_assigns = tuple(set([tuple([elem for ind, elem in enumerate(var_assign) if ind not in exists_vars]) for var_assign in full_var_assigns]))

		return full_var_assigns


	def get_applicable_actions(self):
		applicable_actions = dict()

		action_schemas = self.actions

		for action in action_schemas:
			action_name, action_var_info, action_preconds, _ = action
			action_vars, vars_class = action_var_info

			full_var_assigns = self._get_applicable_var_assigns_action(action, [[-1]*len(action_vars)])

			# Save the variable assignments (groundings) which make the current action applicable
			applicable_actions[action_name] = full_var_assigns

		return applicable_actions

	"""
	This method receives a ground action and returns if it is applicable at the current state (given by self.object_names, self.object_types and self.atoms).

	@action_name Name of the action (e.g., 'drive')
	@var_assign Action parameters instantiations, as a list/tuple of object indexes (e.g., (10, 3) -> first action parameter is instantiated on 10-th object 
	            and the second one on the third object)
	"""
	def is_action_applicable(self, action_name, var_assign):
		action_schemas = self.actions
		type_hierarchy = self.type_hierarchy
		objects = self.object_types
		atoms = self.atoms # Note: atoms must be a set of tuples and not a set of lists

		# Select the action_schema corresponding to @action_name
		action = [action_schema for action_schema in action_schemas if action_schema[0]==action_name]
		assert len(action)==1, "There are several action schemas with the same name!"
		action = action[0]

		action_name, action_var_info, action_preconds, action_effects = action
		action_vars, vars_class = action_var_info

		# Obtain the action parameters, i.e., those variables of class 'param'
		action_params = [var for var, var_class in zip(action_vars, vars_class) if var_class == 'param']

		assert len(var_assign) == len(action_params), "The number of variables in var_assign must be the same that the name of action parameters."

		# Check if the objects the action parameters are instantiated on are of the correct type
		for obj_ind, param_type in zip(var_assign, action_params):
			if objects[obj_ind] not in type_hierarchy[param_type]:
				return False # If a single parameter is of the incorrect type, we know the action is not applicable

		# Add free variables to @var_assign, accounting for the variables in existential preconditions
		num_exist_vars = vars_class.count('exists')
		var_assigns = [list(var_assign) + [-1]*num_exist_vars] # Note: we know that vars corresponding to existential preconditions go after vars corresponding to action params

		# Obtain all the variable instantiations where the bind variables correspond to the variables in @var_assign
		# and the free variables correspond to the variables given by existential preconditions
		full_var_assigns = self._get_applicable_var_assigns_action(action, var_assigns)

		# If the action is applicable, there will be at least one valid variable assignment in full_var_assigns
		return len(full_var_assigns) > 0

	"""
	Successor function.
	This method receives a ground action and returns the next state as a result of applying the action to the current state
	(given by self.object_names, self.object_types and self.atoms).
	The next state is returned as the new set of atoms which are true.
	If @check_action_applicability is True, we check if the action is applicable before applying it to the current state.
	In case it is not applicable, we assume the next state is equal to the current state (the state does not change).
	If @check_action_applicability is False, we assume the action is applicable at the current state.

	@action_name Name of the action (e.g., 'drive')
	@var_assign Action parameters instantiations, as a list/tuple of object indexes (e.g., (10, 3) -> first action parameter is instantiated on 10-th object 
	            and the second one on the third object)
	"""
	def get_next_state(self, action_name, var_assign, check_action_applicability=True):
		action_schemas = self.actions
		type_hierarchy = self.type_hierarchy
		objects = self.object_types
		atoms = self.atoms # Note: atoms must be a set of tuples and not a set of lists

		# Select the action_schema corresponding to @action_name
		action = [action_schema for action_schema in action_schemas if action_schema[0]==action_name]
		assert len(action)==1, "There are several action schemas with the same name!"
		action = action[0]

		# Copy the atoms, so that the new_atoms don't share the reference
		new_atoms = atoms.copy()

		if check_action_applicability:
			is_applicable = self.is_action_applicable(action_name, var_assign)

			# If the action is not applicable, the set of atoms will not change (the state remains the same)
			if not is_applicable:
				return new_atoms

		# Perform the variable substitutions for the action_effects (i.e., ground the variables) according to @var_assign
		_, action_var_info, action_preconds, action_effects = action
		action_vars, vars_class = action_var_info

		ground_action_effects = []
		for effect in action_effects:
			ground_vars = tuple([var_assign[var] for var in effect[2]])
			ground_effect = tuple([effect[0], effect[1], ground_vars])
			ground_action_effects.append(ground_effect)

		# Apply the ground effects:
		# Add effects (effect[0]==True) -> add the corresponding atom
		# Del effects (effect[0]==False) -> delete the corresponding atom
		# Note: we assume that no effects are in both the add and delete list
		for effect in ground_action_effects:
			effect_atom = (effect[1], effect[2])

			if effect[0]: # Add effect		
				if effect_atom not in new_atoms: # If the corresponding atom does already exist in the state atoms, we do nothing
					new_atoms.add(effect_atom)
			else: # Delete effect
				if effect_atom in new_atoms: # If the corresponding atom does not exist in the state atoms, we do nothing
					new_atoms.remove(effect_atom)

		return new_atoms

	"""
	Receives as @ground_actions the set of applicable actions in the dictonary form returned by get_applicable_actions()
	and returns the same applicable actions in PDDL format (e.g., (drive t1 l2 l3 c1), (unload a8 p6 l3), ...).
	If you want to encode the actions applicable at the current state (given by self), you can simply do
	parser.encode_ground_actions_as_pddl(parser.get_applicable_actions(), output_format='str') (assuming parser is an
	instance of the Parser class).

	@output_format Either 'str' or 'tuple'. 
				   If 'str', the output is a set of actions, where each action is a string like '(drive t1 l2 l3 c1)'.
	               If 'list', the output is a set of actions, where each action is a tuple like tuple(('drive', 't1', 'l2', 'l3', 'c1')).
	               Suggestion: choose @output_format='str' if you want to dump the result to a file or print it to the terminal.
	                           choose @output_format='tuple' if you want to process the result in Python (instead of printing it).
	"""
	def encode_ground_actions_as_pddl(self, ground_actions, output_format):
		assert output_format in ('str', 'tuple'), "@output_format must be either 'str' or 'tuple'"
		obj_names = self.object_names

		if output_format == 'tuple':
			actions_pddl_format = set([tuple([action_name] + [obj_names[var] for var in var_assign]) for action_name in ground_actions \
								   for var_assign in ground_actions[action_name]])
		else:
			actions_pddl_format = set(['({} '.format(action_name) + ' '.join(obj_names[var] for var in var_assign) + ')' \
			                       for action_name in ground_actions for var_assign in ground_actions[action_name]])

		return actions_pddl_format

	"""
	Receives as @atoms the set of atoms in the form returned by get_next_state() and returns the same set of atoms in PDDL
	format (e.g., (at t1 l2), (in p2 a8), ...)
	If you want to encode the atoms corresponding to the current state (given by self), you can simply do
	parser.encode_atoms_as_pddl(parser.atoms, output_format='str') (assuming parser is an
	instance of the Parser class).
	If you want to encode the atoms corresponding to the next state obtained by executing an action (action_to_apply) at the current state (given by self),
	you can simply do parser.encode_atoms_as_pddl(parser.get_next_state(action_to_apply), output_format='str').

	@output_format Either 'str' or 'tuple'. 
				   If 'str', the output is a set of atoms, where each atom is a string like '(at t1 l2)'.
	               If 'list', the output is a set of atoms, where each atom is a tuple like tuple(('at', 't1', 'l2')).
	               Suggestion: choose @output_format='str' if you want to dump the result to a file or print it to the terminal.
	                           choose @output_format='tuple' if you want to process the result in Python (instead of printing it).
	"""
	def encode_atoms_as_pddl(self, atoms, output_format):
		assert output_format in ('str', 'tuple'), "@output_format must be either 'str' or 'tuple'"
		obj_names = self.object_names

		if output_format == 'tuple':
			atoms_pddl_format = set([tuple([atom[0]] + [obj_names[obj_ind] for obj_ind in atom[1]]) for atom in atoms])
		else:
			atoms_pddl_format = set(['({} '.format(atom[0]) + ' '.join(obj_names[obj_ind] for obj_ind in atom[1]) + ')' \
									 if len(atom[1]) > 0 else '({})'.format(atom[0]) for atom in atoms])
								# We need the if else condition in the list comprehension because, without it,
								# atoms corresponding to nullary predicates are printed with a blank space at the end
								# (e.g., (handempty ) <- note the blank space)

		return atoms_pddl_format

	"""
	This method returns the PDDL encoding of the problem stored in the parser.

	@problem_name Name of the PDDL problem to output
	"""
	def dump_pddl_problem(self, problem_name):
		# <Definition (and problem name)>
		pddl_problem = f"(define (problem {problem_name})\n\n"

		# <Domain name>
		pddl_problem += f'(:domain {self.domain_name})\n\n'

		# <Objects>

		# Begin :objects
		pddl_problem += '(:objects\n'

		# Get objects of each type - From ['block', 'block', 'circle'] to {'block': ['A','B'], 'circle':['C']}
		object_types_dict = dict()

		for name, t in zip(self.object_names, self.object_types):
			if t in object_types_dict:
				object_types_dict[t].append(name)
			else:
				object_types_dict[t] = [name]

		for key in object_types_dict:
			pddl_problem += '\t'

			for name in object_types_dict[key]:
				pddl_problem += f'{name} '

			pddl_problem += f'- {key}\n'

		# End :objects
		pddl_problem += ')\n\n'

		# <Initial state atoms (:init)>

		# Begin :init
		pddl_problem += '(:init\n'

		# Add each atom of the initial state
		for atom in self.atoms:
			pddl_problem += f'\t({atom[0]}'

			for obj_ind in atom[1]:
				pddl_problem += f' {self.get_object_name(obj_ind)}'

			pddl_problem += ')\n'

		# End :init
		pddl_problem +=')\n\n'

		# <Goal atoms (:goal)>

		# Begin :goal

		pddl_problem += '(:goal (and\n'

		# Add goal atoms
		for atom in self.goals:
			pddl_problem += f'\t({atom[1]}'

			for obj_ind in atom[2]:
				pddl_problem += f' {self.get_object_name(obj_ind)}'

			pddl_problem += ')\n'

		# End :goal
		pddl_problem += '))\n'

		# <End>
		pddl_problem += ")"

		# <<Return the PDDL problem>>
		return pddl_problem