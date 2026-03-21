import pandas as pd
import os
from sqlalchemy import create_engine
import logging
import time 

# Logging info about loading data / creating a dataframe
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/ingestion_db.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a",
    force=True
)

# Creating a connection to databse using SQLite
engine = create_engine('sqlite:///inventory.db')

# Defining a fucntion to ingest csv files into dataset
def ingest_db(df, table_name, engine):
    df.to_sql(table_name, con = engine, if_exists = 'replace', index =False)  # let if_exists = append (For continous)


# Reading CSV Files and getting their dimensions specifically .CSV
# Creating databse from the csv files
def load_raw_data():
    '''This function will load the CSVs as a dataframe and ingest it into database (inventory.db)'''
    start = time.time()
    for file in os.listdir('Data'):
          if file.endswith('.csv'):
            df = pd.read_csv('Data/' + file)
            logging.info(f'Ingesting {file} | Rows: {df.shape[0]}')
            ingest_db(df, file[:-4], engine) # -4 is last four entities in every file name that is .CSV
    end = time.time()
    total_time = (end-start)/60
    logging.info('Ingestion Complete') 
    logging.info(f'Total Time Taken: {total_time:.2f} min')

if __name__ == '__main__':
    load_raw_data()
