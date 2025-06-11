package com.twitter.analysis;

import java.util.concurrent.atomic.AtomicInteger;

import org.apache.spark.ml.clustering.LDA;
import org.apache.spark.ml.feature.CountVectorizer;
import org.apache.spark.ml.feature.CountVectorizerModel;
import org.apache.spark.ml.feature.StopWordsRemover;
import org.apache.spark.ml.feature.Tokenizer;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.functions;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructType;

public class SparkJob {
    // AtomicInteger to keep track of the total number of tweets processed
    private static final AtomicInteger totalTweetsProcessed = new AtomicInteger(0);

    public static void main(String[] args) {
        // Create Spark session
        SparkSession spark = SparkSession.builder()
                .appName("Twitter Analysis")
                .master("local[*]")  // For local testing, will be overridden in cluster
                .config("spark.sql.legacy.timeParserPolicy", "LEGACY")
                .getOrCreate();

        // Define schema for the CSV
        StructType schema = new StructType()
                .add("tweet_id", DataTypes.StringType)
                .add("user", DataTypes.StringType)
                .add("tweet", DataTypes.StringType)
                .add("date", DataTypes.StringType)
                .add("likes", DataTypes.LongType)
                .add("comments", DataTypes.LongType)
                .add("repost", DataTypes.LongType)
                .add("views", DataTypes.LongType)
                .add("quotes", DataTypes.LongType)
                .add("bookmarks", DataTypes.LongType)
                .add("is_pinned", DataTypes.BooleanType)
                .add("is_retweet", DataTypes.BooleanType)
                .add("is_reply", DataTypes.BooleanType)
                .add("has_media", DataTypes.BooleanType)
                .add("language", DataTypes.StringType)
                .add("source", DataTypes.StringType);

        // Read CSV file from local filesystem
        Dataset<Row> tweetsDF = spark.read()
                .option("header", "true")
                .option("inferSchema", "false")
                .schema(schema)
                .option("mode", "PERMISSIVE") // Set permissive mode to avoid dropping malformed rows
                .option("badRecordsPath", "C:/Users/Lenovo/Desktop/MASTER/Projet/bad_records") // Path to store malformed rows
                .option("charset", "UTF-8") // Explicitly set character set
                .option("quote", "\"") // Explicitly set quote character
                .option("escape", "\"") // Explicitly set escape character
                .option("multiLine", "true") // Allow fields to span multiple lines
                .csv("C:/Users/Lenovo/Desktop/MASTER/Projet/src/src/tweets/new1/FabrizioRomano_tweets.csv");

        // Convert date column to TimestampType after reading as String
        // First, clean the date string by removing the day of the week and then convert to timestamp
        tweetsDF = tweetsDF
                .withColumn("date", functions.regexp_replace(functions.col("date"), "^[A-Za-z]{3}\\s", ""))
                .withColumn("date", functions.to_timestamp(functions.col("date"), "MMM dd HH:mm:ss Z yyyy"));

        // Clean and filter the data
        tweetsDF = tweetsDF
                // .filter(functions.lower(functions.trim(col("user"))).equalTo("fabrizioromano")) // Temporarily commented out to check total rows
                .withColumn("tweet", functions.regexp_replace(functions.col("tweet"), "^\"|\"$", ""))
                .withColumn("tweet", functions.regexp_replace(functions.col("tweet"), "\\\"", "\""))
                .withColumn("tweet", functions.regexp_replace(functions.col("tweet"), "\\n", " "))
                .withColumn("tweet", functions.regexp_replace(functions.col("tweet"), "\\r", " "))
                .withColumn("tweet", functions.regexp_replace(functions.col("tweet"), "\n", " "))
                .withColumn("tweet", functions.regexp_replace(functions.col("tweet"), "\r", " "))
                .withColumn("likes", functions.col("likes").cast("long"))
                .withColumn("comments", functions.col("comments").cast("long"))
                .withColumn("repost", functions.col("repost").cast("long"))
                .withColumn("views", functions.col("views").cast("long"))
                .withColumn("quotes", functions.col("quotes").cast("long"))
                .withColumn("bookmarks", functions.col("bookmarks").cast("long"));
                // Remove any rows with null values in key columns - temporarily commented out for debugging
                // .filter(col("tweet").isNotNull())
                // .filter(col("date").isNotNull())
                // .filter(col("user").isNotNull());

        System.out.println("Tweets after cleaning and filtering: " + tweetsDF.count() + " rows");

        // Add time-based columns for analysis
        tweetsDF = tweetsDF
            .withColumn("hour", functions.hour(functions.col("date")))
            .withColumn("day_of_week", functions.dayofweek(functions.col("date")))
            .withColumn("month", functions.month(functions.col("date")))
            .withColumn("year", functions.year(functions.col("date")));

        // 1. Engagement Trend Analysis
        analyzeEngagementTrends(tweetsDF, "output/engagement_trends");

        // 2. Tweet Frequency Analysis
        analyzeTweetFrequency(tweetsDF, "output/tweet_frequency");

        // 3. Topic Modeling
        performTopicModeling(tweetsDF, "output/topics");

        // 4. Correlation Analysis
        analyzeCorrelations(tweetsDF, "output/correlations");

        // 5. Event Classification Analysis
        analyzeEventTypes(tweetsDF, "output/events");

        // Cache the DataFrame for better performance
        tweetsDF.cache();

        // Update the atomic counter
        totalTweetsProcessed.set((int) tweetsDF.count());

        // Print the total number of tweets processed
        System.out.println("\nTotal tweets processed: " + totalTweetsProcessed.get());

        // Uncache the DataFrame
        tweetsDF.unpersist();

        // Stop Spark session
        spark.stop();
    }

