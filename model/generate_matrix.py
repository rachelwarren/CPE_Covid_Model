import pandas as pd
import numpy as np


# expanded matrix
import os

BASE_PATH = '../input2/'
if not os.path.exists(BASE_PATH):
    os.mkdir(BASE_PATH)
CONTACT_MATRIX_PRE_SIP = f'{BASE_PATH}/CONTACT_MATRIX_PRE_SIP.csv'
GROUP_SIZE_MATRIX = f'{BASE_PATH}/GROUP_SIZE_MATRIX.csv'
CONTACT_MATRIX_POST_SIP = f'{BASE_PATH}/CONTACT_MATRIX_POST_SIP.csv'
CONTACT_MATRIX_PRE_SIP_EXPANDED = f'{BASE_PATH}/contact_matrix_expanded_pre_sip.csv'
CONTACT_MATRIX_POST_SIP_EXPANDED = f'{BASE_PATH}/contact_matrix_expanded_post_sip.csv'
ls = []
for race in ['White', 'Black']:
    for labour_type in ['Forced_Labour', 'Non_Essential_Labour', 'Police']:
        for loc in ['At_Work', 'At_Home']:
            simple_name = f'{race}_{labour_type}' if labour_type != 'Non_Essential_Labour' else race

            ls.append(
                {'Race': race,
                 'Labour_Type': labour_type,
                 'Location': loc,
                 'i': f'{race}_{labour_type}_{loc}',
                 'Sub_Group_Name': f'{race}_{labour_type}',
                 'Group_Name': simple_name})

    ls.append({'Race': race, 'Labour_Type': 'Non_Working', 'Location': 'At_Home',
               'Sub_Group_Name': f'{race}_Non_Working', 'i': f'{race}_Non_Working', 'Group_Name': race})
    ls.append({'Race': race, 'Labour_Type': 'Prison',
               'Sub_Group_Name': f'{race}_Prison', 'i': f'{race}_Prison', 'Group_Name': f'{race}_Prison'})

group_df = pd.DataFrame(ls)
group_df = group_df.set_index('i')

# Share of Population
group_sizes = {}  # dictionary with size of the final population groups that we use keyed on sub group name
prop_of_race = {}  # dictionary with proportion of that racial group in this group
WHITE_OF_ALL = .6040  # Group Size B35
BLACK_OF_ALL = 0.1340

ALL_AMERICANS = 328239523.00
WHITE_INCARCERATED_TOTAL = 804712.10  # Calculations B31
BLACK_INCARCERATED_TOTAL = 717931.20

white_total = WHITE_OF_ALL * ALL_AMERICANS
black_total = BLACK_OF_ALL * ALL_AMERICANS

# ?????
WHITE_OF_POLICE = 0.597  # proportion of police who are white
BLACK_OF_POLICE = 0.215  # proportion of police who are black

POLICE_OF_WHITE = 0.00167846  # B43 #proporiton of white who are police
POLICE_OF_BLACK = 0.00272  # This seems real wierd ...

prop_of_race['White_Police'] = POLICE_OF_WHITE
prop_of_race['Black_Police'] = POLICE_OF_BLACK

group_sizes['White_Police'] = POLICE_OF_WHITE * WHITE_OF_ALL
group_sizes['Black_Police'] = POLICE_OF_BLACK * BLACK_OF_ALL

# INCARCERATION
# These are pull from the calculations spread sheet I don't know if they are write and
# I have not used the full calculations

INCARCE_OF_ALL = 0.0063  # Group Size Calculations B32
WHITE_OF_INCARCE = 0.5284967924  # Calculations J31 #proportion of prisoners who are white
BLACK_OF_INCARCE = 0.4715032076  # Calculations J32

group_sizes[
    'White_Prison'] = INCARCE_OF_ALL * WHITE_OF_INCARCE  # Proportion of all people who white AND incarcerated Calculations D32
group_sizes[
    'Black_Prison'] = INCARCE_OF_ALL * BLACK_OF_INCARCE  # Proportion of all black people who are incarcerated Calculations D33

prop_of_race['White_Prison'] = WHITE_INCARCERATED_TOTAL / white_total
prop_of_race['Black_Prison'] = BLACK_INCARCERATED_TOTAL / black_total

# Labour Groups
FORCED_LABOUR_OF_WHITE = 0.1125  # proprotion of all white residents
FORCED_LABOUR_OF_BLACK = 0.1362  # Proportion of all black residents

