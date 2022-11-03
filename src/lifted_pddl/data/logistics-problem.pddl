(define (problem bw_both_generative_policies_0)

(:domain logistics)

(:objects
	c0 c1 c2 c3 c4 c5 - city
	l0 l1 l2 l3 l4 l5 l6 l7 l8 l9 l10 l11 l12 l13 l14 l15 l16 l17 l18 l19 l20 l21 l22 l23 l24 - location
	l25 l26 l27 l28 l29 - airport
	t1 t2 t3 t4 t5 t6 t7 t8 t9 t10 - truck
	a1 a2 a3 a4 a5 - airplane
	p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 - package
)

(:init
	(in-city l0 c0)
	(in-city l1 c0)
	(in-city l2 c0)
	(in-city l3 c0)
	(in-city l4 c0)

	(in-city l5 c1)
	(in-city l6 c1)
	(in-city l7 c1)
	(in-city l8 c1)
	(in-city l9 c1)

	(in-city l10 c2)
	(in-city l11 c2)
	(in-city l12 c2)
	(in-city l13 c2)
	(in-city l14 c2)

	(in-city l15 c3)
	(in-city l16 c3)
	(in-city l17 c3)
	(in-city l18 c3)
	(in-city l19 c3)

	(in-city l20 c4)
	(in-city l21 c4)
	(in-city l22 c4)
	(in-city l23 c4)
	(in-city l24 c4)

	(in-city l25 c5)
	(in-city l26 c5)
	(in-city l27 c5)
	(in-city l28 c5)
	(in-city l29 c5)

	(at t1 l1)
	(at t2 l2)
	(at t3 l3)
	(at t4 l4)
	(at t5 l5)
	(at t6 l6)
	(at t7 l7)
	(at t8 l8)
	(at t9 l9)
	(at t10 l10)

	(at a1 l25)
	(at a2 l26)
	(at a3 l27)
	(at a4 l28)
	(at a5 l29)

	(at p0 l0)
	(at p1 l1)
	(at p2 l2)
	(at p3 l12)
	(at p4 l20)
	(at p5 l20)

	(at p6 l21)
	(at p7 l21)
	(at p8 l21)
	(at p9 l22)
	(at p10 l26)

	(in p11 t1)
	(in p12 t1)
	(in p13 t2)
	(in p14 a1)
	(in p15 a2)
)

(:goal (and
	(in-city l0 c0)
	(in-city l1 c0)
	(in-city l2 c0)
	(in-city l3 c0)
	(in-city l4 c0)

	(in-city l5 c1)
	(in-city l6 c1)
	(in-city l7 c1)
	(in-city l8 c1)
	(in-city l9 c1)

	(in-city l10 c2)
	(in-city l11 c2)
	(in-city l12 c2)
	(in-city l13 c2)
	(in-city l14 c2)

	(in-city l15 c3)
	(in-city l16 c3)
	(in-city l17 c3)
	(in-city l18 c3)
	(in-city l19 c3)

	(in-city l20 c4)
	(in-city l21 c4)
	(in-city l22 c4)
	(in-city l23 c4)
	(in-city l24 c4)

	(in-city l25 c5)
	(in-city l26 c5)
	(in-city l27 c5)
	(in-city l28 c5)
	(in-city l29 c5)

	(at t1 l1)
	(at t2 l2)
	(at t3 l3)
	(at t4 l4)
	(at t5 l5)
	(at t6 l6)
	(at t7 l7)
	(at t8 l8)
	(at t9 l9)
	(at t10 l10)

	(at a1 l25)
	(at a2 l26)
	(at a3 l27)
	(at a4 l28)
	(at a5 l29)

	(at p0 l0)
	(at p1 l1)
	(at p2 l2)
	(at p3 l12)
	(at p4 l20)
	(at p5 l20)

	(at p6 l21)
	(at p7 l21)
	(at p8 l21)
	(at p9 l22)
	(at p10 l26)

	(in p11 t1)
	(in p12 t1)
	(in p13 t2)
	(in p14 a1)
	(in p15 a2)
))
)