    private static void analyzeEngagementTrends(Dataset<Row> tweetsDF, String outputPath) {
        // Daily engagement metrics
        Dataset<Row> dailyEngagement = tweetsDF
            .withColumn("tweet_date", functions.to_date(functions.col("date")))
            .groupBy("tweet_date")
            .agg(
                functions.avg("likes").as("avg_likes"),
                functions.avg("views").as("avg_views"),
                functions.avg("comments").as("avg_comments"),
                functions.avg("repost").as("avg_reposts")
            )
            .orderBy("tweet_date");

        // Save daily engagement trends
        dailyEngagement.coalesce(1)
            .write()
            .option("header", "true")
            .mode("overwrite")
            .csv(outputPath + "/daily_engagement");

        // Hourly engagement patterns
        Dataset<Row> hourlyEngagement = tweetsDF
            .groupBy("hour")
            .agg(
                functions.avg("likes").as("avg_likes"),
                functions.avg("views").as("avg_views"),
                functions.avg("comments").as("avg_comments"),
                functions.avg("repost").as("avg_reposts")
            )
            .orderBy("hour");

        // Save hourly engagement patterns
        hourlyEngagement.coalesce(1)
            .write()
            .option("header", "true")
            .mode("overwrite")
            .csv(outputPath + "/hourly_engagement");
    }

    private static void analyzeTweetFrequency(Dataset<Row> tweetsDF, String outputPath) {
        // Daily tweet frequency
        Dataset<Row> dailyFrequency = tweetsDF
            .withColumn("tweet_date", functions.to_date(functions.col("date")))
            .groupBy("tweet_date")
            .count()
            .orderBy("tweet_date");

        // Save daily frequency
        dailyFrequency.coalesce(1)
            .write()
            .option("header", "true")
            .mode("overwrite")
            .csv(outputPath + "/daily_frequency");

        // Hourly tweet frequency
        Dataset<Row> hourlyFrequency = tweetsDF
            .groupBy("hour")
            .count()
            .orderBy("hour");

        // Save hourly frequency
        hourlyFrequency.coalesce(1)
            .write()
            .option("header", "true")
            .mode("overwrite")
            .csv(outputPath + "/hourly_frequency");
    }

