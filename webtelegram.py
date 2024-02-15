name: login webtelegram

on:
  schedule:
    - cron: '5 * */10 * *'
  workflow_dispatch:
    inputs:
      branch:
        description: 'Branch to run the workflow on'
        required: true
        default: 'main'

jobs:
  send-message:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v2
      - name: Cache Chrome and ChromeDriver
        id: cache-chrome
        uses: actions/cache@v3
        with:
          path: |
            google-chrome-stable_current_amd64.deb
            chromedriver_linux64.zip
            /usr/local/bin/chromedriver
          key: ${{ runner.os }}-chrome-cache-${{ hashFiles('google-chrome-stable_current_amd64.deb') }}-${{ hashFiles('chromedriver_linux64.zip') }}-${{ hashFiles('/usr/local/bin/chromedriver') }}
      - name: Get cache size
        id: cache-size
        run: |
          cache_size=$(du -sh $GITHUB_WORKSPACE | awk '{print $1}')
          echo "Cache size: $cache_size"
          echo "size=$cache_size" >> $GITHUB_ENV
      - name: Clear cache if size > 1GB
        if: steps.cache-size.outputs.size >= '1G'
        run: |
          echo "Cache size is greater than 1GB. Clearing cache..."
          actions/cache@v3
          with:
            path: |
              google-chrome-stable_current_amd64.deb
              chromedriver_linux64.zip
              /usr/local/bin/chromedriver
            key: ${{ runner.os }}-chrome-cache-${{ hashFiles('google-chrome-stable_current_amd64.deb') }}-${{ hashFiles('chromedriver_linux64.zip') }}-${{ hashFiles('/usr/local/bin/chromedriver') }}
            restore-keys: |
              ${{ runner.os }}-chrome-cache-
      - name: Install Chrome
        if: steps.cache-chrome.outputs.cache-hit != true
        run: |
          wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
          sudo dpkg -i google-chrome-stable_current_amd64.deb
      - name: Install ChromeDriver
        if: steps.cache-chrome.outputs.cache-hit != true
        run: |
          curl -fsSL https://chromedriver.storage.googleapis.com/121.0.6167.184/chromedriver_linux64.zip -o chromedriver_linux64.zip
          unzip chromedriver_linux64.zip
          sudo mv chromedriver /usr/local/bin/chromedriver
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install Dependencies
        run: |
          pip install selenium
          pip install requests
      - name: Build web
        run: |
          python webtelegram.py
