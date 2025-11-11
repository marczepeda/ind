'''
Module: io.py
Author: Marc Zepeda
Created: 2024-05-20
Description: Input/Output

Usage:
[Parsing Python literals]
- df_try_parse(): apply try_parse() to dataframe columns and return dataframe
- recursive_json_decode(): recursively decode JSON strings in a nested structure

[Input]
- get(): returns pandas dataframe from a file
- get_dir(): returns python dictionary of dataframe from files within a directory

[Output]
- save(): save .csv file to a specified output directory from obj
- save_dir(): save .csv files to a specified output directory from dictionary of objs

[Input/Output]
- excel_csvs(): exports excel file to .csv files in specified directory
- df_to_dc_txt(): returns pandas DataFrame as a printed text that resembles a Python dictionary
- dc_txt_to_df(): returns a pandas DataFrame from text that resembles a Python dictionary
- in_subs(): moves all files with a given suffix into subfolders named after the files (excluding the suffix).
- out_subs(): delete subdirectories and move their files to the parent directory

[Directory Methods]
- relative_paths(): returns relative paths for all files in a directory including subfolders
- sorted_file_names: returns sorted file names in a directory with the specified suffix
'''

# Import packages
import pandas as pd
import os
import ast
import csv
import shutil
import datetime # might use later
import json

from ..utils import try_parse, mkdir

# Parsing Python literals
def df_try_parse(df: pd.DataFrame) -> pd.DataFrame:
    '''
    df_try_parse(): apply try_parse() to dataframe columns and return dataframe

    Parameters: 
    df (dataframe): dataframe with columns to try_parse()
    
    Dependencies: utils.try_parse()
    '''
    # Apply the parsing function to all columns
    for col in df.columns:
        df[col] = df[col].apply(try_parse)
    return df