    private static void performTopicModeling(Dataset<Row> tweetsDF, String outputPath) {
        System.out.println("Starting Topic Modeling...");

        // Tokenize tweets
        Tokenizer tokenizer = new Tokenizer().setInputCol("tweet").setOutputCol("words");
        Dataset<Row> wordsData = tokenizer.transform(tweetsDF);

        // Remove stopwords
        StopWordsRemover remover = new StopWordsRemover()
                .setInputCol("words")
                .setOutputCol("filtered_words");
        Dataset<Row> filteredData = remover.transform(wordsData);

        // Filter out empty arrays after tokenization and stop word removal
        filteredData = filteredData.filter(functions.size(functions.col("filtered_words")).gt(0));

        System.out.println("Documents after tokenization and stop word removal: " + filteredData.count() + " rows");

        // Check if filteredData is empty before proceeding with CountVectorizer and LDA
        if (filteredData.isEmpty()) {
            System.out.println("No valid documents for topic modeling after filtering and tokenization. Skipping LDA.");
            return; // Exit the method if no data
        }

        // Apply CountVectorizer to convert words to feature vectors
        CountVectorizerModel cvModel = new CountVectorizer()
                .setInputCol("filtered_words")
                .setOutputCol("features")
                .setVocabSize(10000)
                .setMinDF(5) // Only include words that appear in at least 5 documents
                .fit(filteredData);

        Dataset<Row> vectorizedData = cvModel.transform(filteredData);

        System.out.println("Documents after vectorization: " + vectorizedData.count() + " rows");

        // If vectorizedData becomes empty after CountVectorizer, handle it
        if (vectorizedData.isEmpty()) {
            System.out.println("No valid vectorized documents for topic modeling. Skipping LDA.");
            return; // Exit the method if no data
        }

        // Perform LDA
        LDA lda = new LDA()
            .setK(5)  // Number of topics
            .setMaxIter(10);

        org.apache.spark.ml.clustering.LDAModel ldaModel = lda.fit(vectorizedData);
        Dataset<Row> topicsDF = ldaModel.transform(vectorizedData);

        // Save topic distribution
        topicsDF.select(functions.col("tweet"), functions.col("topicDistribution").cast(DataTypes.StringType).as("topic_distribution"))
            .coalesce(1)
            .write()
            .option("header", "true")
            .mode("overwrite")
            .csv(outputPath + "/topic_distribution");

        // Interpret topics by extracting top words
        Dataset<Row> topics = ldaModel.describeTopics(10); // Get top 10 words for each topic
        String[] vocabulary = cvModel.vocabulary();

        Dataset<Row> interpretedTopics = topics.withColumn("topic_words",
                functions.udf((scala.collection.mutable.WrappedArray<Integer> wordIndices, scala.collection.mutable.WrappedArray<Double> wordWeights) -> {
                    StringBuilder sb = new StringBuilder();
                    for (int i = 0; i < wordIndices.size(); i++) {
                        if (i > 0) sb.append(", ");
                        sb.append(vocabulary[wordIndices.apply(i)]).append(" (").append(String.format("%.4f", wordWeights.apply(i))).append(")");
                    }
                    return sb.toString();
                }, DataTypes.StringType).apply(functions.col("termIndices"), functions.col("termWeights"))
        ).select("topic", "topic_words");

        // Save interpreted topics
        interpretedTopics.coalesce(1)
            .write()
            .option("header", "true")
            .mode("overwrite")
            .csv(outputPath + "/top_topic_words");
    }

