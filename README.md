# 📊 Twitter Big Data Analysis

![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=java&logoColor=white)
![Apache Spark](https://img.shields.io/badge/Apache_Spark-E25A1C?style=for-the-badge&logo=apache-spark&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

This project analyzes Twitter data using Apache Spark to perform various analytics on tweets, including topic modeling, engagement metrics, and temporal analysis.

## 🎯 Project Overview

The project processes Twitter data to answer several key questions and uncover trends related to the football transfer market and news:
- Monthly **"Here we go"** tweet analysis
- Engagement comparison between confirmed transfers and rumors
- Most active transfer periods
- Topic modeling of tweets
- Top words per topic

## 🛠️ Technologies Used

- **Java 8+**
- **Apache Spark** (Distributed data processing)
- **Maven** (Dependency management)
- **Python** (Data visualization and charting)

## 📋 Prerequisites

Ensure you have the following installed before running the project:
- Java JDK 8 or higher
- Apache Spark
- Maven
- Python 3.x (for running visualization scripts)

## 📁 Project Structure

```text
.
├── src/
│   ├── main/
│   │   ├── java/com/twitter/analysis/
│   │   │   ├── SparkJob.java
│   │   │   └── Tweet.java
│   │   └── resources/
│   │       └── stopwords.txt
├── visualize_results.py      # Python script for generating visualizations
└── Visualizations/           # Directory containing generated graphical insights
```

## 🚀 Getting Started

### 1. Build the Project
Use Maven to clean and package the Java application:
```bash
mvn clean package
```

### 2. Run the Spark Analysis
Submit the Spark job to process the data and generate the CSV outputs. This will run locally using all available cores:
```bash
spark-submit --class com.twitter.analysis.SparkJob --master local[*] target/twitter-bigdata-analysis-1.0-SNAPSHOT.jar
```

### 3. Generate Visualizations
Once the Spark job finishes, run the Python script to read the generated outputs and create visual representations:
```bash
python visualize_results.py
```

## 📈 Visualizations & Insights

The analysis results are visualized using Python. The generated charts are saved in the `Visualizations/` directory and provide deep insights into the dataset:

- **Temporal Trends**: `daily_tweet_frequency.png`, `hourly_tweet_frequency.png`
- **Engagement Analysis**: `daily_engagement_trends.png`, `hourly_engagement_trends.png`, `event_engagement_by_type.png`
- **Transfer Market Metrics**: `here_we_go_monthly_count.png`, `most_active_transfer_periods.png`
- **Topic Modeling**: `topic_*_wordcloud.png` for various extracted themes (e.g., Match Results, Transfer Market Buzz, Contracts, etc.)
- **Advanced Metrics**: `correlation_heatmap.png`, `co_occurrence_network.png`

## 📂 Output Data

The Spark analysis produces several CSV files in the `output/` directory, which are used by the visualization script:
- `events/here_we_go_monthly_count/part-*.csv`: Monthly counts of "Here we go" tweets.
- `events/event_engagement_metrics/part-*.csv`: Engagement metrics for different event types.
- `events/most_active_transfer_periods/part-*.csv`: Analysis of most active transfer periods.
- `topics/top_topic_words/part-*.csv`: Top words for each identified topic.

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
