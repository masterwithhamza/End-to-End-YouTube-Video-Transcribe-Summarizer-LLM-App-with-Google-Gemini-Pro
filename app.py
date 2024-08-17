import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, VideoUnavailable, TranscriptsDisabled, CouldNotRetrieveTranscript

# Load environment variables
load_dotenv()

# Configure Google Gemini Pro API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define the prompt for summarizing YouTube transcripts
prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here: """

def extract_transcript_details(youtube_video_url):
    try:
        # Extract video ID from the YouTube URL
        video_id = youtube_video_url.split("v=")[-1].split("&")[0]
        
        # Fetch transcript text
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([entry["text"] for entry in transcript_text])

        return transcript

    except VideoUnavailable:
        st.error("This video is unavailable. Please check the video link.")
        return None
    except TranscriptsDisabled:
        st.error("Subtitles are disabled for this video. The transcript cannot be retrieved.")
        st.info("To request subtitles or check if they are available, visit the YouTube video page and check the settings.")
        return None
    except CouldNotRetrieveTranscript:
        st.error("Transcript could not be retrieved. The video might not have a transcript.")
        st.info("If you believe the video should have a transcript, consider reporting the issue at the [YouTube Transcript API GitHub repository](https://github.com/jdepoix/youtube-transcript-api/issues).")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text

    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return "Summary could not be generated."

# Streamlit app interface
st.title("YouTube Transcript to Detailed Notes Converter")

youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = youtube_link.split("v=")[-1].split("&")[0]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    if youtube_link:
        transcript_text = extract_transcript_details(youtube_link)

        if transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            st.markdown("## Detailed Notes:")
            st.write(summary)
        else:
            st.warning("Transcript could not be fetched. Please check the video link and try again.")
    else:
        st.warning("Please enter a valid YouTube video link.")

