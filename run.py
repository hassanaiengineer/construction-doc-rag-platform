import uvicorn
import subprocess
import threading
import sys
import os
import time

def run_streamlit():
    """Run the Streamlit application as a subprocess."""
    print("Starting Streamlit UI on http://localhost:8501")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless=true"])

def main():
    """Run both the FastAPI backend and Streamlit frontend concurrently."""
    
    # Start Streamlit in a separate thread
    st_thread = threading.Thread(target=run_streamlit, daemon=True)
    st_thread.start()
    
    # Wait a moment to ensure ports don't clash on startup output
    time.sleep(2)
    
    # Run FastAPI using uvicorn in the main thread
    print("Starting FastAPI Backend on http://localhost:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main()
