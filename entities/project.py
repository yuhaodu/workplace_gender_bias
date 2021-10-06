
from util import draw_binary,draw_reward_penalty
from random import shuffle
from functools import partial
import math
class Project():

    def __init__(self,
                 agent=None,
                 agent_list=None,
                 is_stretch_project=False,
                 determine_success_fn = None,
                 P=None):
        if agent:
            self.agents = [agent]
            self.is_solo_project = True
            self.is_group_project = False
        elif agent_list:
            self.agents = agent_list
            self.is_solo_project = False
            self.is_group_project = True
        else:
            raise Exception("No agents provided to project!")

        if not determine_success_fn:
            self.is_successful = draw_binary(p=.5)
        else:
            self.is_successful = determine_success_fn(self)
        if self.is_successful:
            self.reward_penalty = draw_reward_penalty(is_stretch_project,P)
        else:
            self.reward_penalty = -draw_reward_penalty(is_stretch_project,P)
            
        self.is_stretch = is_stretch_project
        


def project_function_factory(P,percent_women_at_above_level, type):

    # TODO: I have to clean this up at some point
    # Add in stereotype fit variables
    if P.project_bias_type == 'threshold':
        woman_boost_multiplier = P.project_promotability_boost_women_percent_of_men
        woman_drop_multiplier = P.project_promotability_drop_women_percent_of_men
        if percent_women_at_above_level < P.project_prototype_percentage_threshold:
            woman_boost_multiplier = 1 - ((1- woman_boost_multiplier) * P.project_prototype_boost_bias_multiplier)
            woman_drop_multiplier =  ((woman_drop_multiplier - 1) * P.project_prototype_drop_bias_multiplier) + 1
    elif P.project_bias_type == 'micro_macro':
        if percent_women_at_above_level >= 0.5:
            woman_boost_multiplier,woman_drop_multiplier = 1,1
        else:
            bias = 0.5 - percent_women_at_above_level  # we can try different functions here
            woman_boost_multiplier,woman_drop_multiplier = 1-bias,1+bias
        # make woman_boost_multiplier a function of percent_women_at_above_level

    if woman_boost_multiplier < 0:
        woman_boost_multiplier = 0
    if woman_drop_multiplier > 10:
        woman_drop_multiplier = 10
    if type == 'success':
        return partial(simple_project_promotability,
                       man_boost=(P.project_promotability_boost),
                       woman_boost=(P.project_promotability_boost*woman_boost_multiplier),
                       stretch_boost = P.project_promotability_stretch_multiplier,
                       woman_mixed_group_diff=P.project_women_mixed_group_percent_drop_success,
                       complaint_percentage=P.project_women_percent_complain_on_mixed_success,
                       complaint_boost_impact=P.project_women_additional_promotability_percent_drop_on_complain
                       )
    elif type == 'fail':
        return partial(simple_project_promotability,
                       man_boost=-(P.project_promotability_drop),
                       woman_boost=-(P.project_promotability_drop*woman_drop_multiplier),
                       stretch_boost=P.project_promotability_stretch_multiplier,
                       woman_mixed_group_diff=P.project_women_mixed_group_percent_increase_failure,
                       complaint_percentage=0.,
                       complaint_boost_impact=0.
                       )
    raise Exception("Not implemented project function")
    
    
def effect_size_maker(percent_male_at_above_level,P,turn):
    if P.promotion_intervention and turn >= P.promotion_intervention_span[0]:  
        external_male_at_above_level = P.external_male_at_above_level
        macro_norm = P.macro_norm
        meso_norm = (percent_male_at_above_level - 0.5) * macro_norm / (external_male_at_above_level -0.5)
        weight = P.promotion_intervention_norm
        effect_size = weight * meso_norm + (1-weight) * macro_norm
    else:
        external_male_at_above_level = P.external_male_at_above_level
        macro_norm = P.macro_norm
        meso_norm = (percent_male_at_above_level - 0.5) * macro_norm / (external_male_at_above_level -0.5)
        weight = P.weight
        effect_size = weight * meso_norm + (1-weight) * macro_norm
    return effect_size

def bias_function_factory(P,percent_male_at_above_level, type,turn):

### Bias with downward causation
    effect_size = effect_size_maker(percent_male_at_above_level,P,turn) # gender bias constitutes of proportion of variance
    sign = - 1
    if effect_size < 0: effect_size = -effect_size; sign = 1
    idv_succ_bias = sign * math.sqrt(4 * effect_size / (1 - effect_size))
    idv_fail_bias = sign * math.sqrt(4 * effect_size / (1 - effect_size))
    mixed_succ_bias = sign * math.sqrt(4 * effect_size / (1 - effect_size))
    mixed_fail_bias = sign *  math.sqrt(4 * effect_size / (1 - effect_size))

