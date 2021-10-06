from functools import partial
from math import ceil
from random import shuffle




### PROMOTION ####
def promotion_function_factory(P):
    if P.promotion_model == "topPromotability":
        return get_top_k_by_promotability


def get_top_k_by_promotability(hire_from, n_to_hire, n_women='unbounded'):
    if n_women == 'unbounded' or n_women <= 0:
        hf = sorted(hire_from,
                    key=lambda x: x.promotability_perception,
                    reverse=True)
        hired,remain = hf[:n_to_hire],hf[n_to_hire:]
        lower_bar = hired[-1].original_promotability
    else:
        women = sorted([i for i in hire_from if i.is_male == False],key=lambda x:x.promotability_perception,reverse= True)
        men = sorted([i for i in hire_from if i.is_male == True],key = lambda x:x.promotability_perception,reverse = True)
        n_internal_women = min(len(women),n_women,n_to_hire)
#         n_external_women = n_women - n_internal_women
        internal_women = women[:n_internal_women]
        n_rest = n_to_hire - n_internal_women # which has women and men
        rest = sorted(women[n_internal_women:] + men, key = lambda x: x.promotability_perception,reverse =True)  
        remain = rest[n_rest:] 
        hired = rest[:n_rest] + internal_women
        # update unfair promotion passed:
        lower_bar = rest[n_rest-1].original_promotability if n_rest else float('inf')
        lower_bar = min(internal_women[-1].original_promotability,lower_bar) if internal_women else lower_bar
        assert len(hired) == n_to_hire
    # update promotion passed 
    for agt in remain:
        if agt.original_promotability > lower_bar:
            agt.num_unfair_promotion_passed += 1
        agt.num_promotion_passed += 1
    return hired,remain   

### Leave Functions ####
def leave_function_factory(P):
    if P.leave_function_type == "simple":
        return simple_leave_fn
    elif P.leave_function_type == "unfair":
        return unfair_promotion_leave_fn

def simple_leave_fn(P, agents, level):
    # how many agents should leave?
    n_to_leave = int(ceil(P.pct_leave_at_level[level] * len(agents)))
    # select randomly
    shuffle(agents)
    return agents[:n_to_leave], agents[n_to_leave:]

def unfair_promotion_leave_fn(P,agents,level):
    if level == 0:
        simple_leave_fn(P,agents,level)
    else:
        n_to_leave = int(ceil(P.pct_leave_at_level[level] * len(agents)))
        agents.sort(key= lambda x: x.num_unfair_promotion_passed,reverse = True)
        return agents[:n_to_leave],agents[n_to_leave:]
