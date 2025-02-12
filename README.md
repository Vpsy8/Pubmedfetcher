                                       ** PubMed Fetcher**
A tool to fetch biotech and biopharma industry-affiliated research articles based on user-defined keywords

1. Overview
This Python script retrieves PubMed articles based on user-defined keywords and filters authors' affiliations to identify industry-associated research. It uses PubMed's Entrez API to fetch articles. The script retains only articles with at least one industry-affiliated author by filtering author affiliations using industry identifiers, industry keywords, and academic keywords to classify affiliations.
Note: Refer to the script for Industry Keywords, Industry Identifiers, and Academia Keywords.

2. Features:
Command-line Execution: Provides an executable command named get-papers-list via Poetry
Supports options: 
-h / --help: Display usage instructions
o	-d / --debug: Print debug information during execution
o	-f / --file: Specify the filename to save results

Interactive Prompts
•	Allows users to append or delete default industry keywords
•	Accepts user-defined search terms (MeSH) and number of articles to retrieve

PubMed Search Integration
•	Constructs search queries combining user-defined keywords with industry-specific terms
 Author Affiliation Filtering
•	Uses a classification system to differentiate industry and academic affiliations

 Data Extraction & Storage
•	Extracts PMID, Title, Year, Authors, Company, and Corresponding Emails
•	Saves results as CSV 

3.	Requirements
•	Python >=3.9
•	Required Libraries (installed via Poetry): 
•	requests
•	os
•	re
•	xml.etree.ElementTree
•	pandas
•	argparse

4.  Installation 
Run in command prompt:
Clone the GitHub Repository: git clone https://github.com/Vpsy8/Pubmedfetcher.git
Install Poetry (If Not Installed): pip install poetry
Install Dependencies: poetry install
Run the Executable Command: poetry run get-papers-list

5.	Functionality Workflow
Fetch and Filter PubMed Articles:
•	Retrieves PubMed article IDs matching the query.
•	Extracts metadata, classifies author affiliations (Industry vs. Academia).
•	Retains only articles with at least one industry-affiliated author.

Extract & Store Data:
•	Parses title, year, authors, company, and corresponding emails.
•	Saves results in a CSV file at the user-defined directory.

Key Functions in the Script
•	save_industry_keywords() → Saves industry keyword list.
•	load_industry_keywords() → Loads industry keywords from industry_keywords.txt.
•	construct_query() → Builds a PubMed search query.
•	fetch_pubmed_ids() → Retrieves PubMed article IDs.
•	fetch_article_details() → Fetches XML metadata for articles.
•	extract_email() → Extracts emails from author affiliation text.
•	parse_article_details() → Classifies affiliations & extracts author details.

Example Usage
poetry run get-papers-list -f myresults.csv

Displays Current Industry Keywords

Do you want to edit industry keywords? (Yes/No): Yes 

Enter new keywords to ADD (comma-separated) or press Enter to skip: lupin

Enter new keywords to REMOVE (comma-separated) or press Enter to skip: (skipped)

Displays Updated Keywords

Enter your PubMed topic keyword: "Diabetes Mellitus"[MeSH]

Enter the number of results to be fetched: 100

Output Messages
Found 100 articles  
Data saved to myresults.csv with 15 articles  
Note: This filtering approach is not foolproof. Please review the results

Output Example
PubMed ID: 39932572  
Title: Association between erythrocyte polyunsaturated fatty acids and gestational diabetes mellitus in Chinese pregnant women. 
Year: 2025
Non-Academic Authors: Jinjing Zhong, Xiaoling Zeng
Company: Hyproca Nutrition Co., Ltd, Changsha, 410000, China., Ausnutria Dairy (China) Co., Ltd, Changsha, Hunan Province, 410219, China.
Corresponding Email: caili5@mail.sysu.edu.cn., fengzhao21c@163.com.  

Contributing & Contact
For issues or improvements, feel free to contribute or report bugs.
vipulwagh31@gmail.com


