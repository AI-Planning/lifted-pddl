(define (problem bw_both_generative_policies_8)

(:domain blocksworld)

(:objects
	obj0 obj1 obj2 obj3 obj4 obj5 obj6 obj7 obj8 obj9 obj10 - block
)

(:init
	(ontable obj0)
	(ontable obj1)
	(ontable obj2)
	(on obj3 obj1)
	(on obj4 obj0)
	(on obj5 obj4)
	(on obj6 obj2)
	(on obj7 obj5)
	(on obj8 obj7)
	(on obj9 obj3)
	(clear obj8)
	(clear obj6)
	(clear obj9)
	(holding obj10)
)

(:goal (and
	(holding obj7)
	(ontable obj8)
	(ontable obj10)
	(on obj9 obj10)
	(ontable obj2)
	(on obj3 obj2)
	(on obj5 obj8)
	(clear obj9)
	(ontable obj0)
	(on obj1 obj4)
	(clear obj5)
	(clear obj3)
	(on obj4 obj0)
	(clear obj6)
	(on obj6 obj1)
))
)