    private static void analyzeCorrelations(Dataset<Row> tweetsDF, String outputPath) {
        // Calculate correlation matrix
        Dataset<Row> correlationDF = tweetsDF.select(
            functions.corr("likes", "views").as("likes_views_corr"),
            functions.corr("likes", "comments").as("likes_comments_corr"),
            functions.corr("likes", "repost").as("likes_reposts_corr"),
            functions.corr("views", "comments").as("views_comments_corr"),
            functions.corr("views", "repost").as("views_reposts_corr"),
            functions.corr("comments", "repost").as("comments_reposts_corr")
        );

        // Save correlation matrix
        correlationDF.coalesce(1)
            .write()
            .option("header", "true")
            .mode("overwrite")
            .csv(outputPath + "/correlation_matrix");
    }

    private static void analyzeEventTypes(Dataset<Row> tweetsDF, String outputPath) {
        // Classify tweets based on keywords
        Dataset<Row> classifiedDF = tweetsDF
            .withColumn("is_transfer", functions.when(
                functions.lower(functions.col("tweet")).like("%transfer%")
                .or(functions.lower(functions.col("tweet")).like("%deal%"))
                .or(functions.lower(functions.col("tweet")).like("%sign%")), true).otherwise(false))
            .withColumn("is_confirmation", functions.when(
                functions.lower(functions.col("tweet")).like("%confirmed%")
                .or(functions.lower(functions.col("tweet")).like("%here we go%"))
                .or(functions.lower(functions.col("tweet")).like("%done deal%")), true).otherwise(false))
            .withColumn("is_rumor", functions.when(
                functions.lower(functions.col("tweet")).like("%rumour%")
                .or(functions.lower(functions.col("tweet")).like("%rumor%"))
                .or(functions.lower(functions.col("tweet")).like("%link%")), true).otherwise(false));

        // Save classified tweets for each category
        classifiedDF.filter(functions.col("is_transfer"))
            .coalesce(1)
            .write()
            .option("header", "true")
            .mode("overwrite")
            .csv(outputPath + "/transfer_tweets");

        classifiedDF.filter(functions.col("is_confirmation"))
            .coalesce(1)
            .write()
            .option("header", "true")
            .mode("overwrite")
            .csv(outputPath + "/confirmation_tweets");

        classifiedDF.filter(functions.col("is_rumor"))
            .coalesce(1)
            .write()
            .option("header", "true")
            .mode("overwrite")
            .csv(outputPath + "/rumor_tweets");

        // Analyze "Here we go" tweets per month (Confirmation tweets)
        Dataset<Row> hereWeGoMonthly = classifiedDF.filter(functions.col("is_confirmation"))
                .withColumn("year_month", functions.date_format(functions.col("date"), "yyyy-MM"))
                .groupBy("year_month")
                .count()
                .orderBy("year_month");

        hereWeGoMonthly.coalesce(1)
            .write()
            .option("header", "true")
            .mode("overwrite")
            .csv(outputPath + "/here_we_go_monthly_count");

        // Analyze most active transfer period
        Dataset<Row> activeTransferPeriods = classifiedDF.filter(functions.col("is_transfer"))
                .withColumn("year_month", functions.date_format(functions.col("date"), "yyyy-MM"))
                .groupBy("year_month")
                .count()
                .orderBy(functions.desc("count"));

        activeTransferPeriods.coalesce(1)
            .write()
            .option("header", "true")
            .mode("overwrite")
            .csv(outputPath + "/most_active_transfer_periods");

        // Calculate and save engagement metrics for event types
        Dataset<Row> eventEngagement = classifiedDF
            .groupBy("is_transfer", "is_confirmation", "is_rumor")
            .agg(
                functions.avg("likes").as("avg_likes"),
                functions.avg("views").as("avg_views"),
                functions.avg("comments").as("avg_comments"),
                functions.avg("repost").as("avg_reposts")
            );

        // Save event analysis
        eventEngagement.coalesce(1)
            .write()
            .option("header", "true")
            .mode("overwrite")
            .csv(outputPath + "/event_engagement");
    }
} 