;;   0 1 2
;; 0 x
;; 1 x
;; 2 r x
;; 3

(define (problem sokoban-problem)

(:domain typed-sokoban)

(:objects
	l0-0 l0-1 l0-2 l1-0 l1-1 l1-2 l2-0 l2-1 l2-2 l3-0 l3-1 l3-2 - loc
)

(:init
	(connected-up l3-0 l2-0)
	(connected-up l2-0 l1-0)
	(connected-up l1-0 l0-0)

	(connected-up l3-1 l2-1)
	(connected-up l2-1 l1-1)
	(connected-up l1-1 l0-1)

	(connected-up l3-2 l2-2)
	(connected-up l2-2 l1-2)
	(connected-up l1-2 l0-2)

	(connected-right l0-0 l0-1)
	(connected-right l0-1 l0-2)

	(connected-right l1-0 l1-1)
	(connected-right l1-1 l1-2)

	(connected-right l2-0 l2-1)
	(connected-right l2-1 l2-2)

	(connected-right l3-0 l3-1)
	(connected-right l3-1 l3-2)


	(at-robot l2-0)
	(at-box l2-1)
	(at-box l0-0)
	(at-box l1-0)
)

(:goal (and
	(not (at-robot l2-0))
	(at-robot l1-0)
))
)