NON_ESSENTIAL_LABOUR_OF_WHITE = 0.3749  # B23
NON_ESSENTIAL_LABOUR_OF_BLACK = 0.30438  # B22 prop of black residents doing non essential labour

prop_of_race['White_Forced_Labour'] = FORCED_LABOUR_OF_WHITE
prop_of_race['Black_Forced_Labour'] = FORCED_LABOUR_OF_BLACK

prop_of_race['White_Non_Essential_Labour'] = NON_ESSENTIAL_LABOUR_OF_WHITE
prop_of_race['Black_Non_Essential_Labour'] = NON_ESSENTIAL_LABOUR_OF_BLACK

prop_of_race['White_Non_Working'] = 1 - prop_of_race['White_Prison'] - prop_of_race['White_Non_Essential_Labour'] - \
                                    prop_of_race['White_Forced_Labour']

prop_of_race['Black_Non_Working'] = 1 - prop_of_race['Black_Prison'] - prop_of_race['Black_Non_Essential_Labour'] - \
                                    prop_of_race['Black_Forced_Labour']

group_df['Proportion_of_Racial_Group'] = group_df['Sub_Group_Name'].replace(prop_of_race)


def group_size_fn(g):
    if g in group_sizes.keys():
        return group_sizes[g]
    else:
        if 'Black' in g:
            return prop_of_race[g] * BLACK_OF_ALL
        elif 'White' in g:
            return prop_of_race[g] * WHITE_OF_ALL
        else:
            return np.nan


group_df['Group_Size'] = group_df['Sub_Group_Name'].apply(group_size_fn)

group_df[['Sub_Group_Name', 'Proportion_of_Racial_Group', 'Group_Size']].drop_duplicates()

# %%
WEEKLY_WAKING_HOURS = 112
# Fill in Hours in Neighborhood
# Calculation comves from Expanded may 7 pre social distanced model row 19
group_df['Home_Hours'] = np.where(
    (group_df['Labour_Type'] == 'Non_Working'), WEEKLY_WAKING_HOURS,
    np.where((group_df['Labour_Type'] != 'Non_Working') &
             (group_df['Location'] == 'At_Home'), 72, 0))

group_df['Working_Hours'] = np.where(group_df['Location'] == 'At_Work', 40, 0)
group_df[['Home_Hours', 'Working_Hours']]

# %%

group_df['Race_Home_Hours'] = group_df['Home_Hours'] * group_df['Proportion_of_Racial_Group']
group_df['Race_Work_Hours'] = group_df['Working_Hours'] * group_df['Proportion_of_Racial_Group']

# %%

group_df[['Home_Hours', 'Proportion_of_Racial_Group', 'Race_Work_Hours', 'Race_Home_Hours']]

# %%

white_residential_hours = group_df[(group_df['Location'] == 'At_Home') & (group_df['Race'] == 'White')][
    'Race_Home_Hours'].sum()
black_residential_hours = group_df[(group_df['Location'] == 'At_Home') & (group_df['Race'] == 'Black')][
    'Race_Home_Hours'].sum()
print(f"resident hours --- white: {white_residential_hours}, black: {black_residential_hours}")

print(f"saving group size matrix to {GROUP_SIZE_MATRIX}")
group_df_to_save = group_df.groupby('Group_Name').agg(Population_Proportion = ('Group_Size', 'sum'))
group_df_to_save.to_csv(GROUP_SIZE_MATRIX)
#++++++++++++++++++++++++++++++++++++++++++++
# Contact Matrices
#++++++++++++++++++++++++++++++++++++++++++++
# Create a new data frame for the contact matrix.
contact_matrix_pre_sip = group_df[[]]
for g in group_df.index.values:
    contact_matrix_pre_sip[g] = 0.0

SOCIAL_DISTANCING_INFECTION_RATE = 1.2
NO_SOCIAL_DISTANCING_INFECTION_RATE = 2.7
TRANSMISSION_RATE = 0.01
DAYS_UNTIL_RECOVERY = 21

