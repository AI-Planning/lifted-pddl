(define (problem BW-rand-3)

(:domain blocksworld)

(:objects b1 b2 b3 - block)

(:init
(handempty)
(on b1 b2)
(ontable b2)
(on b3 b1)
(clear b3)
)

(:goal (and))
)
