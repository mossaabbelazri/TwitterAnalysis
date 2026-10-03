import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import os
import networkx as nx

# Base path for the output data
BASE_PATH = 'output'

def plot_daily_engagement():
    """Plots daily engagement trends."""
    # ===== PLOT: Daily Engagement Trends =====
    path = os.path.join(BASE_PATH, 'engagement_trends/daily_engagement')
    if not os.path.exists(path):
        print(f"Directory not found: {path}")
        return
        
    df = pd.read_csv(os.path.join(path, [f for f in os.listdir(path) if f.endswith('.csv')][0]))
    df['tweet_date'] = pd.to_datetime(df['tweet_date'])
    df.set_index('tweet_date', inplace=True)
    
    plt.figure(figsize=(15, 7))
    plt.plot(df.index, df['avg_likes'], label='Average Likes')
    plt.plot(df.index, df['avg_views'], label='Average Views')
    plt.plot(df.index, df['avg_comments'], label='Average Comments')
    plt.plot(df.index, df['avg_reposts'], label='Average Reposts')
    plt.title('Daily Engagement Trends', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Date', fontsize=12, fontweight='bold')
    plt.ylabel('Average Count', fontsize=12, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True)
    plt.savefig(os.path.join(BASE_PATH, 'daily_engagement_trends.png'))
    plt.show()

def plot_hourly_engagement():
    """Plots hourly engagement trends."""
    # ===== PLOT: Hourly Engagement Trends =====
    path = os.path.join(BASE_PATH, 'engagement_trends/hourly_engagement')
    if not os.path.exists(path):
        print(f"Directory not found: {path}")
        return
        
    df = pd.read_csv(os.path.join(path, [f for f in os.listdir(path) if f.endswith('.csv')][0]))
    df.sort_values('hour', inplace=True)
    
    plt.figure(figsize=(15, 7))
    plt.plot(df['hour'], df['avg_likes'], label='Average Likes', marker='o', linewidth=2)
    plt.plot(df['hour'], df['avg_views'], label='Average Views', marker='s', linewidth=2)
    plt.plot(df['hour'], df['avg_comments'], label='Average Comments', marker='^', linewidth=2)
    plt.plot(df['hour'], df['avg_reposts'], label='Average Reposts', marker='d', linewidth=2)
    plt.title('Hourly Engagement Trends', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Hour of Day', fontsize=12, fontweight='bold')
    plt.ylabel('Average Count', fontsize=12, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.xticks(range(0, 24))
    plt.savefig(os.path.join(BASE_PATH, 'hourly_engagement_trends.png'))
    plt.show()

def plot_correlation_heatmap():
    """Plots a heatmap of the correlation matrix with improved labels."""
    # ===== PLOT: Correlation Heatmap =====
    path = os.path.join(BASE_PATH, 'correlations/correlation_matrix')
    if not os.path.exists(path):
        print(f"Directory not found: {path}")
        return

    df = pd.read_csv(os.path.join(path, [f for f in os.listdir(path) if f.endswith('.csv')][0]))
    
    # Shorten the column names for better readability
    renamed_columns = {
        'likes_views_corr': 'Likes & Views',
        'likes_comments_corr': 'Likes & Comments',
        'likes_reposts_corr': 'Likes & Reposts',
        'views_comments_corr': 'Views & Comments',
        'views_reposts_corr': 'Views & Reposts',
        'comments_reposts_corr': 'Comments & Reposts'
    }
    df.rename(columns=renamed_columns, inplace=True)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(df, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Matrix of Engagement Metrics', fontsize=16, fontweight='bold', pad=20)
    plt.xticks(rotation=45, ha='right', fontsize=11, fontweight='bold') # Rotate labels for better fit
    plt.yticks(rotation=0, fontsize=11, fontweight='bold')
    plt.tight_layout() # Adjust layout to prevent labels from being cut off
    plt.savefig(os.path.join(BASE_PATH, 'correlation_heatmap.png'))
    plt.show()

def plot_top_topic_words():
    """Generates word clouds for top topic words."""
    # ===== PLOT: Topic Word Clouds =====
    path = os.path.join(BASE_PATH, 'topics/top_topic_words')
    if not os.path.exists(path) or not any(f.endswith('.csv') for f in os.listdir(path)):
        print(f"Data not found for topic word clouds: {path}")
        return
        
    df = pd.read_csv(os.path.join(path, [f for f in os.listdir(path) if f.endswith('.csv')][0]))

    # Manually defined titles for each topic based on their words
    topic_titles = {
        0: "Match & Season Highlights",
        1: "Transfers & Contracts",
        2: "Specific Player Discussions",
        3: "Club & Player Status",
        4: "Club & Award News"
    }
    
    for index, row in df.iterrows():
        # The 'words' column now contains a string like '{word1=0.1, word2=0.05, ...}'
        words_str = row['words']
        
        # Safely parse the string into a dictionary
        try:
            # Clean up the string for parsing
            words_str = words_str.strip('{}')
            if not words_str:
                continue

            # Create a dictionary of word to weight
            word_freq = {item.split('=')[0].strip(): float(item.split('=')[1]) for item in words_str.split(', ')}

            wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq)
            
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            # Use the descriptive title, fall back to the topic number if not found
            title = topic_titles.get(row['topic'], f'Topic {row["topic"]}')
            plt.title(title, pad=20, fontsize=16, fontweight='bold') # Add more padding to move title up
            plt.savefig(os.path.join(BASE_PATH, f'topic_{row["topic"]}_wordcloud.png'))
            plt.show()

        except Exception as e:
            print(f"Could not generate word cloud for topic {row['topic']}: {e}")

    print("Successfully generated topic word clouds.")

def plot_monthly_predictions():
    """Plots the monthly engagement predictions."""
    # ===== PLOT: Monthly Predictions =====
    path = os.path.join(BASE_PATH, 'predictions/monthly_likes_prediction')
    if not os.path.exists(path):
        print(f"Directory not found: {path}")
        return

    df = pd.read_csv(os.path.join(path, [f for f in os.listdir(path) if f.endswith('.csv')][0]))
    df['year_month'] = pd.to_datetime(df['year_month'], format='%Y-%m')
    df.sort_values('year_month', inplace=True)

    # Convert formatted strings back to numbers for plotting
    df['total_likes_numeric'] = df['total_likes_formatted'].str.replace(',', '').astype(float)
    df['prediction_numeric'] = df['prediction_formatted'].str.replace(',', '').astype(float)
    df['difference_numeric'] = df['difference_formatted'].str.replace(',', '').astype(float)

    plt.figure(figsize=(15, 7))
    plt.plot(df['year_month'], df['total_likes_numeric'], label='Actual Likes', marker='o')
    plt.plot(df['year_month'], df['prediction_numeric'], label='Predicted Likes', linestyle='--', marker='x')
    plt.title('Monthly Likes: Actual vs. Predicted', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Month', fontsize=12, fontweight='bold')
    plt.ylabel('Total Likes', fontsize=12, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True)
    plt.savefig(os.path.join(BASE_PATH, 'monthly_likes_prediction.png'))
    plt.show()

    # Also create a difference plot
    plt.figure(figsize=(15, 7))
    plt.bar(df['year_month'], df['difference_numeric'], color=['red' if x > 0 else 'blue' for x in df['difference_numeric']])
    plt.title('Monthly Prediction Difference (Actual - Predicted)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Month', fontsize=12, fontweight='bold')
    plt.ylabel('Difference in Likes', fontsize=12, fontweight='bold')
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(BASE_PATH, 'monthly_prediction_difference.png'))
    plt.show()

def display_co_occurrence_rules():
    """Displays the top co-occurrence rules."""
    # ===== TABLE: Co-occurrence Rules =====
    path = os.path.join(BASE_PATH, 'co_occurrence/co_occurrence_rules')
    if not os.path.exists(path):
        print(f"Directory not found: {path}")
        return
        
    df = pd.read_csv(os.path.join(path, [f for f in os.listdir(path) if f.endswith('.csv')][0]))
    df = df.sort_values(by=['lift', 'confidence'], ascending=[False, False])
    print("Top Word Co-occurrence Rules (sorted by Lift and Confidence):")
    print(df.head(15))

def plot_tweet_frequency():
    """Plots daily and hourly tweet frequency."""
    # ===== PLOT: Daily Tweet Frequency =====
    daily_path = os.path.join(BASE_PATH, 'tweet_frequency/daily_frequency')
    if os.path.exists(daily_path):
        daily_df = pd.read_csv(os.path.join(daily_path, [f for f in os.listdir(daily_path) if f.endswith('.csv')][0]))
        daily_df['tweet_date'] = pd.to_datetime(daily_df['tweet_date'])
        daily_df.sort_values('tweet_date', inplace=True)
        plt.figure(figsize=(15, 7))
        plt.plot(daily_df['tweet_date'], daily_df['count'], label='Tweets per Day', color='teal')
        plt.title('Daily Tweet Frequency', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Date', fontsize=12, fontweight='bold')
        plt.ylabel('Number of Tweets', fontsize=12, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(BASE_PATH, 'daily_tweet_frequency.png'))
        plt.show()

    # ===== PLOT: Hourly Tweet Frequency =====
    hourly_path = os.path.join(BASE_PATH, 'tweet_frequency/hourly_frequency')
    if os.path.exists(hourly_path):
        hourly_df = pd.read_csv(os.path.join(hourly_path, [f for f in os.listdir(hourly_path) if f.endswith('.csv')][0]))
        hourly_df.sort_values('hour', inplace=True)
        plt.figure(figsize=(15, 7))
        sns.barplot(x='hour', y='count', data=hourly_df, color='skyblue')
        plt.title('Hourly Tweet Frequency', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Hour of Day', fontsize=12, fontweight='bold')
        plt.ylabel('Number of Tweets', fontsize=12, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(BASE_PATH, 'hourly_tweet_frequency.png'))
        plt.show()

def plot_event_analysis():
    """Plots a bar chart of event type counts."""
    # ===== PLOT: Event Type Counts =====
    event_types = ['confirmation_tweets', 'rumor_tweets', 'transfer_tweets']
    all_events_df = []
    for event in event_types:
        try:
            path = os.path.join(BASE_PATH, event)
            if os.path.exists(path) and any(f.endswith('.csv') for f in os.listdir(path)):
                csv_file = os.path.join(path, [f for f in os.listdir(path) if f.endswith('.csv')][0])
                try:
                    # Try reading with the default (fast) C engine
                    df = pd.read_csv(csv_file)
                except pd.errors.ParserError:
                    # If the C engine fails, fall back to the more robust Python engine
                    print(f"C engine failed for {csv_file}, retrying with Python engine.")
                    df = pd.read_csv(csv_file, engine='python')

                df['event_type'] = event.replace('_tweets', '')
                all_events_df.append(df)
        except Exception as e:
            print(f"Could not process {event}: {e}")

    if all_events_df:
        combined_df = pd.concat(all_events_df, ignore_index=True)
        plt.figure(figsize=(10, 7))
        sns.countplot(x='event_type', data=combined_df)
        plt.title('Tweet Counts by Event Type', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Event Type', fontsize=12, fontweight='bold')
        plt.ylabel('Number of Tweets', fontsize=12, fontweight='bold')
        plt.savefig(os.path.join(BASE_PATH, 'event_type_counts.png'))
        plt.show()

def plot_event_engagement():
    """Plots engagement metrics for different event types."""
    # ===== PLOT: Event Engagement by Type =====
    path = os.path.join(BASE_PATH, 'events/event_engagement')
    if not os.path.exists(path) or not any(f.endswith('.csv') for f in os.listdir(path)):
        print(f"Data not found for event engagement: {path}")
        return
        
    df = pd.read_csv(os.path.join(path, [f for f in os.listdir(path) if f.endswith('.csv')][0]))
    
    # Melt the dataframe to create a long format for plotting
    df_melted = df.melt(id_vars='event_type', var_name='metric', value_name='average_value')
    
    plt.figure(figsize=(12, 8))
    sns.barplot(data=df_melted, x='event_type', y='average_value', hue='metric')
    plt.title('Average Engagement by Event Type', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Event Type', fontsize=12, fontweight='bold')
    plt.ylabel('Average Count', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45)
    plt.legend(title='Engagement Metric', fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_PATH, 'event_engagement_by_type.png'))
    plt.show()
    print("Successfully plotted event engagement.")

def plot_here_we_go_monthly():
    """Plots monthly count of 'Here We Go' tweets."""
    # ===== PLOT: Here We Go Monthly Count =====
    path = os.path.join(BASE_PATH, 'events/here_we_go_monthly_count')
    if not os.path.exists(path) or not any(f.endswith('.csv') for f in os.listdir(path)):
        print(f"Data not found for here we go monthly count: {path}")
        return
        
    df = pd.read_csv(os.path.join(path, [f for f in os.listdir(path) if f.endswith('.csv')][0]))
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m')
    df = df.sort_values('month')
    
    plt.figure(figsize=(15, 7))
    plt.plot(df['month'], df['count'], marker='o', linewidth=2, markersize=6)
    plt.title("'Here We Go' Tweets per Month", fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Month', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Tweets', fontsize=12, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_PATH, 'here_we_go_monthly_count.png'))
    plt.show()
    print("Successfully plotted here we go monthly count.")

def plot_most_active_transfer_periods():
    """Plots the most active transfer periods."""
    # ===== PLOT: Most Active Transfer Periods =====
    path = os.path.join(BASE_PATH, 'events/most_active_transfer_periods')
    if not os.path.exists(path) or not any(f.endswith('.csv') for f in os.listdir(path)):
        print(f"Data not found for most active transfer periods: {path}")
        return
        
    df = pd.read_csv(os.path.join(path, [f for f in os.listdir(path) if f.endswith('.csv')][0]))
    df['year_month'] = df['year'].astype(str) + '-' + df['month'].astype(str).str.zfill(2)
    df = df.sort_values('count', ascending=False).head(15)
    
    plt.figure(figsize=(14, 8))
    sns.barplot(data=df, x='year_month', y='count', order=df['year_month'])
    plt.title('Top 15 Most Active Transfer Months', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Year-Month', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Transfer-Related Tweets', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_PATH, 'most_active_transfer_periods.png'))
    plt.show()
    print("Successfully plotted most active transfer periods.")

def plot_co_occurrence_rules():
    """Plots a bar chart of the top co-occurrence rules by lift."""
    # ===== PLOT: Co-occurrence Rules Bar Chart =====
    path = os.path.join(BASE_PATH, 'co_occurrence/co_occurrence_rules')
    if not os.path.exists(path):
        print(f"Directory not found: {path}")
        return
        
    df = pd.read_csv(os.path.join(path, [f for f in os.listdir(path) if f.endswith('.csv')][0]))
    df['word_pair'] = df['antecedent_string'] + ' -> ' + df['consequent_string']
    
    plt.figure(figsize=(12, 8))
    sns.barplot(x='lift', y='word_pair', data=df.sort_values('lift', ascending=False), palette='viridis')
    plt.title('Top 5 Word Co-occurrence Rules by Lift', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Lift', fontsize=12, fontweight='bold')
    plt.ylabel('Word Pair', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_PATH, 'co_occurrence_rules.png'))
    plt.show()

def plot_co_occurrence_network():
    """Generates and saves a network graph of co-occurrence rules."""
    # ===== PLOT: Co-occurrence Network Graph =====
    path = os.path.join(BASE_PATH, 'co_occurrence/co_occurrence_rules')
    if not os.path.exists(path) or not any(f.endswith('.csv') for f in os.listdir(path)):
        print(f"Data not found for co-occurrence network: {path}")
        return

    try:
        df = pd.read_csv(os.path.join(path, [f for f in os.listdir(path) if f.endswith('.csv')][0]))

        # Focus on the top 5 rules for clarity
        df_top = df.nlargest(5, 'lift')
        G = nx.Graph()
        for row in df_top.itertuples(index=False):
            G.add_edge(row.antecedent_string, row.consequent_string, lift=row.lift)

        fig, ax = plt.subplots(figsize=(30, 30))
        
        components = list(nx.connected_components(G))
        if components:
            locations = {
                0: (0, 0),      # Center
                1: (-0.5, 0.1),   # Top-left
                2: (0.5, 0.1),   # Top-right
                3: (0.5, -0.1),  # Bottom-right
                4: (-0.5, -0.1),  # Bottom-left
            }
  
            pos = {}
            for i, component in enumerate(components):
                if i < len(locations) and len(component) == 2:
                    node1, node2 = list(component)
                    center_x, center_y = locations.get(i, (0,0))
                    pos[node1] = (center_x - 0.2, center_y)
                    pos[node2] = (center_x + 0.2, center_y)
  
            weights = [G[u][v]['lift'] for u, v in G.edges()]
            norm_weights = [10 * (w / max(weights)) for w in weights] if weights else [1] * len(G.edges())
  
            nx.draw(G, pos, ax=ax, with_labels=True, node_color='skyblue', node_size=6000,
                    width=norm_weights, font_size=15, edge_color='grey', font_weight='bold')
  
        ax.set_title('Word Co-occurrence Network (Top 5 Rules by Lift)', fontsize=20, fontweight='bold', pad=15)
        plt.tight_layout()
  
        plt.savefig(os.path.join(BASE_PATH, 'co_occurrence_network.png'))
        plt.show()
        print("Co-occurrence network graph generated.")
    except ImportError:
        print("\n---")
        print("Library 'networkx' not found. Please install it to generate the network graph:")
        print("pip install networkx")
        print("---\n")
    except Exception as e:
        print(f"Could not plot co-occurrence network: {e}")

if __name__ == '__main__':
    # Make sure the output directory for plots exists
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)

    print("--- Generating Visualizations ---")
    
    # Plotting functions
    plot_daily_engagement()
    plot_hourly_engagement()  # Added new hourly engagement plot
    plot_correlation_heatmap()
    plot_top_topic_words()
    plot_monthly_predictions()
    plot_tweet_frequency()
    plot_event_analysis()
    plot_event_engagement()
    plot_here_we_go_monthly()
    plot_most_active_transfer_periods()
    plot_co_occurrence_rules()
    plot_co_occurrence_network()
    
    # Display table
    display_co_occurrence_rules()

    print("\n--- Visualizations and analysis tables saved in 'output' directory ---") 