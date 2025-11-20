import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tdsbrondata
from pyspark.sql import functions as F
from pyspark.sql.types import *
from delta.tables import DeltaTable
from functools import reduce

itemsRequiredColumns = {
    "DienstId": IntegerType(),
    "Source": StringType(),
    "SurrogateKey": LongType(),
    "FacturatieMaand": StringType(),
    "VerkooprelatieId": StringType(),
    "ItemCode": StringType(),
    "Aantal": FloatType()
}

itemsOptionalColumns = {
    "AfwijkendePrijs": FloatType(),
    "DatumVanOrigineel": StringType(),
    "DatumTotOrigineel": StringType(),
    "AantalOrigineel": FloatType(),
    "DurationOrigineel": FloatType()
}

itemsAllColumns = [
    ("DienstId", IntegerType()),
    ("Source", StringType()),
    ("SurrogateKey", LongType()),
    ("FacturatieMaand", StringType()),
    ("VerkooprelatieId", StringType()),
    ("ItemCode", StringType()),
    ("Aantal", FloatType()),
    ("AfwijkendePrijs", FloatType()),
    ("DatumVanOrigineel", StringType()),
    ("DatumTotOrigineel", StringType()),
    ("AantalOrigineel", FloatType()),
    ("DurationOrigineel", FloatType()),
    ("LineId", StringType())
]

def validateItemsSchema(items):
    schemaDict = {f.name: f.dataType for f in items.schema.fields}

    for columnName, expectedType in itemsRequiredColumns.items():
        if columnName not in schemaDict:
            raise ValueError(f"Missing required column '{columnName}'")
        if type(schemaDict[columnName]) != type(expectedType):
            raise TypeError(f"Column '{columnName}' has type {schemaDict[columnName]}, expected {expectedType}")

    for columnName, expectedType in itemsOptionalColumns.items():
        if columnName in schemaDict and type(schemaDict[columnName]) != type(expectedType):
            raise TypeError(f"Column '{columnName}' has type {schemaDict[columnName]}, expected {expectedType}")

def writeItems(items):
    validateItemsSchema(items)

    items = items.withColumn("Id", F.expr("uuid()"))
    items = items.withColumn("LineId", F.lit(None).cast(StringType()))

    items = writeLines(items)

    table = "items"
    tablePath = f"{tdsbrondata.tablesRootPath}/{table}"

    if DeltaTable.isDeltaTable(tdsbrondata._spark, tablePath):
        deltaTable = DeltaTable.forPath(tdsbrondata._spark, tablePath)
        facturatieMaand = items.select("FacturatieMaand").head()["FacturatieMaand"]
        deltaTable.delete(f"FacturatieMaand = '{facturatieMaand}'")
        items.write.format("delta").mode("append").save(tablePath)
    else:
        items.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(tablePath)

