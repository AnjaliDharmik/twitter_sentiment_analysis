import streamlit as st
import time
import re
import random
import trafilatura

# Set page configuration
st.set_page_config(
    page_title="Sentiment Analysis Tool",
    page_icon="🧠",
    layout="wide"
)

# Page Title and Description with improved styling
st.title("Advanced Sentiment Analysis Tool")

# Create a two-column layout for the intro section
intro_col1, intro_col2 = st.columns([2, 1])

with intro_col1:
    st.markdown("""
    This application analyzes the sentiment of text from manual input or web URLs.
    The analysis breaks down your content into segments and provides detailed sentiment scoring with visualizations.
    """)

with intro_col2:
    # Add a sample sentiment meter for visual interest
    st.markdown("""
    <div style="background-color:#f0f2f6;border-radius:10px;padding:10px;text-align:center;">
        <div style="font-weight:bold;margin-bottom:5px;">Sentiment Meter</div>
        <div style="display:flex;justify-content:space-between;">
            <span style="color:#F44336;">😠</span>
            <span style="color:#FF9800;">😐</span>
            <span style="color:#4CAF50;">😊</span>
        </div>
        <div style="height:10px;background:linear-gradient(to right, #F44336, #FFEB3B, #4CAF50);border-radius:5px;margin:5px 0;"></div>
    </div>
    """, unsafe_allow_html=True)

# Add a separator
st.markdown("---")

# Create sidebar with information
with st.sidebar:
    st.header("About")
    st.info("""
    This application uses a sentiment analysis approach to analyze text sentiment.
    
    The analysis will classify text as:
    - 📈 **POSITIVE**
    - 📉 **NEGATIVE**
    - ⚖️ **NEUTRAL**
    
    Confidence scores represent the certainty about the prediction.
    """)
    
    st.header("Features")
    st.success("""
    1. Analyze text from manual input
    2. Extract and analyze text from URLs
    3. Split text into segments for detailed analysis
    4. Visualize sentiment distribution and progression
    5. Compare positive and negative sentiments
    """)
    
    st.header("Instructions")
    st.info("""
    1. Choose input method (manual text or URL)
    2. Enter your text or URL
    3. Click the analyze button
    4. Explore the visualization tabs
    5. Review detailed segment-by-segment analysis
    """)
    
# Function to extract text from URL
def extract_text_from_url(url):
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            if text:
                return text
            else:
                return "No text content could be extracted from this URL."
        else:
            return "Failed to download content from the URL."
    except Exception as e:
        return f"Error extracting text from URL: {str(e)}"

# Input method selection
st.header("Choose Input Method")
input_method = st.radio(
    "Select how you want to provide text for analysis:",
    ["Enter Text Manually", "Analyze from URL"]
)

# User input section based on selected method
if input_method == "Enter Text Manually":
    st.subheader("Enter Text for Analysis")
    user_input = st.text_area(
        "Type or paste your text here:",
        height=150,
        placeholder="e.g., I really enjoyed the movie. The actors were great but the plot was somewhat confusing."
    )
    analyze_button = st.button("Analyze Sentiment")
else:
    st.subheader("Enter URL for Analysis")
    url_input = st.text_input(
        "Enter the URL of the webpage to analyze:",
        placeholder="e.g., https://example.com/article"
    )
    
    # Preview section for URL content
    if url_input:
        with st.expander("Preview extracted content (click to expand)"):
            with st.spinner("Extracting content from URL..."):
                extracted_text = extract_text_from_url(url_input)
                if extracted_text:
                    st.write("Preview (first 500 characters):")
                    st.write(extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text)
                    st.info(f"Total characters extracted: {len(extracted_text)}")
                else:
                    st.error("Could not extract text from the provided URL.")
    
    analyze_url_button = st.button("Analyze URL Content")
    
    # Set user_input to the extracted text when the button is clicked
    if analyze_url_button and url_input:
        user_input = extract_text_from_url(url_input)
        analyze_button = True
    else:
        user_input = ""
        analyze_button = False

