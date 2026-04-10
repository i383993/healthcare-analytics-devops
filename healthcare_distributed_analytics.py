import os
import sys
import time

# Set Java environment variables before Spark initializes
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-17-openjdk-amd64"
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, count


def main():
    spark = SparkSession.builder \
        .appName("HealthcareDistributedAnalytics") \
        .master("local[*]") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    csv_path = "healthcare_jobs.csv"
    output_path = "processed_healthcare_results"

    jobs_df = spark.read.csv(csv_path, header=True, inferSchema=True)

    # Distribute the data across 4 partitions to simulate 4 parallel worker processes coordinating on a cluster.
    jobs_df = jobs_df.repartition(4)

    # Persist the DataFrame so Spark can reuse cached lineage and recover lost partitions.
    # RDD Lineage allows Spark to recompute lost partitions from the original transformations if a Docker container (Worker Node) fails during execution.
    jobs_df = jobs_df.persist()

    start_time = time.time()

    department_salary_df = (
        jobs_df.groupBy("Department")
        .agg(
            avg("Minimum").alias("Avg_Minimum"),
            avg("Maximum").alias("Avg_Maximum")
        )
    )

    experience_count_df = (
        jobs_df.groupBy("Experience")
        .agg(count("Job ID").alias("Job_Count"))
    )

    print("\n=== Average salaries by Department ===")
    department_salary_df.show(truncate=False)

    print("=== Job counts by Experience level ===")
    experience_count_df.show(truncate=False)

    department_salary_df.write.mode("overwrite").csv(f"{output_path}/department_salary", header=True)
    experience_count_df.write.mode("overwrite").csv(f"{output_path}/experience_counts", header=True)

    total_time = time.time() - start_time
    print(f"Total execution time: {total_time:.2f} seconds")

    spark.stop()


if __name__ == "__main__":
    main()
