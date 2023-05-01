#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 21:33:42 2023

@author: laura
"""

#!/usr/bin/env python
# coding: utf-8

# # Manyu Luo HW5



import pandas as pd
import numpy as np
import us


# **Import dataset from last homework**



df = pd.read_csv('hw4_data.csv')



df.head()


# **Question 1a: Reshape the data from wide to long, using the wide_to_long function,
# making sure you reset the index to the default values if any of your data is located 
# in the index.  What happened to the POPCHANGE column, and why should it be dropped?**
# 



df_long = pd.wide_to_long(df, stubnames = 'POPESTIMATE', i = 'STATE', j = 'YEAR').reset_index()
df_long = df_long.drop(columns = 'POPCHANGE')



df_long.head()




print(f"The POPCHANGE column should be dropped because in the wide dataframe, \nPOPCHANGE calculates the row difference between POPESTIMATE2022 and \nPOPESTIMATE2020, and it represents the population change across all states. \nHowever, in the long dataset, the difference should be calculated by taking \nthe column difference by every 3 rows. Thus, aside from the rows with YEAR == 2022, \nthe entries for POPCHANGE of the rest of the rows are meaningless. In the original \ndataframe, there are {len(df)} rows and {len(df['POPCHANGE'].unique())} unique POPCHANGE \nvalues, but there are {len(df_long)} rows in the long dataframe, and the number don't match.")


# **Question 1b: Repeat the reshaping using the melt method.  Clean up the result so
# that it is the same as the result from 1a (without the POPCHANGE column).**



df_melt = df.melt(id_vars = 'STATE', value_vars = ['POPESTIMATE2020', 'POPESTIMATE2021', 'POPESTIMATE2022'], 
                  var_name = 'YEAR', value_name = 'POPESTIMATE')
# Cut "POPESTIMATE" in front of each entry and convert to int type
df_melt['YEAR'] = df_melt['YEAR'].str.replace('POPESTIMATE', '')
df_melt['YEAR'] = pd.to_numeric(df_melt['YEAR']) # cite: change YEAR column to int type



df_melt.head()




# make sure that the datasets generated from two methods are the same
assert df_long.equals(df_melt)


# **Question 2: Open the state-visits.xlsx file, and fill in the VISITED column
# with a dummy variable for whether you've visited a state or not.  If you
# haven't been to many states, then filling in a random selection of them
# is fine too.  Save your changes.  Then load the xlsx file as a dataframe in
# Python, and merge the VISITED column into your original wide-form population 
# dataframe, only keeping values that appear in both dataframes.  Are any 
# observations dropped from this?  Show code where you investigate your merge, 
# and display any observations that weren't in both dataframes.**


# load the data
visit = pd.read_excel('state-visits.xlsx')




# generate random indicators
np.random.seed(1301)
visit['VISITED'] = np.random.choice([1, 0], len(visit))




# view data
visit.head()




# merge with same STATE
merged = df.merge(visit, on = 'STATE', how = 'inner')




# show merged
merged.head()


# Extract unmatching rows:



# merge outer with indicators
merged_all = df.merge(visit, on = 'STATE', how = 'outer', indicator = True)




# examine indicators
merged_all['_merge'].unique()


# Show unique rows from left and right dataframe:



# dropped column(s) from state dataframe
left_only = merged_all[merged_all['_merge'] == 'left_only']
left_only



# dropped column(s) from visit dataframe
right_only = merged_all[merged_all['_merge'] == 'right_only']
right_only




# States that get dropped out when merging (in list format)
[left_only['STATE'][51], right_only['STATE'][52]]


# **Question 3a: The file policy_uncertainty.xlsx contains monthly measures of 
# economic policy uncertainty for each state.  The EPU_National column esimates
# uncertainty from national sources, EPU_State from state, and EPU_Composite 
# from both (EPU-N, EPU-S, EPU-C).  Load it as a dataframe, then calculate 
# the mean EPU-C value for each state/year, leaving only columns for state, 
# year, and EPU_Composite, with each row being a unique state-year combination.**



# load the data
policy = pd.read_excel('policy_uncertainty.xlsx')




# show data
policy.head()



# group by state, year and calculate mean
epu_c = pd.DataFrame(policy.groupby(['state', 'year'])['EPU_Composite'].mean().round(2)).reset_index()
epu_c


# **Question 3b) Reshape the EPU data into wide format so that each row is unique 
# by state, and the columns represent the EPU-C values for the years 2022, 
# 2021, and 2020.**



# convert to long shape
policy_wide = epu_c.pivot(index = 'state', columns = 'year', values = 'EPU_Composite').reset_index()




policy_wide.columns.name = None  # cite: remove index name




policy_wide.head()




# select required years
policy_wide = policy_wide[['state', 2020, 2021, 2022]]




policy_wide.head()


# **3c) Finally, merge this data into your merged data from question 2, 
# making sure the merge does what you expect.**


# check length
assert len(policy_wide) == len(merged)




# transform full state name to abbreviation
policy_wide['state'] = policy_wide['state'].map(lambda x : us.states.lookup(x).abbr)




# merge merged and policy_wide, drop redundant column 'state'
final_merge = merged.merge(policy_wide, left_on = 'STATE', right_on = 'state', how = 'inner').drop('state', axis = 1)



final_merge.head()


# **Question 4: Using groupby on the VISITED column in the dataframe resulting from the previous question, answer the following questions and show how you calculated them:** 
# 
# a) what is the single smallest state by 2022 population that you have visited, and not visited?   



min_max = final_merge.groupby('VISITED').min('POPESTIMATE2022')['POPESTIMATE2022']




min_max.tolist()




# smallest state by 2022 population that I have visited (in list and printed)
smallest_visited = final_merge[final_merge['POPESTIMATE2022'] == min_max[0]]['STATE'].tolist()
print(smallest_visited)
print(f"{smallest_visited[0]} is the smallest state I have visited in 2022.")



# smallest state by 2022 population that I have not visited (in list and printed)
smallest_novisited = final_merge[final_merge['POPESTIMATE2022'] == min_max[1]]['STATE'].tolist()
print(smallest_novisited)
print(f"{smallest_novisited[0]} is the smallest state I've not visited in 2022.")


# b) what are the three largest states by 2022 population you have visited, and the three largest states by 2022 
# population you have not visited?


# 3 largest states in 2022 that I've visited (in list and printed)
largest = final_merge.groupby('VISITED').get_group(1).sort_values('POPESTIMATE2022').tail(3)['STATE'].tolist()
print(largest)
largest = ", ".join(largest)
print(f"{largest} are the three largest states in 2022 that I've visited.")




# 3 smallest states in 2022 that I've not visited (in list and printed)
smallest = final_merge.groupby('VISITED').get_group(0).sort_values('POPESTIMATE2022').head(3)['STATE'].tolist()
print(smallest)
smallest = ", ".join(smallest)
print(f"{smallest} are the three smallest states in 2022 that I've not visited.")


# c) do states you have visited or states you have not visited have a higher average EPU-C value in 2022?
# 


# calculate mean scores by VISITED
avg_epuc = final_merge.groupby('VISITED').mean(2022).round(2).reset_index()
avg_epuc




# convert to dictionary showing the mean values
avg_epuc = {'visited_average' : avg_epuc[avg_epuc['VISITED'] == 1][2022][1],
           'no_visited_average' : avg_epuc[avg_epuc['VISITED'] == 0][2022][0]}




print(avg_epuc)
print(list(avg_epuc.values()))




# compare mean score based on different groups of VISITED
assert avg_epuc['visited_average'] > avg_epuc['no_visited_average']




print(f"States I have visited have higher average EPU-C value in 2022 than states I've not visited.")


# **Question 5: Transforming data to have mean zero and unit standard deviation
# is often called "standardization", or a "zscore".  The basic formula to apply to any given value is: (value - mean) / std
# Return to the long-form EPU data you created in step 3a and then, using groupby
# and a function you write, transform the data so that the values for EPU-C
# have mean zero and unit standard deviation for each state.  Add these values
# to a new column named EPU_C_zscore.**



# write a function that takes in a piece of column and calculate the z-scores
def get_zscore(cols):
    avg = cols.mean()
    sd = cols.std()
    cols = (cols - avg) / sd
    return cols




# group by state and calculate z-scores using defined function
epu_c['EPU_C_zscore'] = epu_c.groupby('state')['EPU_Composite'].apply(get_zscore)
epu_c.head()






