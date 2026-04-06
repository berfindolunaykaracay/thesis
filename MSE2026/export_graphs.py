#!/usr/bin/env python3
"""
Export interactive HTML graphs to PNG images for presentation
"""
import subprocess
import sys

# Check if required packages are installed
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    import time
    import os

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1200,800")
    chrome_options.add_argument("--disable-gpu")

    # Initialize driver
    driver = webdriver.Chrome(options=chrome_options)

    base_path = "/Users/berfinkaracay/Desktop/Thesis/phase1/output"
    output_path = "/Users/berfinkaracay/Desktop/Thesis/MSE2026"

    graphs = [
        ("cluster_C1_graph.html", "cluster_C1_graph.png"),
        ("cluster_C2_graph.html", "cluster_C2_graph.png"),
        ("cluster_C3_graph.html", "cluster_C3_graph.png"),
        ("cluster_C4_graph.html", "cluster_C4_graph.png"),
    ]

    for html_file, png_file in graphs:
        html_path = f"file://{base_path}/{html_file}"
        png_path = f"{output_path}/{png_file}"

        print(f"Exporting {html_file}...")
        driver.get(html_path)
        time.sleep(3)  # Wait for graph to render
        driver.save_screenshot(png_path)
        print(f"  Saved to {png_path}")

    driver.quit()
    print("\nDone! All graphs exported.")

except ImportError:
    print("Selenium not installed. Please install with: pip install selenium")
    print("\nAlternatively, you can manually screenshot the graphs:")
    print("1. Open each HTML file in browser")
    print("2. Take screenshot")
    print("3. Save to MSE2026 folder")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    print("\nManual export instructions:")
    print("1. Open phase1/output/cluster_C1_graph.html in browser")
    print("2. Screenshot and save as MSE2026/cluster_C1_graph.png")
    print("3. Repeat for C2, C3, C4")
    sys.exit(1)
