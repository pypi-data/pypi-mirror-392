from pyspark.sql import SparkSession, DataFrame
from delta.tables import DeltaTable
from pyspark.sql.functions import col, lit, when, current_timestamp
import uuid
import traceback

class ChangeLogger:

    def __init__(self,
                 catalog: str,
                 schema: str,
                 tracked_table_name: str,
                 primary_key_fieldname: str,
                 columns_to_track: list):
        
        self.catalog = catalog
        self.schema = schema
        self.tracked_table_name = tracked_table_name
        self.primary_key_fieldname = primary_key_fieldname
        self.columns_to_track = columns_to_track

        # Ensure Spark session exists
        try:
            self.spark = SparkSession.builder.getOrCreate()
        except Exception as e:
            raise RuntimeError(f"Unable to create Spark session: {e}")

    def logTheChangedFields(self, df_NewData: DataFrame):
        try:
            table_name = self.tracked_table_name
            catalog = self.catalog
            schema = self.schema

            # Reference the main Delta table
            full_table_name = f"{catalog}.{schema}.{table_name}"
            delta_table = DeltaTable.forName(self.spark, full_table_name)
            df_existing = delta_table.toDF()

            # Join new and existing data on primary key
            df_joined = df_NewData.alias("new").join(
                df_existing.alias("old"),
                on=self.primary_key_fieldname,
                how="left"
            )

            # Build audit rows per column
            audit_rows = []
            for col_name in self.columns_to_track:
                df_col_changes = df_joined.select(
                    lit(catalog).alias("catalog"),
                    lit(schema).alias("schema"),
                    lit(table_name).alias("table_name"),
                    col(f"new.{self.primary_key_fieldname}").alias("record_id"),
                    lit(col_name).alias("field_name"),
                    when(col("old."+self.primary_key_fieldname).isNull(), lit("insert")).otherwise(lit("update")).alias("change_type"),
                    current_timestamp().alias("change_timestamp"),
                    col(f"old.{col_name}").cast("string").alias("old_value"),
                    col(f"new.{col_name}").cast("string").alias("new_value"),
                    col("old.LastModifiedDate").alias("old_lastmodifieddate"),
                    col("new.LastModifiedDate").alias("new_lastmodifieddate"),
                    lit(str(uuid.uuid4())).alias("audit_id")
                )
                audit_rows.append(df_col_changes)

            # Union all field-level change DataFrames safely
            if audit_rows:
                df_audit = audit_rows[0]
                for next_df in audit_rows[1:]:
                    df_audit = df_audit.unionByName(next_df)

                # Filter out rows where old_value == new_value
                df_audit = df_audit.filter(
                    (col("old_value").isNull() & col("new_value").isNotNull()) |
                    (col("old_value").isNotNull() & col("new_value").isNotNull() & (col("old_value") != col("new_value")))
                )

                # Save audit rows into the generic change log table
                audit_table = f"{catalog}.{schema}.field_change_log"
                if not self.spark.catalog.tableExists(audit_table):
                    df_audit.write.format("delta").mode("overwrite").saveAsTable(audit_table)
                else:
                    df_audit.write.format("delta").mode("append").saveAsTable(audit_table)

            return {"success": True, "error": None}

        except Exception as e:
            return {"success": False, "error": e}
