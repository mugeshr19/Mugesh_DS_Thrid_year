"""
Capture high-resolution screenshots of all major web dashboard tabs using headless Chrome
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

os.makedirs("outputs/figures", exist_ok=True)

options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1440,920")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)
driver.get("http://localhost:5173")
time.sleep(3)

# 1. Overview
driver.save_screenshot("outputs/figures/dashboard_overview_screenshot.png")
print("Saved dashboard_overview_screenshot.png")

# 2. Live Monitoring
driver.find_element(By.ID, "nav-btn-monitoring").click()
time.sleep(2)
driver.save_screenshot("outputs/figures/dashboard_monitoring_screenshot.png")
print("Saved dashboard_monitoring_screenshot.png")

# 3. Traffic Map
driver.find_element(By.ID, "nav-btn-map").click()
time.sleep(3)
driver.save_screenshot("outputs/figures/dashboard_map_screenshot.png")
print("Saved dashboard_map_screenshot.png")

# 4. Prediction Center
driver.find_element(By.ID, "nav-btn-prediction").click()
time.sleep(2)
driver.save_screenshot("outputs/figures/dashboard_prediction_screenshot.png")
print("Saved dashboard_prediction_screenshot.png")

driver.quit()
print("All screenshots successfully captured!")