### Fixed bias effect size
#     sign = -1
#     idv_succ_bias = sign * math.sqrt(4 * P.idv_succ_effect_size / (1 - P.idv_succ_effect_size))
#     idv_fail_bias = sign * math.sqrt(4 * P.idv_fail_effect_size / (1 - P.idv_fail_effect_size))
#     mixed_succ_bias = sign * math.sqrt(4 * P.mixed_succ_effect_size / (1 - P.mixed_succ_effect_size))
#     mixed_fail_bias = sign * math.sqrt(4 * P.mixed_fail_effect_size / (1 - P.mixed_fail_effect_size))
    
### Fixed average bias
#     idv_succ_bias = P.idv_succ_bias
#     idv_fail_bias = P.idv_fail_bias 
#     mixed_succ_bias = P.mixed_succ_bias
#     mixed_fail_bias = P.mixed_fail_bias

    if type == 'success':
        return partial(complex_project_promotability,
                        pure_gender_bias = idv_succ_bias,    # influence on female           
                        mix_group_bias = mixed_succ_bias,        # influence on female
                        complaint_percentage = P.project_women_percent_complain_on_mixed_success,
                        complaint_bias = P.complaint_bias           # influence on female
                       ),idv_succ_bias/P.project_reward_mean
    elif type == 'fail':
        return partial(complex_project_promotability,             
                        pure_gender_bias = idv_fail_bias,                  
                        mix_group_bias = mixed_fail_bias,
                        complaint_percentage=0,
                        complaint_bias = P.complaint_bias
                       ),idv_fail_bias/P.project_reward_mean
    raise Exception("Not implemented project function")
          

def complex_project_promotability(proj,pure_gender_bias,mix_group_bias,complaint_percentage,complaint_bias):
    if proj.is_solo_project:
        if proj.agents[0].is_male:
            proj.agents[0].promotability_perception += proj.reward_penalty
        else:
            proj.agents[0].promotability_perception += proj.reward_penalty 
            proj.agents[0].promotability_perception += pure_gender_bias
            if pure_gender_bias!= 0: proj.agents[0].numBias += 1
    else:
        n_men = sum([a.is_male for a in proj.agents ])
        n_women = sum([not a.is_male for a in proj.agents])
        if n_men == 0:
            for a in proj.agents:
                a.promotability_perception += proj.reward_penalty 
                a.promotability_perception += pure_gender_bias
                if pure_gender_bias!= 0: a.numBias += 1
        elif n_women == 0:
            for a in proj.agents:
                a.promotability_perception += proj.reward_penalty 
        else:
            for a in proj.agents:
                if a.is_male:
                    a.promotability_perception += proj.reward_penalty
                else:
                    indiv_woman_boost = proj.reward_penalty
                    indiv_woman_boost += pure_gender_bias
                    indiv_woman_boost += mix_group_bias
                    if pure_gender_bias!= 0: a.numBias += 1
                    if mix_group_bias!=0: a.numBias += 1
#                     a.promotability_perception += indiv_woman_boost
                    if complaint_percentage > 0 and draw_binary(p=complaint_percentage) and (pure_gender_bias < 0 or mix_group_bias < 0):
                        indiv_woman_boost *= complaint_bias
#                         a.promotability_perception *= complaint_bias
                        a.numBias += 1
                    a.promotability_perception += indiv_woman_boost

    


def simple_project_promotability(proj,
                                 man_boost,
                                 woman_boost,
                                 stretch_boost,
                                 woman_mixed_group_diff,
                                 complaint_percentage,
                                 complaint_boost_impact):

    if proj.is_stretch:
        man_boost *= stretch_boost
        woman_boost *= stretch_boost

    if proj.is_solo_project:
        if proj.agents[0].is_male:
            proj.agents[0].promotability_perception += man_boost
        else:
            proj.agents[0].promotability_perception += woman_boost
    else:
        n_men = sum([a.is_male for a in proj.agents ])
        n_women = sum([not a.is_male for a in proj.agents])
        if n_men == 0:
            for a in proj.agents:
                a.promotability_perception += woman_boost
        elif n_women == 0:
            for a in proj.agents:
                a.promotability_perception += man_boost
        else:
            for a in proj.agents:
                if a.is_male:
                    a.promotability_perception += man_boost
                else:
                    indiv_woman_boost = woman_boost
                    if complaint_percentage > 0 and draw_binary(p=complaint_percentage):
                        indiv_woman_boost = woman_boost*(complaint_boost_impact)
                    a.promotability_perception += woman_mixed_group_diff*indiv_woman_boost

