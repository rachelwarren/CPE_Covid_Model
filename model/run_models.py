import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import prep_for_model_runs as prep
import build_models as build
import modify_contact as mod
import model_params_class as mp
import calc_summary_stat as summ

"""
Run all of the models of interest

params
------
base_dir: String
    The path for the directory to which results should be saved

params: object of class ModelParams
    the model parameters for this model run

days: Int
    the number of days to run the model for

group_size_data: DataFrame (???)
    the DataFrame that contains the size of each population sub-group

eq_group_size_data: DataFrame
    the DataFrame where some population sub-groups are equal (???)

contact_data_pre_SIP: k*k contact matrix for pre-SIP order

contact_data_post_SIP: k*k contact matrix for post-SIP order

prison_peak_date: Int
    the date on which the prison infection rate will peak

returns
-------
summary_stats_original: a DataFrame of summary statistics

infection_rates: a DataFrame of all the infection rates for each version of the
model 

pop_size_df: the population sizes used for inputs to each of the models 
"""

def run_models(base_dir, params, days,
               group_size_data,
               eq_group_size_data,
               contact_data_pre_SIP,
               contact_data_post_SIP,
               prison_peak_date):
    output_name = params.get_name()
    output_path =os.path.join(base_dir, output_name)
     
    #get sizes and initial values     
    group_size_data = prep.process_group_size(group_size_data, params.initial_infection_multiplier)        
    pop_size = prep.combine_groups(group_size_data)
   
    #equal forced labour  
    eq_group_size_data = prep.process_group_size(eq_group_size_data, params.initial_infection_multiplier) 
    
    #conctact_matrix_list 
    cm_pre = []
    cm_post = []
  

    pre_lockdown, post_lockdown, group_size_ls = mod.create_matrix(contact_data_pre_SIP,
                                                               contact_data_post_SIP,
                                                               group_size_data,
                                                               eq_group_size_data)
        
    infection_rates = []
    pop_sizes = {}
    
    #run the original model
    S_df, I_df, _ = build.build_model(group_size_data, days,
                                params.sip_start_date,
                                contact_data_pre_SIP.values,
                                contact_data_post_SIP.values,
                                params.transmission_rate,
                                params.prison_infection_rate, 
                                prison_peak_date)
    pop_sizes['original'] = pop_size
    
    cm_pre.append(prep.add_contact_matrix(contact_data_pre_SIP, output_name, 'original'))
    cm_post.append(prep.add_contact_matrix(contact_data_post_SIP, output_name, 'original'))            
                    
    summary_stats_original = summ.calculate_peak_infections(S_df, I_df, pop_size, "original", output_path)
    peak_days_original = summary_stats_original.loc['Total_w_Police', 'days_peak']
    I_df['model_name'] = 'original'
    I_df['name'] = output_name
    infection_rates.append(I_df)
    
    for model_name in pre_lockdown.keys():
        
        pre_contact = pre_lockdown[model_name]
        post_contact = post_lockdown[model_name]
        size_df = group_size_ls[model_name]
                   
        cm_pre.append(prep.add_contact_matrix(contact_data_pre_SIP, output_name, model_name))
        cm_post.append(prep.add_contact_matrix(contact_data_post_SIP, output_name, model_name))  
        
        S_df2, I_df2, _ = build.build_model(size_df, days,
                                      params.sip_start_date,
                                      pre_contact.values,
                                      post_contact.values,
                                      params.transmission_rate,
                                      params.prison_infection_rate,
                                      prison_peak_date)
        pop_size = prep.combine_groups(size_df)
        summary_stats = summ.calculate_peak_infections(S_df2, I_df2, pop_size, model_name,
                                                  output_path, peak_days_original)
        I_df2['model_name'] = model_name
        I_df2['name'] = output_name
        infection_rates.append(I_df2)
        pop_sizes[model_name] = pop_size
        summary_stats_original = summary_stats_original.append(summary_stats)
        
    #Turn map of population sizes into data frame 
    pop_series = [values.rename(k) for k, values in pop_sizes.items()]
    pop_size_df = pd.concat(pop_series, axis = 1).transpose()
    pop_size_df['name'] = output_name
    summary_stats_original['model_tag'] = output_name
        
    return summary_stats_original, pd.concat(infection_rates), pop_size_df