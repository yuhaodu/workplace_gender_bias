import functools
import numpy as np
import pandas as pd
from itertools import product
import math
###### Constants
MALE = 0
FEMALE = 1

# make it more obvious and succinct to draw a single binary variable
draw_binary = functools.partial(np.random.binomial,n=1)

np.set_printoptions(suppress=True)


def draw_reward_penalty(is_stretch_project,P):
    if is_stretch_project:
        return np.random.normal(P.stretch_project_reward_mean,P.stretch_project_reward_sd)
    else:
        return np.random.normal(P.project_reward_mean,P.project_reward_sd)
    
def calculate_d(x):
    return math.sqrt(4 * x / (1-x))


def tsn(x):
    return "\t".join([str(y) if type(y) is int else '{:.5f}'.format(y) for y in x]) + "\n"


class ParameterHolder(object):
  def __init__(self, adict):
    self.__dict__.update(adict)


def scale_to_probability(x):
    exp_x = np.exp(x)
    exp_x = exp_x / (1 + np.sum(exp_x))
    return exp_x/np.sum(exp_x)


def expand_grid(dictionary):
    return pd.DataFrame([row for row in product(*dictionary.values())],
                        columns=dictionary.keys())


def chunkify(lst,n):
    return [lst[i::n] for i in xrange(n)]


def gen_stats(agents):
    st = np.matrix([(a.promotability,
                     a.num_successful_projects,
                     a.num_failed_projects,
                     a.num_promotion_passed,
                     a.num_unfair_promotion_passed,
                     a.numBias) for a in agents])
    st = st.mean(axis=0).tolist()[0]
    if len(st) == 6:
        return st
    return [-1,-1,-1,-1,-1,-1 ]

def print_stats(P, turn, company_hierarchy):

    # Write out number of men and women at each level
    for level_iter, level in enumerate(company_hierarchy):
        n_men = sum([agent.is_male for agent in level])
        n_women = len(level) - n_men

        fem_stats = gen_stats([a for a in level if not a.is_male])
        male_stats = gen_stats([a for a in level if a.is_male])

        P.turn_output_file.write(tsn(fem_stats + male_stats + [n_men,n_women,turn,level_iter, P.run_number,P.replication_number]))
        
        
def print_stats_promotion(P, turn, company_hierarchy,men_leave,women_leave,men_promoted,women_promoted,bias_each_level):

    # Write out number of men and women at each level
    for level_iter, level in enumerate(company_hierarchy):
        n_men = sum([agent.is_male for agent in level])
        n_women = len(level) - n_men
        P.turn_output_promotion_file.write(tsn([n_men,n_women,men_leave[level_iter],women_leave[level_iter],men_promoted[level_iter],women_promoted[level_iter],turn,level_iter, P.run_number,P.replication_number,bias_each_level[level_iter]] ))
        

def print_agents(P,company_hierarchy):
    
    for level_iter,level in enumerate(company_hierarchy):
        for agent in level:
            for index in range(len(agent.promotion_cycle)):
                P.turn_output_agent_file.write(tsn([ \
                agent.id,\
                agent.promotion_cycle[index],\
                agent.hist_promotability_perception[index],\
                agent.hist_num_successful_projects[index],\
                agent.hist_num_failed_projects[index],\
                agent.level_iter[index],
                agent.is_male]))
                
def print_agents_each_turn(P,company_hierarchy,promotion_cycle):
    
    for level_iter,level in enumerate(company_hierarchy):
        for agent in level:
            P.turn_output_agent_file.write(tsn([ \
            agent.id,\
            promotion_cycle,\
            agent.promotability_perception,\
            agent.num_successful_projects,\
            agent.num_failed_projects,\
            level_iter,
            agent.is_male]))
    
        
        
def print_leave_stats(P,turn,leaving_agents,level_iter):
    
    n_men = sum([agent.is_male for agent in leaving_agents])
    n_women = len(leaving_agents) - n_men
    
    fem_stats = gen_stats([a for a in leaving_agents if not a.is_male])
    male_stats = gen_stats([a for a in leaving_agents if a.is_male])
    
    P.turn_output_leave_file.write(tsn(fem_stats + male_stats + [n_men,n_women,turn,level_iter,P.run_number,P.replication_number]))
    


    # mean_female_comp_perc = np.mean([a.competence_perception for a in agents if a.sex == FEMALE])
    # mean_male_comp_perc = np.mean([a.competence_perception for a in agents if a.sex == MALE])
    # mean_female_competence = np.mean([a.competence for a in agents if a.sex == FEMALE])
    # mean_male_competence = np.mean([a.competence for a in agents if a.sex == MALE])
    # n_male = len([a for a in agents if a.sex == MALE])
    # n_female = len([a for a in agents if a.sex == FEMALE])
    #
    # P.turn_output_file.write(tsn([mean_female_comp_perc,
    #                               mean_male_comp_perc,
    #                               mean_female_competence,
    #                               mean_male_competence,
    #                               n_male, n_female, proj_iter,
    #                               P.run_number,
    #                               P.replication_number]))