social_distancing_contact_rate = SOCIAL_DISTANCING_INFECTION_RATE / (TRANSMISSION_RATE * DAYS_UNTIL_RECOVERY)
no_social_distancing_contact_rate = NO_SOCIAL_DISTANCING_INFECTION_RATE / (TRANSMISSION_RATE * DAYS_UNTIL_RECOVERY)
occupation_infection_number = no_social_distancing_contact_rate
print(social_distancing_contact_rate)
print(no_social_distancing_contact_rate)
print(occupation_infection_number)
# number of people this group contacts when at work
# this will change in the post social distancing world.
group_df['labour_type_contact_rate'] = group_df['Labour_Type'].apply(
    lambda x: occupation_infection_number * (WEEKLY_WAKING_HOURS / 40) if x in ['Prison', 'Police', 'Forced_Labour'] else (
        no_social_distancing_contact_rate))

# at home contact rates are no social distancing for now, but should be with social distancing in the future.
group_df['Target_Contacts'] = (group_df['Home_Hours'] / WEEKLY_WAKING_HOURS) * no_social_distancing_contact_rate + group_df[
    'labour_type_contact_rate'] * group_df['Working_Hours'] / WEEKLY_WAKING_HOURS
group_df[['labour_type_contact_rate', 'Home_Hours', 'Target_Contacts']]

def fill_in_working_groups(m, my_df, is_post):
    # for all workers, they contact only other workers at work.
    # Proportional to types of workers, to hit the total contacts.
    # no one contacts police at work
    if not is_post:
        worker_df = my_df[(my_df['Location'] == 'At_Work') & my_df['Labour_Type'].isin(
            ['Forced_Labour', 'Non_Essential_Labour'])]
    else:
        worker_df = group_df_sip[
            (my_df['Location'] == 'At_Work') & my_df['Labour_Type'].isin(['Forced_Labour'])]
    total_worker_size = worker_df['Group_Size'].sum()
    worker_proportion = (worker_df['Group_Size'] / total_worker_size)
    for a in worker_df.index.values:
        target_contacts = worker_df.loc[a, 'Target_Contacts']
        for b in worker_df.index.values:
            # if b is white non essential labour at work
            # then worker proportion is non essential labour / all working groups
            m.loc[a, b] = target_contacts * worker_proportion[b]
    return m


contact_matrix_pre_sip = fill_in_working_groups(contact_matrix_pre_sip, group_df, is_post=False)

white_of_black_white_police = WHITE_OF_POLICE / (WHITE_OF_POLICE + BLACK_OF_POLICE)
black_of_black_white_police = BLACK_OF_POLICE / (WHITE_OF_POLICE + BLACK_OF_POLICE)
print(f'white of black white police {white_of_black_white_police} black: {black_of_black_white_police}')
POLICE_STOP_WHITE = 0.6895951865  # D16
POLICE_STOP_BLACK = 0.2751037807
TOTAL_OFFICER_STOPS = 10

police_contacts_with_whites = TOTAL_OFFICER_STOPS * POLICE_STOP_WHITE
print(f'white --> police {police_contacts_with_whites}')
police_contacts_with_blacks = TOTAL_OFFICER_STOPS * POLICE_STOP_BLACK
# police contact in white neighborhoods
# police --> white
white_police_contacts_with_whites = police_contacts_with_whites * white_of_black_white_police
black_police_contacts_with_whites = police_contacts_with_whites * black_of_black_white_police
# white --> police
# whites_contact_with_white_police = white_police_contacts_with_whites * group_df.loc[
#     'White_Police_At_Work', 'Group_Size'] / WHITE_OF_ALL
# whites_contact_with_black_police = black_police_contacts_with_whites * group_df.loc[
#     'Black_Police_At_Work', 'Group_Size'] / WHITE_OF_ALL
whites_contact_with_white_police = 0.01437116675
whites_contact_with_black_police = 0.005175545815
print(f' white --> police_contact {whites_contact_with_white_police} + {whites_contact_with_black_police} = {whites_contact_with_white_police + whites_contact_with_black_police}')
# police contacts in black neighborhoods
# police --> black
white_police_contacts_with_blacks = police_contacts_with_blacks * white_of_black_white_police
black_police_contacts_with_blacks = police_contacts_with_blacks * black_of_black_white_police
# black --> police
blacks_contact_with_white_police = 0.02584202286
blacks_contact_with_black_police = 0.009306591148
# blacks_contact_with_black_police = black_police_contacts_with_blacks * group_df.loc[
#     'Black_Police_At_Work', 'Group_Size'] / BLACK_OF_ALL
# blacks_contact_with_white_police = white_police_contacts_with_blacks * group_df.loc[
#     'White_Police_At_Work', 'Group_Size'] / BLACK_OF_ALL

