# import libraries for mini functions.
from csv_diff import load_csv, compare
import os
import os.path
import pyodbc
import pandas as pd

# connection function.
def db_connect(connection):
    
    try:
        db_connection = pyodbc.connect(connection)
        return db_connection
    except:    
         print("Sorry. Couldn't connect to database!")

# define a function that grabs the connection variable and fetches the sql query.
def read_query(connection, query):
    
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")

# this converts data from sql and turn it into a dataframe.
def convert_dataframe(results_db, columns):

    # empty list which ...
  from_db = []

  # ...will be populated by results in a loop.
  for result in results_db:
    result = list(result)
    from_db.append(result)

  # convert to dataframe.
  df = pd.DataFrame(from_db, columns=columns)

  return df

# implementation of python version of sql view.
def create_view(df):

  # pivot dataframe to recreate the view. copy UserID and SurveyID as our first two columns.
  # convert to int to match the sql query. reason is because when you use pandas the values convert to float.
  # also since we're using the recent version of pandas, the display will be <NA> not NaN. (for aesthetic reasons)
  pt = pd.pivot_table(df, values='Answer_Value', index=['UserID', 'SurveyID'], columns=['QuestionID']).astype('Int64')

  # sort values ascending for two columns.
  pt.sort_values(by=['SurveyID', 'UserID'], inplace=True)

  #  remove the name for the columns in our pivot table. removes question id and leaves 1,2,3 
  #  which ends up being our version of ANS_1, ANS_2, ANS_3.
  pt.rename_axis(None, axis=1, inplace=True)

  # reset index so that 1, 2, 3 are at equal level with UserID, SurveyID
  pt.reset_index(inplace=True)

  # ANS_Q4 was null so limited it to ANS_Q3. Will add one once it populates.
  pt.rename(columns={1:'ANS_Q1',2:'ANS_Q2',3:'ANS_Q3'}, inplace=True)

  # set the index to one.
  pt.index +=1

  # return pivoted dataframe.
  return(pt)

# store initial file. a one time thing.
def store_initial(view):
    try:
      return view.to_csv('alwaysfresh.csv', index=False)
    except FileNotFoundError:
      print("The file does not exist.")

# store freshly extracted file.
def store_updated(view):
    try:
      return view.to_csv('updated.csv', index=False)
    except FileNotFoundError:
      print("The file does not exist.")


# check if the file exists.
def file_exist(view, file): 

    # to check if alwaysfresh exists, if it does...
    if os.path.isfile(file):
        # ...should produce the updated csv. 
        store_updated(view) 
     

    # initial store.    
    else:    
        store_initial(view)
        

# check if there are changes in the csv. if there are, numbers are populated inside the assert brackets.
def test_csv_changed(file1, file2, id):
    
    # compare csvs stored in a variable.
    diff = compare(
        # file1 is for alwaysfresh. file2 is for the recently extracted file.
        # key is the column of reference. in our case, it's for UserID.
        load_csv(open(file1), key=id), load_csv(open(file2), key=id)
    )
    # with a simple assert to see if changes were made on the file.
    assert {
        "added": [],
        "removed": [],
        "changed": [],
        "columns_added": [],
        "columns_removed": [],
    } == diff


# compare difference between two files and load updated.
def load_updated(view, file1, file2, id): 
    
    try:
      test_csv_changed(file1, file2, id)
    # the idea is if an error is thrown. it means there's a change in the file 
    except AssertionError:
      # we retain the updated file.
      store_updated(view)
      # remove the current alwaysfresh fle.
      os.remove('alwaysfresh.csv')
      # rename the updated csv tand replace it with alwaysfresh.
      os.rename('updated.csv','alwaysfresh.csv')
      # rename the file and delete old always fresh.

    else:
      # retain alwaysfresh and remove the updated file.
      os.remove('updated.csv')
    
    

