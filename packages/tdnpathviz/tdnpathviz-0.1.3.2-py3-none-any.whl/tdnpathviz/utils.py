import functools
import teradataml as tdml
import os
from packaging import version
from collections import OrderedDict

def is_version_greater_than(tested_version, base_version="17.20.00.03"):
    """
    Check if the tested version is greater than the base version.

    Args:
        tested_version (str): Version number to be tested.
        base_version (str, optional): Base version number to compare. Defaults to "17.20.00.03".

    Returns:
        bool: True if tested version is greater, False otherwise.
    """
    return version.parse(tested_version) > version.parse(base_version)
def execute_query_wrapper(f):
    """
    Decorator to execute a query. It wraps around the function and adds exception handling.

    Args:
        f (function): Function to be decorated.

    Returns:
        function: Decorated function.
    """
    @functools.wraps(f)
    def wrapped_f(*args, **kwargs):
        query = f(*args, **kwargs)
        if is_version_greater_than(tdml.__version__, base_version="17.20.00.03"):
            if type(query) == list:
                for q in query:
                    try:
                        tdml.execute_sql(q)
                    except Exception as e:
                        print(str(e).split('\n')[0])
                        print(q)
            else:
                try:
                    tdml.execute_sql(query)
                except Exception as e:
                    print(str(e).split('\n')[0])
                    print(query)
        else:
            if type(query) == list:
                for q in query:
                    try:
                        tdml.get_context().execute(q)
                    except Exception as e:
                        print(str(e).split('\n')[0])
                        print(q)
            else:
                try:
                    tdml.get_context().execute(query)
                except Exception as e:
                    print(str(e).split('\n')[0])
                    print(query)
        return
    return wrapped_f


def execute_query(query):
    if is_version_greater_than(tdml.__version__, base_version="17.20.00.03"):
        if type(query) == list:
            for q in query:
                try:
                    tdml.execute_sql(q)
                except Exception as e:
                    print(str(e).split('\n')[0])
                    print(q)
        else:
            try:
                return tdml.execute_sql(query)
            except Exception as e:
                print(str(e).split('\n')[0])
                print(query)
    else:
        if type(query) == list:
            for q in query:
                try:
                    tdml.get_context().execute(q)
                except Exception as e:
                    print(str(e).split('\n')[0])
                    print(q)
        else:
            try:
                return tdml.get_context().execute(query)
            except Exception as e:
                print(str(e).split('\n')[0])
                print(query)
    return

def find_longest_common_substring(strings):
    """
    Finds the longest common substring among a list of strings.

    Parameters
    ----------
    strings : list of str
        A list of strings to find the common substring.

    Returns
    -------
    str
        The longest common substring found in all strings.
    """
    if not strings:
        return ""

    # Start with the first string in the list
    common_substring = strings[0]

    for string in strings[1:]:
        # Find the longest common substring between common_substring and string
        common_length = min(len(common_substring), len(string))
        temp_common_substring = ""

        for i in range(common_length):
            if common_substring[i] == string[i]:
                temp_common_substring += common_substring[i]
            else:
                break

        # Update the common substring
        common_substring = temp_common_substring

    return common_substring


def remove_common_substring_from_features(features):
    """
    Removes the longest common substring from a list of feature names.

    Parameters
    ----------
    features : list of str
        A list of feature names.

    Returns
    -------
    list of str
        A list of feature names with the common substring removed.
    """
    common_substring = find_longest_common_substring(features)

    # Remove the common substring from each feature
    updated_features = [feature.replace(common_substring, "", 1).strip() for feature in features]

    return updated_features


def rename_numeric_column_name(df, root_string='_'):
    """
    Renames columns in a DataFrame by prepending a specified string to any column name that is a number.

    Parameters:
    df (pandas.DataFrame): The DataFrame whose column names are to be renamed.
    root_string (str): The string to prepend to column names that are numeric. Default is '_'.

    Returns:
    pandas.DataFrame: A DataFrame with renamed columns if any were numeric, otherwise the original DataFrame.
    """

    def prepend_to_numbers(string_list, root_string):
        """
        Prepend a specified string to elements in a list that are numbers.

        Parameters:
        string_list (list): A list of strings to check.
        root_string (str): The string to prepend to numeric elements.

        Returns:
        list: A list with the specified string prepended to numeric elements.
        """

        def is_number(s):
            """
            Check if a string represents a number.

            Parameters:
            s (str): The string to check.

            Returns:
            bool: True if the string is a number, False otherwise.
            """
            try:
                float(s)
                return True
            except ValueError:
                return False

        # Prepend root_string to numeric elements in string_list
        return [f"{root_string}{s}" if is_number(s) else s for s in string_list]

    # Generate new column names by prepending root_string to numeric column names
    new_names = prepend_to_numbers(df.columns, root_string)

    # If no column names have changed, return the original DataFrame
    if new_names == list(df.columns):
        return df
    else:
        # Create a dictionary mapping new column names to existing columns
        renaming = OrderedDict()
        for new_, old_ in zip(new_names, df.columns):
            renaming[new_] = df[old_]

        # Return a new DataFrame with renamed columns
        return df.assign(drop_columns=True, **renaming)