# Might want to make the next few lines a function since it's needed for both pre and post SIP
def calc_race_neighborhood(my_group_df):
    home = my_group_df[(my_group_df['Location'] == 'At_Home')]
    white_at_home = home[home['Race'] == 'White']
    white_at_home['hours_prop'] = white_at_home['Race_Home_Hours'] / white_at_home['Race_Home_Hours'].sum()
    black_at_home = home[home['Race'] == 'Black']
    black_at_home['hours_prop'] = black_at_home['Race_Home_Hours'] / black_at_home['Race_Home_Hours'].sum()
    return white_at_home, black_at_home

MAX_OCCUPATION_INFECTION_NUMBER = 17
MIN_OCCUPATION_INFECTION_NUMBER = 10
print(group_df.loc['Black_Police_At_Home', 'Home_Hours'])


def fill_in_police_job_contacts(m, g_df):
    w_neighborhood, b_neighborhood = calc_race_neighborhood(group_df)

    # police contacts are spread evenly by "race_home_hours" for a given neighborhood
    # police at home also contact police at work, so adding police into this.
    for person in g_df.index.values:
        time = g_df.loc[person, 'Home_Hours'] / WEEKLY_WAKING_HOURS
        if person in w_neighborhood.index.values:
            prop = w_neighborhood.loc[person, 'hours_prop']
            m.loc['White_Police_At_Work', person] = white_police_contacts_with_whites * prop
            m.loc['Black_Police_At_Work', person] = black_police_contacts_with_whites * prop
            # HELP!!! These numbers seem not to match up with what the google sheet has
            m.loc[person, 'White_Police_At_Work'] = whites_contact_with_white_police * time
            m.loc[person, 'Black_Police_At_Work'] = whites_contact_with_black_police * time

        if person in b_neighborhood.index.values:
            prop = b_neighborhood.loc[person, 'hours_prop']
            m.loc['White_Police_At_Work', person] = white_police_contacts_with_blacks * prop
            m.loc['Black_Police_At_Work', person] = black_police_contacts_with_blacks * prop
            # HELP!!! These numbers seem not to match up with what the google sheet has
            m.loc[person, 'White_Police_At_Work'] = blacks_contact_with_white_police * time
            m.loc[person, 'Black_Police_At_Work'] = blacks_contact_with_black_police * time

    m.loc['White_Police_At_Work', 'White_Police_At_Work'] = \
        (MAX_OCCUPATION_INFECTION_NUMBER - white_police_contacts_with_whites - white_police_contacts_with_blacks) * white_of_black_white_police  # E37-B41-B44 * B28
    m.loc['White_Police_At_Work', 'Black_Police_At_Work'] = \
        (MAX_OCCUPATION_INFECTION_NUMBER - white_police_contacts_with_whites - white_police_contacts_with_blacks) * black_of_black_white_police

    m.loc['Black_Police_At_Work', 'White_Police_At_Work'] = \
        (MAX_OCCUPATION_INFECTION_NUMBER - black_police_contacts_with_whites - black_police_contacts_with_blacks) * white_of_black_white_police
    m.loc['Black_Police_At_Work', 'Black_Police_At_Work'] = \
        (MAX_OCCUPATION_INFECTION_NUMBER - black_police_contacts_with_whites - black_police_contacts_with_blacks) * black_of_black_white_police

    return m

contact_matrix_pre_sip = fill_in_police_job_contacts(contact_matrix_pre_sip, group_df)

# Target for totals is the proportion of hours at work or at home * the expected number of contacts per day (?week?)

# All hard coded from EXPANDED_CONTACT_MATRIX_PRE_SIP B78,
# at some point we should put the calculations to get here in the spreadsheet
WHITE_RELEASE_RATE = 0.00007130892426
BLACK_RELEASE_RATE = 0.0002163545656

