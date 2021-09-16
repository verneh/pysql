# there goes a call from another file.
from functions import *

# where the magic happens. 
def main():

    # defining the connection to MSSQL. change connection here. change user and pass to your own.
    connection_string = "DRIVER={ODBC Driver 17 for SQL Server}; SERVER=localhost;DATABASE=Survey_Sample_A19;UID=sa;PWD=Yolo8181"

    # storing mssql connection into a variable.
    mssql_connection = db_connect(connection_string)
        
    # our parameterized sql query goes here. this is the query that gets the original raw survey data.
    sql_query = "SELECT ss.QuestionId, ss.SurveyId, a.UserId, ISNULL(av.Answer_Value, -1) \
    as Answer_Value from dbo.SurveyStructure ss LEFT JOIN dbo.Answer a ON ss.SurveyId = a.SurveyId \
    LEFT JOIN dbo.Answer av ON ss.SurveyId = av.SurveyId and a.UserId = av.UserId and ss.QuestionId \
    = av.QuestionId ORDER BY ss.SurveyId, a.UserId ASC" 
        
    # store read query function into a variable.
    results = read_query(mssql_connection, sql_query)

    # initialize header columns for dataframe.
    columns = ['QuestionID', 'SurveyID', 'UserID', 'Answer_Value'] 

    # convert raw survey data to dataframe.
    df = convert_dataframe(results, columns)
    
    # initialize or create view of sql function from the initial or most recent fetch.
    current_view = create_view(df)
    print(current_view)
    
    # does file exist? if no, save file as "alwaysfresh." if it does, save file as "updated" since its most recent.
    file_exist(current_view, 'alwaysfresh.csv')  

    # it will do a check. if there are changes made on the db, we drop the original alwaysfresh, use 
    # the updated csv which will then be renamed to alwaysfresh. if there are none, retain alwaysfresh. 
    # use UserID as the "key" of the two files. 
    try:
        load_updated(current_view, 'alwaysfresh.csv', 'updated.csv', 'UserID')
        print("Now, we have an updated file. but we removed it.")
    except: 
        print("No updated file generated yet.")
        

    # close connection if not needed.
    mssql_connection.close()

# call main.
main()    











