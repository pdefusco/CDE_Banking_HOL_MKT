#****************************************************************************
# (C) Cloudera, Inc. 2020-2023
#  All rights reserved.
#
#  Applicable Open Source License: GNU Affero General Public License v3.0
#
#  NOTE: Cloudera open source products are modular software products
#  made up of hundreds of individual components, each of which was
#  individually copyrighted.  Each Cloudera open source product is a
#  collective work under U.S. Copyright Law. Your license to use the
#  collective work is as provided in your written agreement with
#  Cloudera.  Used apart from the collective work, this file is
#  licensed for your use pursuant to the open source license
#  identified above.
#
#  This code is provided to you pursuant a written agreement with
#  (i) Cloudera, Inc. or (ii) a third-party authorized to distribute
#  this code. If you do not have a written agreement with Cloudera nor
#  with an authorized and properly licensed third party, you do not
#  have any rights to access nor to use this code.
#
#  Absent a written agreement with Cloudera, Inc. (“Cloudera”) to the
#  contrary, A) CLOUDERA PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY
#  KIND; (B) CLOUDERA DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED
#  WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT LIMITED TO
#  IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND
#  FITNESS FOR A PARTICULAR PURPOSE; (C) CLOUDERA IS NOT LIABLE TO YOU,
#  AND WILL NOT DEFEND, INDEMNIFY, NOR HOLD YOU HARMLESS FOR ANY CLAIMS
#  ARISING FROM OR RELATED TO THE CODE; AND (D)WITH RESPECT TO YOUR EXERCISE
#  OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, CLOUDERA IS NOT LIABLE FOR ANY
#  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR
#  CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO, DAMAGES
#  RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF
#  BUSINESS ADVANTAGE OR UNAVAILABILITY, OR LOSS OR CORRUPTION OF
#  DATA.
#
# #  Author(s): Paul de Fusco
#***************************************************************************/

from os.path import exists
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from utils import *
from datetime import datetime
import sys, random, os, json, random, configparser

## CDE PROPERTIES

def parseProperties():
    """
    Method to parse total number of HOL participants argument
    """
    try:
        print("PARSING JOB ARGUMENTS...")
        maxParticipants = sys.argv[1]
    except Exception as e:
        print("READING JOB ARG UNSUCCESSFUL")
        print('\n')
        print(f'caught {type(e)}: e')
        print(e)

    return maxParticipants


def createSparkSession():
    """
    Method to create an Iceberg Spark Session
    """

    try:
        spark = SparkSession \
            .builder \
            .appName("BANK TRANSACTIONS LOAD") \
            .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog")\
            .config("spark.sql.catalog.spark_catalog.type", "hive")\
            .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")\
            .getOrCreate()
    except Exception as e:
        print("LAUNCHING SPARK SESSION UNSUCCESSFUL")
        print('\n')
        print(f'caught {type(e)}: e')
        print(e)

    return spark


def createDatabase(spark, dbname):
    """
    Method to create a Database for the Specified User
    """
    try:
        print("CREATING BANKING TRANSACTIONS DATABASE...")
        spark.sql("DROP DATABASE IF EXISTS {} CASCADE".format(dbname))
        spark.sql("CREATE DATABASE IF NOT EXISTS {}".format(dbname))

        print("SHOW DATABASES LIKE '{}'".format(dbname))
        spark.sql("SHOW DATABASES LIKE '{}'".format(dbname)).show()
        print("\n")
    except Exception as e:
        print("CREATING DATABASE UNSUCCESSFUL")
        print('\n')
        print(f'caught {type(e)}: e')
        print(e)


def createData(spark):
    """
    Method to create a Banking Transactions dataframe using the dbldatagen and Faker frameworks
    """

    try:
        print("CREATING BANKING TRANSACTIONS DF...\n")
        dg = BankDataGen(spark)
        bankTransactionsDf = dg.bankDataGen()
    except Exception as e:
        print("CREATING TABLE UNSUCCESSFUL")
        print('\n')
        print(f'caught {type(e)}: e')
        print(e)

    return bankTransactionsDf


def createTable(bankTransactionsDf, dbname, username):
    """
    Method to create an Iceberg Table to store Banking Transactions
    """

    print("CREATING BANKING TRANSACTIONS TABLE...\n")

    try:
        bankTransactionsDf\
            .writeTo("{0}.BNK_TRNS_{1}"\
            .format(dbname, username))\
            .using("iceberg")\
            .tableProperty("write.format.default", "parquet")\
            .createOrReplace()
    except Exception as e:
        print("CREATING SYNTHETIC DATA UNSUCCESSFUL")
        print('\n')
        print(f'caught {type(e)}: e')
        print(e)


def validateTable(spark, dbname):
    """
    Method to validate the successful creation of user's DB and Table
    """

    try:
        print("VALIDATING DATABASE AND TABLES {}\n".format(dbname))
        spark.sql("SHOW TABLES IN {}".format(dbname))
    except Exception as e:
        print("VALIDATING DATABASE UNSUCCESSFUL")
        print('\n')
        print(f'caught {type(e)}: e')
        print(e)


def main():

    maxParticipants = parseProperties()
    spark = createSparkSession()

    for i in range(int(maxParticipants)):
        if i+1 < 10:
            username = "user00" + str(i+1)
        elif i+1 > 9 & i+1 < 99:
            username = "user0" + str(i+1)
        elif i+1 > 99:
            username = "user" + str(i+1)

        print("PROCESSING USER {}...\n".format(username))

        createDatabase(spark, username)
        df = createData(spark)
        createTable(df, username, username)
        validateTable(spark, username)


if __name__ == "__main__":
    main()
