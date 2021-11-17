#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 22:50:48 2021

@author: julie-schnurr
"""

import pandas as pd
import numpy as np
import math
from fuzzywuzzy import fuzz

def excel_results(df_results, outfile_name):
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
    max_score = -1
    max_name = ''
    for x in list_names:
        score = fuzz.ratio(name, x)
        if (score > min_score) & (score > max_score):
            max_name = x
            max_score = score
    return (max_name, max_score)

def match_token(name, list_names, min_score=0):
    max_score = -1
    max_name = ''
    for x in list_names:
        score = fuzz.token_sort_ratio(name, x)
        if (score > min_score) & (score > max_score):
            max_name = x
            max_score = score
    return (max_name, max_score)

def match_checker(input_list, matchto_list, similarity_score):
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
            
    data = {'Family Cite': matched_array, 'Best Citation Match': guess_array, 
            'Match Score': ratio_array}  
    df = pd.DataFrame(data)
    df['Match Score'] = df['Match Score'].astype(int) # make score an integer for inequalities
    
    df_results = df
    df_goodmatch =  df_results[df_results['Match Score'] >= similarity_score]
    df_badmatch =  df_results[df_results['Match Score'] < similarity_score]
    
    return df_results, df_goodmatch, df_badmatch

def duplicate_remover(input_list, similarity_score):
    
    # getting rid of nan values
    
    for idx, value in enumerate(input_list):
        # removing the instance we are checking for from the list
        input_list_2 = input_list.copy()
        input_list_2.remove(value)
        
        # first checking for an exact match
        if value in input_list_2:
            max_name = value
            max_score = 100
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
            input_list[idx] = max_name
            
    unique_list = np.unique(input_list)
           
    return unique_list

if __name__ == '__main__':


    df_best_buy = pd.read_excel("Best Buy Accused Products.xlsx", header=0, usecols="A:C", nrows=1581)
    df_black_list = pd.read_excel("Best Buy Accused Products.xlsx", header=0, usecols="F", nrows=50)
    
    bestbuy_list = df_best_buy['Best Buy Brands'].tolist()
    black_list = df_black_list['Blacklist'].tolist()

    
    df_results, df_goodmatch, df_badmatch = match_checker(bestbuy_list, black_list, similarity_score = 80.)

    unique_list = duplicate_remover(black_list, similarity_score=80)
    
    excel_results(df_results, outfile_name='test2')



    


