# Movie_Data_Scraping_and_Sentiment_Classifier
This project scrapes movie data from Rotten Tomatoes and employs a Voting Classifier to predict audience sentiment based on features like runtime and critic score.

# Project Title: Movie Sentiment Analysis with Web Scraping and Ensemble Learning

## Description
A brief overview of your project.

*This project first scrapes movie data from Rotten Tomatoes using Python, Selenium, and BeautifulSoup. It then preprocesses this data and employs a Voting Classifier (combining Logistic Regression, Random Forest, and SVC with GridSearchCV) to predict audience sentiment based on features like movie runtime and critic scores.*


## Features
List the main capabilities of your project.
* **Web Scraping:**
    * Collects detailed movie information from Rotten Tomatoes.
    * Scrapes fields including title, summary, director, producer, screenwriter, rating, genre, language, release date, box office gross, runtime, critic score, and audience score.
    * Handles pagination and lazy loading on the Rotten Tomatoes website.
    * Saves scraped data to a CSV file (`movies.csv`) in a `dataset/` directory.
* **Data Preprocessing:**
    * Loads data from the CSV file.
    * Handles missing values in `audience_score`, `critic_score`, and `runtime` by dropping rows.
    * Binarizes `audience_score` into an `audience_sentiment` (1 if score >= 50, else 0) for classification.
* **Sentiment Prediction:**
    * Uses `runtime` and `critic_score` as features to predict `audience_sentiment`.
    * Employs an ensemble learning model: `VotingClassifier`.
    * The Voting Classifier combines `LogisticRegression`, `RandomForestClassifier`, and `SVC` (Support Vector Classifier).
    * Utilizes `GridSearchCV` for hyperparameter tuning of the ensemble model to find the best parameters and improve accuracy.
* **Model Evaluation:**
    * Splits data into training and testing sets (75/25 split).
    * Reports the test accuracy of the best estimator found by GridSearchCV.
    * Prints the best hyperparameters found for the combined model.

## Technologies Used
* **Python 3.12**
* **Web Scraping & Data Handling:**
    * `Selenium`: For web browser automation to handle dynamic content.
    * `BeautifulSoup4`: For parsing HTML content.
    * `requests`: For making HTTP requests (used as a fallback or initial fetch in `get_scraper`).
    * `Pandas`: For data manipulation and creating DataFrames, and CSV export/import.
    * `re` (Regular Expressions): For parsing text like scores, runtime, rating, release date, and gross.
* **Machine Learning (Scikit-learn):**
    * `train_test_split`: For splitting data.
    * `GridSearchCV`: For hyperparameter tuning.
    * `VotingClassifier`: For ensembling models.
    * `RandomForestClassifier`: Base estimator.
    * `LogisticRegression`: Base estimator.
    * `SVC`: Base estimator.
    * `accuracy_score`: For model evaluation.
* **Standard Libraries:**
    * `datetime`: For parsing release dates.
    * `os`: For directory creation.
    * `time`: For adding delays during scraping.