def writeLines(items):
    table = "lines"
    tablePath = f"{tdsbrondata.tablesRootPath}/{table}"
    facturatieMaand = items.select("FacturatieMaand").head()["FacturatieMaand"]

    existingitemsOptionalColumns = [col for col in itemsOptionalColumns.keys() if col in items.columns]

    if existingitemsOptionalColumns:
        filterExpression = " AND ".join([f"{col} IS NULL" for col in existingitemsOptionalColumns])
        itemsToAggregate = items.filter(filterExpression)
        itemsToPreserve = items.filter(f"NOT ({filterExpression})")
    else:
        itemsToAggregate = items
        itemsToPreserve = items.limit(0)

    for col, colType in itemsOptionalColumns.items():
        if col not in items.columns:
            itemsToAggregate = itemsToAggregate.withColumn(col, F.lit(None).cast(colType))
            itemsToPreserve = itemsToPreserve.withColumn(col, F.lit(None).cast(colType))

    aggregated = itemsToAggregate.groupBy(
        "DienstId", "FacturatieMaand", "VerkooprelatieId", "ItemCode"
    ).agg(
        F.sum("Aantal").alias("Aantal"),
        F.collect_list("SurrogateKey").alias("SurrogateKeys")
    )

    for col, colType in itemsOptionalColumns.items():
        aggregated = aggregated.withColumn(col, F.lit(None).cast(colType))

    aggregated = aggregated.withColumn(
        "HasItems",
        F.when(
            (F.size("SurrogateKeys") > 1)
            & (F.expr("aggregate(SurrogateKeys, true, (accumulator, x) -> accumulator AND x IS NOT NULL)")),
            True
        ).otherwise(False)
    ).drop("SurrogateKeys").drop("Source")

    aggregated = aggregated.withColumn("Id", F.expr("uuid()"))

    itemsToAggregate = itemsToAggregate.join(
        aggregated.select(
            "DienstId", "FacturatieMaand", "VerkooprelatieId", "ItemCode", "Id"
        ),
        on=["DienstId", "FacturatieMaand", "VerkooprelatieId", "ItemCode"],
        how="left"
    ).withColumnRenamed("Id", "LineId")

    itemsToPreserve = itemsToPreserve.withColumn(
        "HasItems",
        F.when(F.col("SurrogateKey").isNotNull(), True).otherwise(False)
    ).join(
        aggregated.select(
            "DienstId", "FacturatieMaand", "VerkooprelatieId", "ItemCode", "Id"
        ),
        on=["DienstId", "FacturatieMaand", "VerkooprelatieId", "ItemCode"],
        how="left"
    ).withColumnRenamed("Id", "LineId")

    aggregated = aggregated.select([c for c in itemsToPreserve.columns if c not in ["Source", "SurrogateKey", "LineId"]])

    itemsToPreserve = itemsToPreserve.drop("Source", "SurrogateKey")

    lines = aggregated.unionByName(itemsToPreserve)

    if DeltaTable.isDeltaTable(tdsbrondata._spark, tablePath):
        deltaTable = DeltaTable.forPath(tdsbrondata._spark, tablePath)
        deltaTable.delete(f"FacturatieMaand = '{facturatieMaand}'")
        lines.write.format("delta").mode("append").save(tablePath)
    else:
        lines.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(tablePath)

    return itemsToAggregate.unionByName(itemsToPreserve)

def mergeItems(lists, facMonth):

    items = []

    for schema in lists:
        
        df = tdsbrondata.utils.getCurrentData(
            workspaceName='Tosch-Facturatie',
            lakehouseName='S_Items',
            schemaName=schema,
            tableName='items',
            usesScd=False
        )

        df = df.filter(F.col("FacturatieMaand") == facMonth)
        
        for colName, colType in itemsOptionalColumns.items():
            if colName not in df.columns:
                df = df.withColumn(colName, F.lit(None).cast(colType))
            if colType == FloatType():
                df = df.withColumn(colName, F.round(F.col(colName).cast(FloatType()), 2))
            else:
                df = df.withColumn(colName, F.col(colName).cast(colType))
        
        items.append(df)

    dfItems = reduce(lambda df1, df2: df1.unionByName(df2), items)

    return dfItems

def mergeLines(lists, facMonth):

    lines = []

    for schema in lists:
        df = tdsbrondata.utils.getCurrentData(
            workspaceName='Tosch-Facturatie',
            lakehouseName='S_Items',
            schemaName=schema,
            tableName='lines',
            usesScd=False
        )

        df = df.filter(F.col("FacturatieMaand") == facMonth)
        
        for colName, colType in linesAllColumns:
            if colName not in df.columns:
                df = df.withColumn(colName, F.lit(None).cast(colType))
            if colType == FloatType():
                df = df.withColumn(colName, F.round(F.col(colName).cast(FloatType()), 2))
            else:
                df = df.withColumn(colName, F.col(colName).cast(colType))
        
        lines.append(df)

    dfLines = reduce(lambda df1, df2: df1.unionByName(df2), lines)

    return dfLines

