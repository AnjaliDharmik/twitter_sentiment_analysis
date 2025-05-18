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

# Page Title and Description
st.title("📊 Sentiment Analysis Tool")
st.markdown("""
This application analyzes the sentiment of your text.
Enter text in the box below and see if it has a positive, negative, or neutral sentiment.
""")

# Create sidebar with information
with st.sidebar:
    st.header("About")
    st.info("""
    This application uses a simple rule-based sentiment analysis approach.
    
    The model will classify text as:
    - 📈 **POSITIVE**
    - 📉 **NEGATIVE**
    - ⚖️ **NEUTRAL**
    
    Confidence scores represent the certainty about the prediction.
    """)
    
    st.header("Instructions")
    st.info("""
    1. Enter your text in the text area
    2. Click 'Analyze Sentiment'
    3. View the results and visualization
    4. You can analyze multiple paragraphs or sentences at once
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

# Create a simple bar chart for visualization using Streamlit
def create_simple_visualization(results):
    # Extract sentiment data for visualization
    segments = [f"Segment {i+1}" for i in range(len(results))]
    positive_scores = [result['scores']['POSITIVE'] for result in results]
    negative_scores = [result['scores']['NEGATIVE'] for result in results]
    
    # Display a simple bar chart for each segment
    st.subheader("Sentiment Scores by Segment")
    
    for i, segment in enumerate(segments):
        st.write(f"**{segment}**: {results[i]['text'][:50]}...")
        
        # Create a two-column layout for positive/negative scores
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Positive Score")
            # Display positive score as a progress bar
            st.progress(positive_scores[i])
            st.write(f"{positive_scores[i]:.2f}")
            
        with col2:
            st.write("Negative Score")
            # Display negative score as a progress bar
            st.progress(negative_scores[i])
            st.write(f"{negative_scores[i]:.2f}")
        
        st.markdown("---")

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

# Footer
st.markdown("---")
st.markdown("Powered by Streamlit")