def fill_in_prison_contacts(m, my_group_df, is_post=False):
    # These are in the spread sheet but don't know where they are used
    # white_weekly_release_rate = WHITE_RELEASE_RATE * 7
    # black_weekly_release_rate = BLACK_RELEASE_RATE * 7
    white_release_rate_delay = WHITE_RELEASE_RATE * DAYS_UNTIL_RECOVERY * 0.5  # don't understand the 0.5 this is B77
    black_release_rate_delay = BLACK_RELEASE_RATE * DAYS_UNTIL_RECOVERY * 0.5
    if not is_post:
        white_prison = white_release_rate_delay * no_social_distancing_contact_rate

        black_prison = black_release_rate_delay * no_social_distancing_contact_rate
    else:
        white_prison = white_release_rate_delay * social_distancing_contact_rate
        black_prison = black_release_rate_delay * social_distancing_contact_rate

    for i in my_group_df.index.values:
        if my_group_df.loc[i, 'Location'] == 'At_Home':
            if my_group_df.loc[i, 'Race'] == 'Black':
                m.loc[i, 'Black_Prison'] = black_prison * (my_group_df.loc[i, 'Home_Hours']/WEEKLY_WAKING_HOURS)
            else:
                m.loc[i, 'White_Prison'] = white_prison * (my_group_df.loc[i, 'Home_Hours']/WEEKLY_WAKING_HOURS)

    # black_police_work --> black_prison
    # See Row L .. i don't understand this logic.
    m.loc['White_Police_At_Work', 'White_Prison'] = white_release_rate_delay * white_police_contacts_with_whites
    m.loc['White_Police_At_Work', 'Black_Prison'] = black_release_rate_delay * white_police_contacts_with_blacks

    m.loc['Black_Police_At_Work', 'Black_Prison'] = black_release_rate_delay * black_police_contacts_with_blacks
    m.loc['Black_Police_At_Work', 'White_Prison'] = white_release_rate_delay * black_police_contacts_with_whites
    return m

contact_matrix_pre_sip = fill_in_prison_contacts(contact_matrix_pre_sip, group_df)

def fill_in_home_contacts(m, g_df):

    white_neighborhood, black_neighborhood = calc_race_neighborhood(g_df)
    for a in g_df.index.values:
        if g_df.loc[a, 'Location'] == 'At_Home':
            # Its not what we did in the spread sheet but maybe we should be subtracting these from target contacts
            other_contacts = m.loc[a][['Black_Police_At_Work',
              'Black_Prison', 'White_Police_At_Work', 'White_Prison']].sum()

            target_contacts = g_df.loc[a, 'Target_Contacts']
            if g_df.loc[a, 'Race'] == 'Black':
                for b in black_neighborhood.index.values:
                    m.loc[a, b] = black_neighborhood.loc[b, 'hours_prop'] * target_contacts
            else:
                for w in white_neighborhood.index.values:
                    m.loc[a, w] = white_neighborhood.loc[w, 'hours_prop'] * target_contacts
    return m

contact_matrix_pre_sip = fill_in_home_contacts(contact_matrix_pre_sip, group_df)

def collapse_racial_groups(m):

    m = m.rename(index={'White_Non_Working': 'White',
                        'Black_Non_Working': 'Black'})
    m['White'] = m['White_Non_Working'] + m['White_Non_Essential_Labour_At_Home']
    m['Black'] = m['Black_Non_Working'] + m['Black_Non_Essential_Labour_At_Home']
    m = m.drop(['White_Non_Essential_Labour_At_Home', 'White_Non_Essential_Labour_At_Work',
                'Black_Non_Essential_Labour_At_Home', 'Black_Non_Essential_Labour_At_Work'])
    m = m.drop(['White_Non_Working', 'White_Non_Essential_Labour_At_Home', 'White_Non_Essential_Labour_At_Work',
                'Black_Non_Working', 'Black_Non_Essential_Labour_At_Home', 'Black_Non_Essential_Labour_At_Work'],
               axis=1)
    return m

def create_final_matrix(m):
    new = m.copy()

    new['White_Non_Essential_Labour_At_Home'] = m['White_Non_Working'] + m['White_Non_Essential_Labour_At_Home']
    new['Black_Non_Essential_Labour_At_Home'] = m['Black_Non_Working'] + m['Black_Non_Essential_Labour_At_Home']

    new = new.drop(['White_Non_Working', 'Black_Non_Working'])
    new = new.drop(['White_Non_Working', 'Black_Non_Working'], axis=1)
    name_dict = group_df[group_df['Labour_Type'] != 'Non_Working']['Group_Name'].to_dict()
    new = new.rename(index=name_dict).reset_index()
    new = new.groupby('i').sum()

    for v in name_dict.values():
        columns = filter(lambda k: name_dict[k] == v, name_dict.keys())
        new[v] = new[columns].sum(axis=1)  # row sum
    group_names = list(set(group_df['Group_Name'].values))
    return new[group_names]