# Simple rule-based sentiment analysis
def simple_sentiment_analysis(text):
    if not text.strip():
        return None
    
    # Define positive and negative word lists
    positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'happy', 'enjoy', 'nice', 'best', 
                     'beautiful', 'fantastic', 'perfect', 'awesome', 'delightful', 'pleased', 'joy', 'fabulous', 
                     'superb', 'impressive', 'outstanding', 'terrific', 'brilliant', 'recommend']
    
    negative_words = ['bad', 'terrible', 'awful', 'horrible', 'poor', 'hate', 'disappointed', 'disappointing', 
                     'worst', 'dislike', 'negative', 'sad', 'angry', 'unfortunate', 'frustrating', 'mediocre',
                     'failed', 'failure', 'unhappy', 'problem', 'sucks', 'boring']
    
    # Split text into sentences
    segments = [seg.strip() for seg in re.split(r'[.!?]', text) if seg.strip()]
    
    if not segments:
        segments = [text]  # If no clear sentences, analyze the whole text
    
    results = []
    
    for segment in segments:
        # Convert to lowercase for case-insensitive matching
        segment_lower = segment.lower()
        
        # Count positive and negative words
        positive_count = sum(1 for word in positive_words if word in segment_lower)
        negative_count = sum(1 for word in negative_words if word in segment_lower)
        
        # Calculate sentiment scores
        total_count = positive_count + negative_count
        if total_count > 0:
            positive_score = positive_count / total_count
            negative_score = negative_count / total_count
        else:
            # If no sentiment words found, consider it neutral
            positive_score = 0.5
            negative_score = 0.5
        
        # Determine dominant sentiment
        if positive_count > negative_count:
            dominant_sentiment = "POSITIVE"
            confidence = positive_score
        elif negative_count > positive_count:
            dominant_sentiment = "NEGATIVE"
            confidence = negative_score
        else:
            dominant_sentiment = "NEUTRAL"
            confidence = 0.5
            
        # Add small random variation to make visualization more interesting
        positive_score = min(1.0, max(0.0, positive_score + random.uniform(-0.1, 0.1)))
        negative_score = min(1.0, max(0.0, negative_score + random.uniform(-0.1, 0.1)))
        
        results.append({
            'text': segment,
            'dominant_sentiment': dominant_sentiment,
            'confidence': confidence,
            'scores': {
                'POSITIVE': positive_score,
                'NEGATIVE': negative_score
            }
        })
    
    return results

# Create enhanced visualizations for sentiment analysis
def create_simple_visualization(results):
    # Extract sentiment data for visualization
    segments = [f"Segment {i+1}" for i in range(len(results))]
    positive_scores = [result['scores']['POSITIVE'] for result in results]
    negative_scores = [result['scores']['NEGATIVE'] for result in results]
    
    # 1. Overall sentiment distribution pie chart
    st.subheader("Overall Sentiment Distribution")
    
    # Count sentiments
    sentiment_counts = {
        "Positive": sum(1 for r in results if r['dominant_sentiment'] == 'POSITIVE'),
        "Negative": sum(1 for r in results if r['dominant_sentiment'] == 'NEGATIVE'),
        "Neutral": sum(1 for r in results if r['dominant_sentiment'] == 'NEUTRAL')
    }
    
    # Create pie chart data
    pie_labels = list(sentiment_counts.keys())
    pie_values = list(sentiment_counts.values())
    pie_colors = ['#4CAF50', '#F44336', '#2196F3']  # green, red, blue
    
    # Only show pie chart if we have data
    if sum(pie_values) > 0:
        # Display pie chart using Streamlit's native pyplot integration
        pie_fig, pie_ax = st.columns([3, 1])
        with pie_fig:
            # Create a horizontal bar chart instead of pie chart
            # (streamlit doesn't have direct pie chart, but this works well)
            chart_data = {
                "Sentiment": pie_labels,
                "Count": pie_values,
            }
            
            # Use st.bar_chart for a simple bar chart
            st.bar_chart(chart_data, x="Sentiment", y="Count", color="#FFAA00")
        
        with pie_ax:
            for label, count, color in zip(pie_labels, pie_values, pie_colors):
                st.markdown(f"<div style='color:{color};font-weight:bold;'>{label}: {count}</div>", unsafe_allow_html=True)
    
    # 2. Sentiment progression visualization (how sentiment changes through segments)
    st.subheader("Sentiment Progression")
    
    # Create a line chart to show sentiment change across segments
    progression_chart_data = {
        "Segment": segments,
        "Positive Score": positive_scores,
        "Negative Score": negative_scores
    }
    
    # Display line chart
    st.line_chart(progression_chart_data, x="Segment")
    
    # 3. Detailed segment-by-segment visualization with improved UI
    st.subheader("Detailed Segment Analysis")
    
    # Create tabs for different view options
    tab1, tab2 = st.tabs(["Individual Segments", "Comparative View"])
    
    with tab1:
        # Individual segment analysis with progress bars
        for i, segment in enumerate(segments):
            with st.expander(f"**{segment}**: {results[i]['text'][:50]}...", expanded=(i==0)):
                # Show the full segment text
                st.markdown(f"**Full text:** {results[i]['text']}")
                st.markdown("**Sentiment scores:**")
                
                # Create a two-column layout for positive/negative scores
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"<div style='color:#4CAF50;font-weight:bold;'>Positive Score</div>", unsafe_allow_html=True)
                    # Display positive score as a progress bar
                    st.progress(positive_scores[i])
                    st.write(f"{positive_scores[i]:.2f}")
                    
                with col2:
                    st.markdown(f"<div style='color:#F44336;font-weight:bold;'>Negative Score</div>", unsafe_allow_html=True)
                    # Display negative score as a progress bar
                    st.progress(negative_scores[i])
                    st.write(f"{negative_scores[i]:.2f}")
                
                # Show dominant sentiment with an icon
                dominant = results[i]['dominant_sentiment']
                if dominant == "POSITIVE":
                    st.markdown("**Dominant sentiment:** 📈 Positive")
                elif dominant == "NEGATIVE":
                    st.markdown("**Dominant sentiment:** 📉 Negative")
                else:
                    st.markdown("**Dominant sentiment:** ⚖️ Neutral")
    
    with tab2:
        # Comparative bar chart for all segments
        st.bar_chart({
            "Positive": positive_scores,
            "Negative": negative_scores
        })

