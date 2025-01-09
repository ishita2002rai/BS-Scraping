# BS-Scraping
This project automates tasks related to the **El País** news website, including scraping articles from the Opinion section, translating their titles to English, analyzing repeated words, and performing cross-browser testing using BrowserStack.

---

## Features

### 1. **Scrape Articles**
- Fetches the first 5 articles from the Opinion section of El País.
- Extracts the following information for each article:
  - **Title** (in Spanish)
  - **Content** (in Spanish)
  - **Cover image** (gets saved locally, if available).

### 2. **Translate Article Titles**
- Use the Google Translate API to translate article titles from Spanish to English.
- Save the translated titles for analysis.

### 3. **Analyze Translated Headers**
- Identify repeated words (appearing more than twice) across all translated titles.
- Display the repeated words along with their occurrence counts.

### 4. **Cross-Browser Testing**
- Verify functionality across multiple browsers and devices using BrowserStack.

---

## Installation

### Prerequisites
- **Python 3.x**
- Required Python packages:
  ```bash
  pip install requests beautifulsoup4 googletrans selenium

