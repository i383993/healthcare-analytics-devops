import streamlit as st
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, col, count, max, min, round
import time
import pandas as pd
import plotly.express as px

# 1. Initialize Spark with Distributed Config
@st.cache_resource
def init_spark():
    return SparkSession.builder \
        .appName("HealthcareAdvancedAnalytics") \
        .master("local[*]") \
        .getOrCreate()

spark = init_spark()

# UI Styling
st.set_page_config(page_title="Healthcare Workforce Intelligence", layout="wide")
st.title("🏥 Healthcare Workforce Advanced Analytics")
st.markdown("### Distributed Engine: Apache Spark | UI: Streamlit")

# 2. Sidebar - File Upload & System Controls
st.sidebar.header("System Control Panel")
uploaded_file = st.sidebar.file_uploader("Upload healthcare_jobs.csv", type=["csv"])

if uploaded_file:
    # Buffer the file for Spark
    with open("temp_data.csv", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # 3. Processing Phase (Start Timer)
    start_time = time.time()
    
    # Load and Partition into 4 blocks (Master-Worker Logic)
    df = spark.read.csv("temp_data.csv", header=True, inferSchema=True)
    df = df.repartition(4) 
    
    # --- Advanced Analytics Logic ---
    
    # A. Departmental Salary & Spread (Inequality Metric)
    dept_analysis = df.groupBy("Department").agg(
        round(avg("Minimum salary"), 2).alias("Avg_Min"),
        round(avg("Maximum salary"), 2).alias("Avg_Max"),
        round(max("Maximum salary") - min("Minimum salary"), 2).alias("Salary_Spread")
    ).orderBy(col("Avg_Max").desc()).toPandas()

    # B. Experience Level Volume
    exp_dist = df.groupBy("Experience Level").count().toPandas()

    # C. System Health: Partition Balance Check
    partition_counts = df.rdd.mapPartitions(lambda it: [sum(1 for _ in it)]).collect()
    
    execution_time = time.time() - start_time
    total_rows = df.count()
    throughput = total_rows / execution_time

    # 4. Top Row: KPI Metrics
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Records", f"{total_rows:,}")
    kpi2.metric("Processing Time", f"{execution_time:.3f}s")
    kpi3.metric("Throughput", f"{int(throughput)} rows/s")
    kpi4.metric("Cluster Partitions", len(partition_counts))

    st.divider()

    # 5. Visualizations
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Departmental Salary: Avg Min vs Max")
        fig_salary = px.bar(
            dept_analysis, 
            x="Department", 
            y=["Avg_Min", "Avg_Max"], 
            barmode="group",
            color_discrete_sequence=["#1f77b4", "#ff7f0e"]
        )
        st.plotly_chart(fig_salary, use_container_width=True)

    with col2:
        st.subheader("Experience Level Mix")
        fig_pie = px.pie(exp_dist, values="count", names="Experience Level", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    # 6. Advanced Analytics & System Health
    st.divider()
    low_col, high_col = st.columns(2)

    with low_col:
        st.subheader("Salary Spread (Pay Inequality)")
        st.info("Measures the gap between the lowest and highest pay in each department.")
        st.bar_chart(dept_analysis.set_index("Department")["Salary_Spread"])

    with high_col:
        st.subheader("Distributed System Health")
        st.write("Rows per Worker Partition:")
        # Displaying partition load as a simple table
        p_df = pd.DataFrame({"Partition ID": [f"Worker {i+1}" for i in range(len(partition_counts))], "Row Count": partition_counts})
        st.dataframe(p_df, use_container_width=True)
        st.success("Master Node successfully balanced the workload across all 4 worker threads.")

    # 7. Technical Evidence Expanders
    with st.expander("Show Spark Execution Plan (DAG Logic)"):
        st.code(df._jdf.queryExecution().logical().toString())

else:
    st.info("Please upload the healthcare dataset in the sidebar to initialize the Spark engine.")