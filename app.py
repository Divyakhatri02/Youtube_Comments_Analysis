import streamlit as st
import os
import time
from Senti import extract_video_id, analyze_sentiment, bar_chart, plot_sentiment, show_wordcloud
from YoutubeCommentScrapper import save_video_comments_to_csv, get_channel_info, youtube, get_channel_id, get_video_stats

def delete_non_matching_csv_files(directory_path, video_id):
    for file_name in os.listdir(directory_path):
        if not file_name.endswith('.csv'):
            continue
        if file_name == f'{video_id}.csv':
            continue
        os.remove(os.path.join(directory_path, file_name))


st.set_page_config(page_title='Divya Khatrii', page_icon='app_logo.png', initial_sidebar_state='auto')
st.sidebar.title("Sentimental Analysis")
st.sidebar.header("Enter YouTube Link")
youtube_link = st.sidebar.text_input("Link")
submit_button = st.sidebar.button("Submit")

directory_path = os.getcwd()

# 🎨 Custom CSS
custom_css = """
<style>
[data-testid="stAppViewContainer"] {
    background: #ffffff;
    background: radial-gradient(circle, rgba(255, 255, 255, 1) 0%, rgba(252, 232, 232, 1) 70%);
}
[data-testid="stSidebar"] {
    background: #dedeff;
    background: radial-gradient(circle, rgba(222, 222, 255, 1) 0%, rgba(250, 220, 220, 1) 34%);
    font-weight: 600;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
h1, h2, h3, h4, h5, h6 {
    font-family: 'Segoe UI', sans-serif;
    color: #3b0764;
    font-weight: bold;
    text-shadow: 0 1px 1px rgba(0,0,0,0.1);
}
.css-1v0mbdj p {
    color: #333333;
    font-size: 16px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

if youtube_link and submit_button:
    try:
        # 🍪 Cute baking animation
        loading_box = st.empty()
        emojis = ["🍪", "🍩", "🧁", "🎂", "🍰", "🍕"]
        message = "Baking your link, please wait"

        for i in range(12):  # ~6 seconds total
            emoji = emojis[i % len(emojis)]
            loading_html = f"""
            <div style="text-align:center; padding-top: 100px;">
                <div style="font-size: 80px;">{emoji}</div>
                <div style="font-size: 24px; font-weight: bold;">{message}</div>
            </div>
            """
            loading_box.markdown(loading_html, unsafe_allow_html=True)
            time.sleep(0.5)

        loading_box.empty()

        # 🎯 Start processing after animation
        video_id = extract_video_id(youtube_link)
        if not video_id:
            st.sidebar.error("❌ Could not extract video ID from the link.")
            st.stop()

        channel_id = get_channel_id(video_id)
        if not channel_id:
            st.sidebar.error("❌ Could not fetch channel ID.")
            st.stop()

        csv_file = save_video_comments_to_csv(video_id)
        delete_non_matching_csv_files(directory_path, video_id)
        st.sidebar.success("✅ Comments saved to CSV!")
        st.sidebar.download_button(
            label="Download Comments",
            data=open(csv_file, 'rb').read(),
            file_name=os.path.basename(csv_file),
            mime="text/csv"
        )

        # Fetching Channel Info
        channel_info = get_channel_info(youtube, channel_id)

        col1, col2 = st.columns(2)
        with col1:
            st.image(channel_info['channel_logo_url'], width=250)
        with col2:
            st.text("YouTube Channel Name")
            st.title(channel_info['channel_title'])

        st.markdown("---")

        col3, col4, col5 = st.columns(3)
        with col3:
            st.header("Total Videos")
            st.subheader(channel_info['video_count'])

        with col4:
            st.header("Channel Created")
            st.subheader(channel_info['channel_created_date'][:10])

        with col5:
            st.header("Subscriber Count")
            st.subheader(channel_info["subscriber_count"])

        stats = get_video_stats(video_id)

        st.title("Video Information")
        col6, col7, col8 = st.columns(3)
        with col6:
            st.header("Total Views")
            st.subheader(stats["viewCount"])
        with col7:
            st.header("Like Count")
            st.subheader(stats["likeCount"])
        with col8:
            st.header("Comment Count")
            st.subheader(stats["commentCount"])

        st.video(data=youtube_link)

        results = analyze_sentiment(csv_file)

        col9, col10, col11 = st.columns(3)
        with col9:
            st.header("Positive Comments")
            st.subheader(results['num_positive'])
        with col10:
            st.header("Negative Comments")
            st.subheader(results['num_negative'])
        with col11:
            st.header("Neutral Comments")
            st.subheader(results['num_neutral'])

        bar_chart(csv_file)
        plot_sentiment(csv_file)


        st.title("Sentiment Word Cloud Viewer")
        show_wordcloud(csv_file)
        
        
        st.subheader("Channel Description")
        st.write(channel_info['channel_description'])

    except Exception as e:
        st.error("⚠️ An unexpected error occurred while processing the video.")
        st.exception(e)