def assign_projects_factory(P): # each project has equal weight
    if P.project_assignment_method == "equalSoloGroup":
        return assign_projects
    if P.project_assignment_method == "equalSoloGroupPromotability":
        return assign_projects_promotability
    
def assign_projects_promotability(P,company_level,turn,level_index):
    company_level.sort(key = lambda x: x.promotability_perception,reverse = True)
    projects = []
    agent_start_index = 0
    num_stretch_project = 0
    rest = company_level
    if turn % P.project_turns_per_stretch == 0:
        num_stretch_project = int(P.hierarchy_sizes[level_index] * P.stretch_project_percentage)
        if P.stretch_intervention and turn >= P.stretch_intervention_start:
            female_num = int(num_stretch_project * P.stretch_intervention_bar)
            male = [x for x in company_level if x.is_male]
            female = [x for x in company_level if not x.is_male]
            count = 0
            for idx,agent in enumerate(female):
                if count >= female_num:
                    break
                projects.append(Project(agent = agent, is_stretch_project = True,P=P))
                count += 1
            female_num = count
            count = 0
            for idx,agent in enumerate(male):
                if count >= num_stretch_project - female_num:
                    break
                projects.append(Project(agent = agent, is_stretch_project = True,P=P))
                count += 1
            male_num = count
#             print('num:',num_stretch_project)
#             print(male_num,female_num)
            rest = female[female_num:] + male[male_num:]
        elif P.stretch_project_biased_assignment:
            # calulate successful project bar for male
            companyMale = [agent for agent in company_level if agent.is_male] 
            lcompanyMale = len(companyMale)
            topcompanyMale = int(math.ceil(0.2 * lcompanyMale))
            res = 0
            for i in range(topcompanyMale):
                res += companyMale[i].num_successful_projects
            succBar = (res/topcompanyMale) * P.stretch_project_biased_bar if topcompanyMale > 0 else 0
            idx = 0
            jumped = []
            n_male,n_female = 0,0
            while len(projects) < num_stretch_project and idx <= len(company_level) - 1:
                a = company_level[idx]
                if a.is_male:
                    projects.append(Project(agent = a, is_stretch_project = True,P=P))
                    n_male += 1 
                else: # not a.is_male
                    if a.num_successful_projects >= succBar:
                        projects.append(Project(agent = a, is_stretch_project = True,P=P))
                        n_female +=1 
                    else:
                        a.numBias += 1
                        jumped.append(a)
                idx += 1 
            rest = jumped + company_level[idx:]
            
        else:
            for i in range(num_stretch_project):
                projects.append(Project(agent = company_level[i], is_stretch_project = True,P=P))
            rest = company_level[num_stretch_project:]
    shuffle(rest)
    n_agents_to_assign_to = len(rest) #  len(company_level) - num_stretch_project
    solo_project_len = n_agents_to_assign_to // 2 #+ n_agents_to_assign_to % 2
    for i in range(solo_project_len):
        projects.append(Project(agent = rest[i],P=P))
    for i in range(solo_project_len,n_agents_to_assign_to,2):
        projects.append(Project(agent_list = rest[i:i+2],P=P))
    return projects
    

def assign_projects(P, company_level, turn, level_index):
#     if param_holder.project_assignment_method == "equal_solo_group_within_level":
        # Shuffle around the hierarchy
    shuffle(company_level)

    # Assign projects

    agent_start_index = 0
    projects = []

    # Assign stretch project, if its time to do so

    if turn % P.project_turns_per_stretch == 0:
        for index, agent in enumerate(company_level):
            min_proj = (P.project_min_men_stretch_project if agent.is_male else
                        P.project_min_women_stretch_project)
            min_proj += P.project_stretch_min_level_multiplier*level_index
            if agent.num_successful_projects > min_proj:
                projects.append(Project(agent=agent, is_stretch_project=True,P=P))
                # put the agent at the front of the company level
                # and then start assigning projects at index 1
                # to make sure we don't assign 2 projects to this person
                company_level = [agent] + company_level[0:index] + company_level[(index+1):]
                agent_start_index = 1
                break

    n_agents_to_assign_to = len(company_level) - agent_start_index
    # First half are solo projects
    solo_proj_len = n_agents_to_assign_to / 2
    solo_proj_len = solo_proj_len - 1 if not n_agents_to_assign_to % 2 else solo_proj_len
    projects = [Project(agent=company_level[i],P=P) for i in range(agent_start_index,solo_proj_len)]

    # Second half are group projects
    projects += [Project(agent_list=company_level[i:i + 2],P=P)
                 for i in range(solo_proj_len, len(company_level), 2)]

    return projects

