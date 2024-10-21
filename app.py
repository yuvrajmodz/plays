from flask import Flask, jsonify
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import os

app = Flask(__name__)

# Function to extract data using Playwright and BeautifulSoup
def extract_data_from_number(phone_number):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Launch browser
        page = browser.new_page()

        # Go to the number input page
        page.goto("https://getno.site/number/index.html")

        # Fill the phone number in the input field
        page.fill("input#mobileNumber", phone_number)

        # Click the "PROCEED" button
        page.click("button[onclick='submitForm()']")

        # Wait for the page to redirect to the result page
        page.wait_for_url("https://getno.site/number/result.html")

        # Get the page content after redirection
        content = page.content()

        # Close the browser
        browser.close()

        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Find the <pre> tag that contains the JSON data
        json_data = soup.find('pre', id='jsonData')

        if json_data:
            # Parse the JSON data
            extracted_data = eval(json_data.text)

            # Extract relevant information
            your_number = extracted_data.get("your number", "")
            passkey = extracted_data.get("passkey", "")
            bildbiska = extracted_data.get("bildbiska", "")

            return {
                "your_number": your_number,
                "passkey": passkey,
                "bildbiska": bildbiska
            }

        return None

@app.route('/<phone_number>', methods=['GET'])
def get_phone_details(phone_number):
    try:
        # Extract data for the given phone number
        result = extract_data_from_number(phone_number)
        if result:
            return jsonify(result)
        else:
            return jsonify({"error": "Data not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5015))
    app.run(host='0.0.0.0', port=port, debug=True)