## Steps:
# 1. Initiate the Data Validation(Read from the path given by the Data Ingestion Artifact)
# 2. 
## Note: We need to validate no. of columns , we need to check whether numerical columns exist or not
## For this we need to define some kind of schema ---> schema path(based on this we will compare how man fields are there).
## This schema path where it needs to be created : Schema file path will be given in training_pipeline
## In data_validation we are going to read that schema

from networksecurity.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact ## (DataIngestionArtifact->This is input to our Data Validation Component
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from scipy.stats import ks_2samp ## For Data Drift we will use the library from scipy(ks_2samp --> This will basically check 2 samples of data to find out whether there is a data drift or not)
import pandas as pd
import os,sys
from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file

class DataValidation:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
                 data_validation_config:DataValidationConfig):  ## Our output here is DataValidationConfig
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    ## Read data function : It is like a common function -> so this function can also be created as a static method. -> Bcoz: This function is going to be used only one time at the data validation stage
    @staticmethod
    def read_data(file_path)->pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def validate_number_of_columns(self,dataframe:pd.DataFrame)->bool:
        try:
            number_of_columns = len(self._schema_config)
            logging.info(f"Required number of columns:{number_of_columns}")
            logging.info(f"Dataframe has columns: {len(dataframe.columns)}")
            if len(dataframe.columns) == number_of_columns:
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def detect_dataset_drift(self,base_df,current_df,threshold=0.05)->bool: ## Base df is the df which we had originally and current df is the current dataframe that we have
        try:
            status=True
            report = {}
            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]
                is_same_dist = ks_2samp(d1,d2)
                if threshold <= is_same_dist.pvalue:
                    is_found = False
                else:
                    is_found = True
                    status = False ## Considering that there is a change in the distribution
                report.update({column:{
                    "p_value":float(is_same_dist.pvalue),
                    "drift_status":is_found
                }})
            drift_report_file_path = self.data_validation_config.drift_report_file_path

            ## Create directory
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path,exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path, content=report)

        except Exception as e:
            raise NetworkSecurityException(e,sys)   
        
    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            ## read the data from train and test ---> then validate the columns and check whether numerical columns exist or not
            train_dataframe = DataValidation.read_data(train_file_path) ## Called the class , read the data from the static function
            test_dataframe = DataValidation.read_data(test_file_path)

            ## validate number of columns
            status = self.validate_number_of_columns(dataframe=train_dataframe)
            if not status:  ## i.e. if its false
                error_message = f"Train dataframe does not contain all columns. \n"
            status = self.validate_number_of_columns(dataframe=test_dataframe)    
            if not status:
                error_message = f"Test dataframe does not contain all columns. \n"

            ## lets check datadrift
            status = self.detect_dataset_drift(base_df=train_dataframe,current_df=test_dataframe)
            dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path,exist_ok=True)

            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path, index=False, header=True
            )

            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path, index=False, header=True
            )

            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_ingestion_artifact.trained_file_path,
                valid_test_file_path=self.data_ingestion_artifact.test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)  


