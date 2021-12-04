#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 22:50:48 2021

@author: julie-schnurr
"""

import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from pySankey.sankey import sankey

def excel_results(df_results, outfile_name):
    # input a python data frame and get an excel file
    with pd.ExcelWriter(str(outfile_name) +'.xlsx', engine='xlsxwriter') as writer:  
       
        # Sheets for results and summary
        df_results.to_excel(writer, sheet_name='Results', index=False)

        # Get the xlsxwriter worksheet objects.
        worksheet = writer.sheets['Results']
        
        # Get the dimensions of the dataframes
        (max_row, max_col) = df_results.shape
        
        # Create a list of column headers, to use in add_table()
        column_settings = []
        for header in df_results.columns:
            column_settings.append({'header': header})
        
        # Add the tables
        worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
        
        # Make the columns wider for readability
        worksheet.set_column(0, max_col - 1, 20)

def match_basic(name, list_names, min_score=0):
    # Basic Levenshtein Distance minimization algorithm
    max_score = -1
    max_name = ''
    for x in list_names:
        score = fuzz.ratio(name, x)
        if (score > min_score) & (score > max_score):
            max_name = x
            max_score = score
    return (max_name, max_score)

def match_token(name, list_names, min_score=0):
    # Tokenized Levenshtein Distance minimization algorithm
    max_score = -1
    max_name = ''
    for x in list_names:
        score = fuzz.token_sort_ratio(name, x)
        if (score > min_score) & (score > max_score):
            max_name = x
            max_score = score
    return (max_name, max_score)

def match_checker(input_list, matchto_list, similarity_score):
    # Checks two lists for matches using Levenshtein Distance
    matched_array = []
    guess_array=[]
    ratio_array=[] 
    
    # first checking for an exact match
    for value in input_list:
        if value in matchto_list:
            matched_array.append(value)
            guess_array.append(value)
            ratio_array.append('100')
        else:   
            # deciding if we want to use the tokenized version of the matcher
            numbers = sum(c.isdigit() for c in value)
            letters = sum(c.isalpha() for c in value)
            spaces  = sum(c.isspace() for c in value)
            others  = len(value) - numbers - letters - spaces
            
            if numbers>(letters+spaces+others):
                max_name, max_score = match_basic(value, matchto_list)
            else:
                max_name, max_score = match_token(value, matchto_list)
            
            matched_array.append(value)
            guess_array.append(max_name)
            ratio_array.append(max_score)
            
    data = {'Original': matched_array, 'Best Match': guess_array, 
            'Match Score': ratio_array}  
    df = pd.DataFrame(data)
    df['Match Score'] = df['Match Score'].astype(int) # make score an integer for inequalities
    
    df_results = df
    df_goodmatch =  df_results[df_results['Match Score'] >= similarity_score]
    df_badmatch =  df_results[df_results['Match Score'] < similarity_score]
    
    return df_results, df_goodmatch, df_badmatch

def duplicate_remover(input_list, similarity_score):
    
    # Gets rid of fuzzy fuplicates using Levenshtein Distance (85 similarity
    # score is a good place to start)
            
    # Initilizing lists for Sankey plot
    true_list = []
    predicted_list = []
    input_list_1 = input_list.copy()
    
    for idx, value in enumerate(input_list):
        
        # removing the instance we are checking for from the list
        
        input_list_2 = input_list_1.copy()
        input_list_2.remove(value)
        true_list.append(value)
        
        # first checking for an exact match
        if value in input_list_2:
            max_name = value
            max_score = 100
            predicted_list.append(value)
            
        else:   
            # deciding if we want to use the tokenized version of the matcher
            numbers = sum(c.isdigit() for c in value)
            letters = sum(c.isalpha() for c in value)
            spaces  = sum(c.isspace() for c in value)
            others  = len(value) - numbers - letters - spaces

            if numbers>(letters+spaces+others):
                max_name, max_score = match_basic(value, input_list_2)
            else:
                max_name, max_score = match_token(value, input_list_2)
 
            if max_score >= similarity_score:
                predicted_list.append(max_name)
                input_list_1[idx] = max_name
                
            else: 
                predicted_list.append(value)

    sankey(true_list, predicted_list) 
    unique_list = true_list, predicted_list, np.unique(input_list_1)
    
    return unique_list

if __name__ == '__main__':

    # load data from ecel to a pandas datafram
    df_brand = pd.read_excel("Products.xlsx", header=0, usecols="A:C", nrows=1581)
    df_black_list = pd.read_excel("Products.xlsx", header=0, usecols="F", nrows=50)
    
    # conversion to list
    brand_list = df_brand['Brands'].tolist()
    black_list = df_black_list['Blacklist'].tolist()

    # check for matches beteen the brand list and the blacklist using an 80 similarity score
    df_results, df_goodmatch, df_badmatch = match_checker(brand_list, black_list, similarity_score = 80.)
    
    #removing fuzzy duplicates
    duplicate_list = ['12345678','12345678', '12345678-A', '6724914-A', '6724914-B', '182456783']
    true_list, predicted_list, unique_list = duplicate_remover(duplicate_list, similarity_score=85)
    
    #outputing results of match to excel file
    excel_results(df_results, outfile_name='test')



    