contact_matrix_pre_sip.to_csv(CONTACT_MATRIX_PRE_SIP_EXPANDED)
actual = pd.read_csv('/Users/rachelwarren/projects/CPE_Covid_Model/input2/actual_pre_contact_expanded.csv',
                     sep='\t', lineterminator='\n', index_col='Groups')

contact_matrix_pre_sip_final = create_final_matrix(contact_matrix_pre_sip)

# ++++++++++++++++++++++
# identify where code diverges from spread sheet
# +++++++++++++++++++++
# print("Verifying Pre SIP Matrix ++++++++++++++++++++++++++++++++++++++++++")
# for index, row in actual.iterrows():
#     print(f'checking row {index}')
#     for col in actual.columns:
#         x = row[col]
#         y = contact_matrix_pre_sip.loc[index, col]
#         if np.round(x, 2) != np.round(y, 2):
#             print(f'     {index}, {col}: {x} != {y}')
# contact_matrix_pre_sip_final.to_csv(CONTACT_MATRIX_PRE_SIP)

### BEGIN POST SIP CONTACT MATRIX CREATION
group_df_sip = group_df[
    ['Race', 'Labour_Type', 'Location', 'Sub_Group_Name', 'Group_Name', 'Proportion_of_Racial_Group', 'Group_Size']]
# Now non-essential labor and non-working for both races is collapsed into "white"
# Need to calculate new home_hours, work_hours and TargetContacts
group_df_sip['Home_Hours'] = np.where(
    group_df_sip['Location'] == 'At_Work', 0, np.where(
        (group_df_sip['Labour_Type'] == 'Forced_Labour') & (group_df_sip['Location'] == 'At_Home'), 72, np.where(
            (group_df_sip['Labour_Type'] == 'Police') & (group_df_sip['Location'] == 'At_Home'), 72, 112)))

group_df_sip['Working_Hours'] = np.where(
    (group_df_sip['Labour_Type'] == 'Forced_Labour') & (group_df_sip['Location'] == 'At_Work'),
    40, np.where(
        (group_df_sip['Labour_Type'] == 'Police') & (group_df_sip['Location'] == 'At_Work'), 40, 0))
group_df_sip['labour_type_contact_rate'] = group_df_sip['Labour_Type'].apply(
    lambda x: occupation_infection_number * (WEEKLY_WAKING_HOURS / 40) if x in ['Prison', 'Police', 'Forced_Labour'] else (
        social_distancing_contact_rate))

group_df_sip['Target_Contacts'] = (group_df_sip['Home_Hours'] / WEEKLY_WAKING_HOURS) * social_distancing_contact_rate + group_df_sip[
    'labour_type_contact_rate'] * group_df_sip['Working_Hours'] / WEEKLY_WAKING_HOURS
#print(group_df_sip[['Home_Hours', 'Working_Hours', 'labour_type_contact_rate', 'Target_Contacts']])

group_df_sip['Race_Home_Hours'] = group_df_sip['Home_Hours'] * group_df_sip['Proportion_of_Racial_Group']
group_df_sip['Race_Work_Hours'] = group_df_sip['Working_Hours'] * group_df_sip['Proportion_of_Racial_Group']

#print(group_df_sip[['Home_Hours', 'Working_Hours', 'labour_type_contact_rate', 'Target_Contacts']])

# Create post-SIP contact matrix
contact_matrix_sip = group_df_sip[[]]
for g in group_df_sip.index.values:
    contact_matrix_sip[g] = 0.0

# Fill in working groups: made modification to function above
contact_matrix_sip = fill_in_working_groups(contact_matrix_sip, group_df_sip, is_post=True)

# Fill in police job contacts
contact_matrix_sip = fill_in_police_job_contacts(contact_matrix_sip, group_df_sip)

# Fill in prison contacts
contact_matrix_sip = fill_in_prison_contacts(contact_matrix_sip, group_df_sip, is_post=True)

# Fill in home contacts
contact_matrix_sip = fill_in_home_contacts(contact_matrix_sip, group_df_sip)