def recursive_json_decode(obj):
    '''
    recursive_json_decode(): recursively decode JSON strings in a nested structure

    Parameters:
    obj: object of any type (looking for dict, list, or str)
    
    Dependencies: json
    '''
    if isinstance(obj, dict):
        return {k: recursive_json_decode(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [recursive_json_decode(item) for item in obj]
    elif isinstance(obj, str):
        try:
            decoded = json.loads(obj)
            return recursive_json_decode(decoded)
        except (json.JSONDecodeError, TypeError):
            return obj
    return obj

# Input
def get(pt: str, literal_eval:bool=False, **kwargs) -> pd.DataFrame | dict[pd.DataFrame]:
    ''' 
    get(): returns pandas dataframe from a file
    
    Parameters:    
    pt (str): file path
    literal_evals (bool, optional): convert Python literals encoded as strings (Default: False)
        (1) automatically detects and parses columns containing Python literals (e.g., dict, list, set, tuple) encoded as strings
        (2) recursively evaluates nested structures
    **kwargs: pandas.read_csv() parameters
    
    Dependencies: pandas,ast,utils[try_parse(),recursive_parse()],df_try_parse()
    '''
    suf = pt.split('.')[-1]
    if suf=='csv': 
        if literal_eval: return df_try_parse(pd.read_csv(filepath_or_buffer=pt,sep=',',**kwargs))
        else: return pd.read_csv(filepath_or_buffer=pt,sep=',',**kwargs)
    elif suf=='tsv': 
        if literal_eval: return df_try_parse(pd.read_csv(filepath_or_buffer=pt,sep='\t',**kwargs))
        else: return pd.read_csv(filepath_or_buffer=pt,sep='\t',**kwargs)
    elif suf=='xlsx': 
        if literal_eval: 
            dc = {sheet_name:df_try_parse(pd.read_excel(pt,sheet_name,**kwargs))
                                 for sheet_name in pd.ExcelFile(pt).sheet_names}
        else: 
            dc = {sheet_name:pd.read_excel(pt,sheet_name,**kwargs)
                                 for sheet_name in pd.ExcelFile(pt).sheet_names}
        print(f"Excel file: {pt}\nKeys: {', '.join([key for key in dc.keys()])}")
        return dc
    elif suf=='html': 
        if literal_eval: return df_try_parse(pd.read_html(pt,**kwargs))
        else: return pd.read_html(pt,**kwargs)
    else: 
        if literal_eval: return df_try_parse(pd.read_csv(filepath_or_buffer=pt,**kwargs))
        else: return pd.read_csv(filepath_or_buffer=pt,**kwargs)
    
def get_dir(dir: str, suf: str='.csv', literal_eval: bool=False, **kwargs) -> dict[pd.DataFrame]:
    ''' 
    get_dir(): returns python dictionary of dataframe from files within a directory
    
    Parameters:
    dir (str): directory path with files
    suf (str): file type suffix
    literal_evals (bool, optional): convert Python literals encoded as strings (Default: False)
        (1) automatically detects and parses columns containing Python literals (e.g., dict, list, set, tuple) encoded as strings
        (2) recursively evaluates nested structures
    **kwargs: pandas.read_csv() parameters
    
    Dependencies: pandas
    '''
    files = [file for file in os.listdir(dir) if file[-len(suf):]==suf]
    dc = {file[:-len(suf)]:get(os.path.join(dir,file),literal_eval,**kwargs) for file in files}
    print(f"Directory: {dir}\nKeys: {', '.join([key for key in dc.keys()])}")
    return dc

# Output
def save(dir: str, file: str, obj, cols: list=[], id: bool=False, sort: bool=True, **kwargs):
    ''' 
    save(): save .csv file to a specified output directory from obj
    
    Parameters:
    dir (str): output directory path
    file (str): file name
    obj: dataframe, series, set, or list
    cols (str, list, optional): isolate dataframe column(s)
    id (bool, optional): include dataframe index (False)
    sort (bool, optional): sort set, list, or series before saving (True)
    
    Dependencies: pandas, os, csv & utils.mkdir()
    '''
    mkdir(dir) # Make output directory if it does not exist

    if type(obj)==pd.DataFrame:
        for col in cols: # Check if each element in the list is a string
            if not isinstance(col, str):
                raise ValueError("All elements in the list must be strings.")
        if cols!=[]: obj = obj[cols]
        if file.split('.')[-1]=='tsv': obj.to_csv(os.path.join(dir,file), index=id, sep='\t', **kwargs)
        elif file.split('.')[-1]=='xlsx': 
            with pd.ExcelWriter(os.path.join(dir,file)) as writer: 
                obj.to_excel(writer,sheet_name='.'.join(file.split('.')[:-1]),index=id) # Dataframe per sheet
        else: obj.to_csv(os.path.join(dir,file), index=id, **kwargs)
    elif type(obj)==set or type(obj)==list or type(obj)==pd.Series:
        if sort==True: obj2 = sorted(list(obj))
        else: obj2=list(obj)
        with open(os.path.join(dir,file), 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, dialect='excel') # Create a CSV writer object
            csv_writer.writerow(obj2) # Write each row of the list to the CSV file
    elif (type(obj)==dict)&(file.split('.')[-1]=='xlsx'):
        for col in cols: # Check if each element in the list is a string
            if not isinstance(col, str):
                raise ValueError("All elements in the list must be strings.")
        with pd.ExcelWriter(os.path.join(dir,file)) as writer:
            if cols!=[]: obj = obj[cols]
            for key,df in obj.items(): 
                if cols!=[]: df = df[cols]
                df.to_excel(writer,sheet_name=key,index=id) # Dataframe per sheet
    else: raise ValueError(f'save() does not work for {type(obj)} objects with {file.split(".")[-1]} files.')

def save_dir(dir: str, dc: dict, suf: str='.csv', **kwargs):
    ''' 
    save_dir(): save .csv files to a specified output directory from dictionary of objs
    
    Parameters:
    dir (str): output directory path
    dc (dict): dictionary of objects (files)
    suf (str, optional): file name suffix (Default: .csv)

    Dependencies: pandas, os, csv, & save()
    '''
    for key,val in dc.items(): save(dir=dir,file=str(key)+suf,obj=val,**kwargs)

# Input/Output
def excel_csvs(pt: str, dir: str='', **kwargs):
    ''' 
    excel_csvs(): exports excel file to .csv files in specified directory    
    
    Parameters:
    pt (str): excel file path
    dir (str, optional): output directory path (Default: same directory as excel file name)
    
    Dependencies: pandas, os, & mkdir
    '''
    if dir=='': dir = '.'.join(pt.split('.')[:-1]) # Get the directory where the Excel file is located
    mkdir(dir) # Make output directory if it does not exist
    for sheet_name in pd.ExcelFile(pt).sheet_names: # Loop through each sheet in the Excel file
        df = pd.read_excel(pd.ExcelFile(pt),sheet_name,**kwargs) # Read the sheet into a DataFrame
        df.to_csv(os.path.join(dir,f"{sheet_name}.csv"),index=False) # Save the DataFrame to a CSV file

def df_to_dc_txt(df: pd.DataFrame) -> str:
    ''' 
    df_to_dc_txt(): returns pandas DataFrame as a printed text that resembles a Python dictionary
    
    Parameters:
    df (dataframe): pandas dataframe
    
    Dependencies: pandas
    '''
    dict_text = "{\n"
    for index, row in df.iterrows():
        dict_text += f"  {index}: {{\n"
        for col in df.columns:
            value = row[col]
            if isinstance(value, str):
                value = f"'{value}'"
            dict_text += f"    '{col}': {value},\n"
        dict_text = dict_text.rstrip(",\n") + "\n  },\n"  # Remove trailing comma for last key-value pair
    dict_text = dict_text.rstrip(",\n") + "\n}"  # Close the main dictionary
    print(dict_text)
    return dict_text

def dc_txt_to_df(dc_txt: str, transpose: bool=True) -> str:
    ''' 
    dc_txt_to_df(): returns a pandas DataFrame from text that resembles a Python dictionary
    
    Parameters:
    dc_txt (str): text that resembles a Python dictionary
    transpose (bool, optional): transpose dataframe (True)
    
    Dependencies: pandas & ast
    '''
    if transpose==True: return pd.DataFrame(ast.literal_eval(dc_txt)).T
    else: return pd.DataFrame(ast.literal_eval(dc_txt))

def in_subs(dir: str, suf: str): 
    '''
    in_subs: moves all files with a given suffix into subdirectory named after the files (excluding the suffix).

    Parameters:
    dir (str): Path to the directory containing the files.
    suf (str): File suffix (e.g., '.txt', '.csv') to filter files.

    Dependences: os, shutil
    '''
    if not os.path.isdir(dir):
        raise ValueError(f"{dir} is not a valid directory.")

    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        
        if os.path.isfile(file_path) and filename.endswith(suf):
            base_name = filename[:-len(suf)]
            subdir = os.path.join(dir, base_name)

            # Create subfolder if it doesn't exist
            os.makedirs(subdir, exist_ok=True) 

            # Move the file into the subfolder
            new_path = os.path.join(subdir, filename)
            shutil.move(file_path, new_path)

def out_subs(dir: str):
    """
    out_subs(): Delete subdirectories and move their files to the parent directory.

    Parameters:
    dir (str): Path to the directory containing the files.
    """
    if not os.path.isdir(dir):
        raise ValueError(f"{dir} is not a valid directory.")

    for root, dirs, files in os.walk(dir, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            target_path = os.path.join(dir, file)

            # Resolve name conflicts by appending a counter
            base, ext = os.path.splitext(file)
            counter = 1
            while os.path.exists(target_path):
                target_path = os.path.join(dir, f"{base}_{counter}{ext}")
                counter += 1

            shutil.move(file_path, target_path)

        # Remove empty directories
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if os.path.isdir(dir_path) and not os.listdir(dir_path):
                os.rmdir(dir_path)

# Directory Methods
def relative_paths(root_dir: str) -> list[str]:
    ''' 
    relative_paths(): returns relative paths for all files in a directory including subfolders
    
    Parameters:
    root_dir (str): root directory path or relative path

    Dependencies: os
    '''
    relative_paths = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            # Get the relative path of the file
            relative_path = os.path.relpath(os.path.join(dirpath, filename), root_dir)
            relative_paths.append(relative_path)
    return relative_paths

def sorted_file_names(dir: str, suf: str='.csv') -> list[str]:
    '''
    sorted_file_names: returns sorted file names in a directory with the specified suffix

    dir (str): directory path or relative path
    suf (str): suffix to parse file names

    Dependencies: os
    '''
    return sorted([file for file in os.listdir(dir) if file[-len(suf):]==suf])