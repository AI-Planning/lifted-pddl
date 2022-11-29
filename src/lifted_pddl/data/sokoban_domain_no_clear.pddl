(define (domain typed-sokoban)
(:requirements :typing :negative-preconditions)
(:types loc)

(:predicates 
             (at-robot ?l - loc)
             (at-box ?l - loc)
             (connected-up ?l1 - loc ?l2 - loc)
             (connected-right ?l1 - loc ?l2 - loc) 
)


(:action move-up
    :parameters (?from - loc ?to - loc)
    :precondition (and 
                    (at-robot ?from)
                    (not (at-box ?to))
                    (connected-up ?from ?to)
                  )
    :effect (and 
                (not (at-robot ?from))
                (at-robot ?to)
            )
)

(:action move-down
    :parameters (?from - loc ?to - loc)
    :precondition (and 
                    (at-robot ?from)
                    (not (at-box ?to))
                    (connected-up ?to ?from)
                  )
    :effect (and 
                (not (at-robot ?from))
                (at-robot ?to)
            )
)

(:action move-right
    :parameters (?from - loc ?to - loc)
    :precondition (and 
                    (at-robot ?from)
                    (not (at-box ?to))
                    (connected-right ?from ?to)
                  )
    :effect (and 
                (not (at-robot ?from))
                (at-robot ?to)
            )
)

(:action move-left
    :parameters (?from - loc ?to - loc)
    :precondition (and 
                    (at-robot ?from)
                    (not (at-box ?to))
                    (connected-right ?to ?from)
                  )
    :effect (and 
                (not (at-robot ?from))
                (at-robot ?to)
            )
)



(:action push-up
    :parameters (?l1 - loc ?l2 - loc ?l3 - loc)
    :precondition (and
                    (at-robot ?l1)
                    (at-box ?l2)
                    (not (at-box ?l3))
                    (connected-up ?l1 ?l2)
                    (connected-up ?l2 ?l3)
                  )
    :effect (and
                (not (at-robot ?l1))
                (at-robot ?l2)
                (not (at-box ?l2))
                (at-box ?l3)
            )
)

(:action push-down
    :parameters (?l1 - loc ?l2 - loc ?l3 - loc)
    :precondition (and
                    (at-robot ?l1)
                    (at-box ?l2)
                    (not (at-box ?l3))
                    (connected-up ?l2 ?l1)
                    (connected-up ?l3 ?l2)
                  )
    :effect (and
                (not (at-robot ?l1))
                (at-robot ?l2)
                (not (at-box ?l2))
                (at-box ?l3)
            )
)

(:action push-right
    :parameters (?l1 - loc ?l2 - loc ?l3 - loc)
    :precondition (and
                    (at-robot ?l1)
                    (at-box ?l2)
                    (not (at-box ?l3))
                    (connected-right ?l1 ?l2)
                    (connected-right ?l2 ?l3)
                  )
    :effect (and
                (not (at-robot ?l1))
                (at-robot ?l2)
                (not (at-box ?l2))
                (at-box ?l3)
            )
)

(:action push-left
    :parameters (?l1 - loc ?l2 - loc ?l3 - loc)
    :precondition (and
                    (at-robot ?l1)
                    (at-box ?l2)
                    (not (at-box ?l3))
                    (connected-right ?l2 ?l1)
                    (connected-right ?l3 ?l2)
                  )
    :effect (and
                (not (at-robot ?l1))
                (at-robot ?l2)
                (not (at-box ?l2))
                (at-box ?l3)
            )
)

)