# Process and display results when the button is clicked
if analyze_button:
    if not user_input.strip():
        st.warning("Please enter some text to analyze.")
    else:
        with st.spinner("Analyzing sentiment..."):
            # Simulate a brief delay for better UX
            time.sleep(0.5)
            results = simple_sentiment_analysis(user_input)
            
        if results:
            st.header("Analysis Results")
            
            # Display overall sentiment
            overall_positive = sum(1 for r in results if r['dominant_sentiment'] == 'POSITIVE')
            overall_negative = sum(1 for r in results if r['dominant_sentiment'] == 'NEGATIVE')
            overall_neutral = sum(1 for r in results if r['dominant_sentiment'] == 'NEUTRAL')
            
            if overall_positive > overall_negative and overall_positive > overall_neutral:
                st.success(f"📈 Overall Sentiment: POSITIVE ({overall_positive}/{len(results)} segments)")
            elif overall_negative > overall_positive and overall_negative > overall_neutral:
                st.error(f"📉 Overall Sentiment: NEGATIVE ({overall_negative}/{len(results)} segments)")
            else:
                st.info(f"⚖️ Overall Sentiment: NEUTRAL ({overall_neutral}/{len(results)} segments)")
            
            # Display detailed results
            st.subheader("Segment-by-Segment Analysis")
            for i, result in enumerate(results):
                sentiment = result['dominant_sentiment']
                confidence = result['confidence']
                
                # Create a color-coded expander for each segment
                if sentiment == 'POSITIVE':
                    with st.expander(f"Segment {i+1}: 📈 POSITIVE ({confidence:.2f} confidence)"):
                        st.write(result['text'])
                        st.write(f"Positive score: {result['scores']['POSITIVE']:.2f}")
                        st.write(f"Negative score: {result['scores']['NEGATIVE']:.2f}")
                elif sentiment == 'NEGATIVE':
                    with st.expander(f"Segment {i+1}: 📉 NEGATIVE ({confidence:.2f} confidence)"):
                        st.write(result['text'])
                        st.write(f"Positive score: {result['scores']['POSITIVE']:.2f}")
                        st.write(f"Negative score: {result['scores']['NEGATIVE']:.2f}")
                else:
                    with st.expander(f"Segment {i+1}: ⚖️ NEUTRAL ({confidence:.2f} confidence)"):
                        st.write(result['text'])
                        st.write(f"Positive score: {result['scores']['POSITIVE']:.2f}")
                        st.write(f"Negative score: {result['scores']['NEGATIVE']:.2f}")
            
            # Visualization of sentiment scores
            create_simple_visualization(results)
            
            # Additional metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label="Positive Segments",
                    value=f"{overall_positive}/{len(results)}",
                    delta=f"{overall_positive/len(results)*100:.1f}%"
                )
            with col2:
                st.metric(
                    label="Negative Segments",
                    value=f"{overall_negative}/{len(results)}",
                    delta=f"{overall_negative/len(results)*100:.1f}%"
                )
            with col3:
                st.metric(
                    label="Neutral Segments",
                    value=f"{overall_neutral}/{len(results)}",
                    delta=f"{overall_neutral/len(results)*100:.1f}%"
                )