#Collapse non-working and non-essential; need to sum these columns for each race, but not the rows
contact_matrix_sip_final = create_final_matrix(contact_matrix_sip)
#print(group_df_sip)
contact_matrix_sip_final.to_csv(CONTACT_MATRIX_POST_SIP)


contact_matrix_sip = contact_matrix_sip.rename(index={'White_Non_Working': 'White',
                                                      'Black_Non_Working': 'Black'})
contact_matrix_sip['White'] = contact_matrix_sip['White_Non_Working'] + contact_matrix_sip[
    'White_Non_Essential_Labour_At_Home']
contact_matrix_sip['Black'] = contact_matrix_sip['Black_Non_Working'] + contact_matrix_sip[
    'Black_Non_Essential_Labour_At_Home']
contact_matrix_sip = contact_matrix_sip.drop(
    ['White_Non_Essential_Labour_At_Home', 'White_Non_Essential_Labour_At_Work',
     'Black_Non_Essential_Labour_At_Home', 'Black_Non_Essential_Labour_At_Work'])
contact_matrix_sip = contact_matrix_sip.drop(
    ['White_Non_Working', 'White_Non_Essential_Labour_At_Home', 'White_Non_Essential_Labour_At_Work',
     'Black_Non_Working', 'Black_Non_Essential_Labour_At_Home', 'Black_Non_Essential_Labour_At_Work'],
    axis=1)

actual_sip = pd.read_csv('/Users/rachelwarren/projects/CPE_Covid_Model/input2/actual_post_contact_expanded.csv',
                     sep='\t', lineterminator='\n', index_col='Groups')

# ++++++++++++++++++++++
# identify where code diverges from spread sheet
# +++++++++++++++++++++
# print("Verifying Post SIP Matrix")
# for index, row in actual_sip.iterrows():
#     print(f'checking row {index}')
#     for col in actual_sip.columns:
#         x = row[col]
#         y = contact_matrix_sip.loc[index, col]
#         if np.round(x, 2) != np.round(y, 2):
#             print(f'     {index}, {col}: {x} != {y}')

#### POLICY INTERVENTIONS ####
## Policy lever 1: reduce police patrol of misdemeanors ##
# TODO: Reduce police contacts w/ non-police by factor when lockdown begins and reduce
# jail releases by a factor(change group size matrix)
POLICE_CONTACT_SHRINK = 0.5
POLICE_CONTACTS_TO_SHRINK = ['White_Forced_Labour_At_Work', 'White_Forced_Labour_At_Home',
                             'White', 'White_Prison', 'Black_Forced_Labour_At_Work',
                             'Black_Forced_Labour_At_Home', 'Black', 'Black_Prison']
JAIL_OF_CORRECTIONS = 0.5 # fraction of jail/prison releases that are jail releases
JAIL_RELEASE_SHRINK = 0.4

contact_matrix_p1 = contact_matrix_sip
contact_matrix_p1.loc[['White_Police_At_Work', 'Black_Police_At_Work'], 
                          POLICE_CONTACTS_TO_SHRINK] = contact_matrix_p1.loc[[
        'White_Police_At_Work', 'Black_Police_At_Work'], POLICE_CONTACTS_TO_SHRINK]*POLICE_CONTACT_SHRINK

group_df_p1 = group_df
group_df_p1.loc[['White_Prison', 'Black_Prison'], 
                'Group_Size'] = group_df_p1.loc[['White_Prison', 'Black_Prison'],
                                               'Group_Size']*(1-(JAIL_OF_CORRECTIONS*JAIL_RELEASE_SHRINK))
# In Model Runs, will want to use contact_matrix_p1 as post-SIP matrix. After
# 14 days (after lockdown?), will want to use group_df_p1

## Policy lever 2: Alter prison release strategy ##
# TODO: Change number of people who are released each day who are COVID-positive
COVID_POSITIVE_OF_CORRECTIONS = 0 # in the future, we can make this a fraction

contact_matrix_p2 = contact_matrix_sip
contact_matrix_p2[['White_Prison', 'Black_Prison']] = contact_matrix_p2[['White_Prison',
                 'Black_Prison']]*COVID_POSITIVE_OF_CORRECTIONS
# In Model Runs, will want to use contact_matrix_p2 as post-SIP matrix; will
# eventually want to consider ramping up/down (however you want to view it) to
# this fraction of positive cases


