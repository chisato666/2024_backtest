from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize the webdriver (replace 'path/to/chromedriver' with the actual path to your Chrome driver)
driver = webdriver.Chrome('path/to/chromedriver')

# Navigate to the webpage
driver.get('https://example.com')

# Wait for the button to be present and visible
wait = WebDriverWait(driver, 10)
button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.ModelSelect_selectNoneOfThese__QF7Xw[tabindex='0']")))

# Click the button
button.click()

# Close the browser
driver.quit()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize the webdriver (replace 'path/to/chromedriver' with the actual path to your Chrome driver)
driver = webdriver.Chrome('path/to/chromedriver')

# Navigate to the webpage
driver.get('https://example.com')

# Wait for the element to be present and visible
wait = WebDriverWait(driver, 10)
element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.styles_dropDownItem__title__jSeF6")))

# Click the element
element.click()

# Close the browser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize the webdriver (replace 'path/to/chromedriver' with the actual path to your Chrome driver)
driver = webdriver.Chrome('path/to/chromedriver')

# Navigate to the webpage
driver.get('https://example.com')

# Wait for the element with the exact text to be present and visible
wait = WebDriverWait(driver, 10)
element = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'styles_dropDownItem__title__jSeF6') and text()='Very good condition']")))

# Click the element
element.click()

# Close the browser
driver.quit()


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize the Chrome driver
driver = webdriver.Chrome()

# Navigate to the webpage
driver.get("https://example.com")

# Find the element with data-component-id="model"
data_component_id = "model"
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, f"[data-component-id='{data_component_id}']"))
)

# Click the element
element.click()

# Close the browser
driver.quit()

from selenium import webdriver
from selenium.webdriver.common.by import By

# Initialize the webdriver (replace 'path/to/chromedriver' with the actual path to your Chrome driver)
driver = webdriver.Chrome('path/to/chromedriver')

# Navigate to the webpage
driver.get('https://example.com')

# Locate the button element using its attributes
button = driver.find_element(By.CSS_SELECTOR, 'button.vc-btn.vc-btn--primary.vc-btn--medium.vc-btn--full')

# Click the button
button.click()

# Close the browser
driver.quit()

from selenium import webdriver
from selenium.webdriver.common.by import By

# Initialize the webdriver (replace 'path/to/chromedriver' with the actual path to your Chrome driver)
driver = webdriver.Chrome('path/to/chromedriver')

# Navigate to the webpage
driver.get('https://example.com')

# Locate the span element using its class attribute
span = driver.find_element(By.CSS_SELECTOR, 'span.styles_dropDownItem__title__jSeF6')

# Click the span element
span.click()

# Close the browser
driver.quit()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize the webdriver (replace 'path/to/chromedriver' with the actual path to your Chrome driver)
driver = webdriver.Chrome('path/to/chromedriver')

# Navigate to the webpage
driver.get('https://example.com')

# Wait up to 10 seconds for the element to be present
wait = WebDriverWait(driver, 10)
span = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.styles_dropDownItem__title__jSeF6')))

# Click the span element
span.click()

# Close the browser
driver.quit()