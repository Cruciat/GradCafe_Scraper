# GradCafe Scraper

**GradCafe Scraper** is a command-line tool written in Python that automatically extracts admission decision data from [The GradCafe](https://www.thegradcafe.com/survey/). It uses `requests` and `BeautifulSoup` to navigate and parse result pages, and saves the collected data into a structured CSV file.

---

## Main Features

* **Parametric search**: filters by institution, program, and degree type.
* **Automatic pagination**: navigates through all result pages and handles pagination dynamically.
* **Detailed extraction**: extracts school, program, study level, submission date, decision, GPA and GRE scores (V, Q, AW), plus any comments.
* **Interactive status bar**: displays a colored progress bar with percentage, current page, and number of entries collected.
* **CSV output**: saves data into a CSV file automatically named based on parameters and execution date.

---

## Requirements

* Python 3.7 or higher  
* Internet connection

The program requires the following Python libraries (installable via `requirements.txt`):

```text
requests>=2.0
beautifulsoup4>=4.0
pyfiglet>=0.8
colorama>=0.4
```

---

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/your-username/gradcafe-scraper.git
   cd gradcafe-scraper
   ```

2. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

Run the script from terminal:

```bash
python gradcafe_scraper.py
```

Follow the interactive prompts:

1. Enter the name of the institution (leave blank for no filter).
2. Enter the program name (leave blank for no filter).
3. Select the degree type from the menu.

The tool will display a summary of your input and start downloading the result pages; you'll see a progress bar. When done, you'll find the generated CSV in:

```
CSVs/GradCafe/<institution>_<program>_<degree>_<DDMMYYYY>.csv
```

---

## CSV Structure

The CSV file will contain the following columns:

| Column   | Description                                |
| -------- | ------------------------------------------ |
| School   | Institution name                           |
| Program  | Program name                               |
| Level    | Level of study (e.g., PhD, Masters, etc.)  |
| Added on | Submission date                            |
| Decision | Decision outcome (first word only)         |
| GPA      | Reported GPA                               |
| GRE V    | GRE Verbal score                           |
| GRE Q    | GRE Quantitative score                     |
| GRE AW   | GRE Analytical Writing score               |
| Comment  | Any additional comment                     |

### Example CSV row

```
MIT,Computer Science,PhD,March 15,2024,Accepted,3.9,160,170,5.0,"Excited to join!"
```

---

## Sample Dataset

In the `csv_output` folder, you’ll find two sample datasets previously extracted, based on master’s programs of personal interest. These CSV files can be used as a reference for the data structure or to test analyses without having to run the scraper right away.

---

## Customization

* You can adjust the sleep interval (currently 0.5 s) to balance speed and server load.
* The user agent is configured in the `headers` variable; feel free to change it if needed.

---

## Contributions

Contributions are welcome! Feel free to open a pull request or report an issue for bugs or feature suggestions.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

*Last updated: July 2, 2025*
