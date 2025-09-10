import streamlit as st
import queue
import threading
import time
from scraper import WebScraper

st.set_page_config(page_title="Web Scraper UI", layout="wide")

st.title("🚀 Enhanced Web Scraper UI")
st.write("Enter the details below to start scraping a website.")

with st.form(key='scraper_form'):
    url = st.text_input("Enter the starting URL", "https://docs.python.org/3/")

    col1, col2, col3 = st.columns(3)
    with col1:
        depth = st.number_input("Crawl Depth", min_value=0, max_value=10, value=2)
    with col2:
        threads = st.number_input("Number of Threads", min_value=1, max_value=50, value=5)
    with col3:
        delay = st.number_input("Delay (seconds)", min_value=0.0, max_value=10.0, value=1.0, step=0.1)

    user_agent = st.text_input("User-Agent", "EnhancedScraper/1.0 (Streamlit UI)")
    vectorize = st.checkbox("Generate text embeddings (vectorize)?")

    submit_button = st.form_submit_button(label='✨ Start Scraping')

if submit_button:
    if not url:
        st.error("Please enter a URL to start scraping.")
    else:
        st.subheader("📝 Live Log")
        log_container = st.empty()
        all_logs = []
        log_container.text_area("Live Log Output", value="", height=300, disabled=True)

        log_queue = queue.Queue()

        scraper = WebScraper(
            base_url=url, depth_limit=depth, threads=threads, delay=delay,
            user_agent=user_agent, vectorize=vectorize, log_queue=log_queue
        )

        crawl_thread = threading.Thread(target=scraper.crawl)
        crawl_thread.start()

        while crawl_thread.is_alive():
            try:
                log_message = log_queue.get_nowait()
                all_logs.append(log_message)
                log_container.text_area(
                    "Live Log Output", 
                    value='\n'.join(all_logs), 
                    height=300, 
                    disabled=True
                )
            except queue.Empty:
                time.sleep(0.1)

        while not log_queue.empty():
            log_message = log_queue.get()
            all_logs.append(log_message)
        
        log_container.text_area(
            "Live Log Output", 
            value='\n'.join(all_logs), 
            height=300, 
            disabled=True
        )

        st.success("Scraping complete!")

        json_result, log_result = scraper.get_results()

        tab1, tab2, tab3 = st.tabs(["📊 Summary & Downloads", "📄 Scraped Data (JSON)", "📜 Navigation Log (TXT)"])
        with tab1:
            st.write(f"Found and scraped **{len(scraper.scraped_data)}** pages.")
            st.write("Use the buttons below to download the full results.")
            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                st.download_button(
                    label="📥 Download Scraped Data (JSON)", data=json_result,
                    file_name="scraped_data.json", mime="application/json", use_container_width=True
                )
            with dl_col2:
                st.download_button(
                    label="📥 Download Navigation Log (TXT)", data=log_result,
                    file_name="scraped_log.txt", mime="text/plain", use_container_width=True
                )
        with tab2:
            st.json(scraper.scraped_data, expanded=False)
        with tab3:
            st.code(log_result)