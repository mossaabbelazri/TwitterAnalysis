# Twitter Big Data Analysis Project

This project analyzes Twitter data using Apache Spark to perform various analytics on tweets, including topic modeling, engagement metrics, and temporal analysis.

## Project Overview

The project processes Twitter data to answer several key questions:
- Monthly "Here we go" tweet analysis
- Engagement comparison between confirmed transfers and rumors
- Most active transfer periods
- Topic modeling of tweets
- Top words per topic

## Technologies Used

- Java 8+
- Apache Spark
- Maven
- Power BI (for visualization)

## Prerequisites

- Java JDK 8 or higher
- Apache Spark
- Maven

## Project Structure

```
src/
├── main/
│   ├── java/
│   │   └── com/
│   │       └── twitter/
│   │           └── analysis/
│   │               ├── SparkJob.java
│   │               └── Tweet.java
│   └── resources/
│       └── stopwords.txt
```

## Building the Project

```bash
mvn clean package
```

## Running the Analysis

```bash
spark-submit --class com.twitter.analysis.SparkJob --master local[*] target/twitter-bigdata-analysis-1.0-SNAPSHOT.jar
```

## Output

The analysis generates several CSV files in the `output` directory:
- `events/here_we_go_monthly_count/part-00000.csv`: Monthly counts of "Here we go" tweets
- `events/event_engagement_metrics/part-00000.csv`: Engagement metrics for different event types
- `events/most_active_transfer_periods/part-00000.csv`: Analysis of most active transfer periods
- `topics/top_topic_words/part-00000.csv`: Top words for each identified topic

## Topic Analysis

The project identifies five main topics in the tweets:
1. Match Results & Player Performance
2. Transfer Market Buzz & Club Specifics
3. Awards & Competitions
4. Direct Quotes & Player Intent
5. Contract & Loan Negotiations

## Visualization

The analysis results are visualized using Power BI for better insights and presentation.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 