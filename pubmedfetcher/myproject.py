#!/usr/bin/env python
# coding: utf-8

# In[180]:


import requests
import os
import re
import xml.etree.ElementTree as ET
import pandas as pd
from urllib.parse import quote
import xml.etree.ElementTree as ET
import argparse




# In[211]:


INDUSTRY_FILE = "industry_keywords.txt"


# In[212]:


DEFAULT_KEYWORDS = ["Biopharma", "Pharmaceutical", "Biotech", "Ltd", "Limited",
"Eli Lilly", "Novo Nordisk", "Johnson & Johnson", "Merck", "AbbVie", "Roche",
"AstraZeneca", "Novartis", "Pfizer", "Amgen", "Sanofi", "Bristol-Myers Squibb",
"Gilead Sciences", "Vertex Pharmaceuticals", "CVS Health", "Regeneron Pharmaceuticals",
"Zoetis", "GlaxoSmithKline", "CSL", "Merck KGaA", "Daiichi Sankyō",
"Chugai Pharmaceutical", "Takeda Pharmaceutical", "Bayer", "Seagen",
"Jiangsu Hengrui Medicine", "Biogen", "Moderna", "WuXi AppTec", "Lonza",
"Sun Pharmaceutical", "Argenx", "West Pharmaceutical", "WuXi Biologics",
"Horizon Therapeutics", "BioNTech", "Astellas Pharma", "Genmab",
"Alnylam Pharmaceuticals", "ICON plc", "Walgreens Boots Alliance", "BeiGene",
"Otsuka Holdings", "LabCorp", "Royalty Pharma", "BioMarin Pharmaceutical",
"Baxter", "UCB", "Eisai", "Celltrion"]


# In[213]:


def save_industry_keywords(keywords):
    """Saves industry keywords to a file using UTF-8 encoding."""
    try:
        with open(INDUSTRY_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(set(keywords))))  # Remove duplicates & sort
        print(f"✅ Industry keywords saved to '{INDUSTRY_FILE}'")
    except Exception as e:
        print(f"❌ Error saving file: {e}")


# In[214]:


def load_industry_keywords():
    """Loads industry keywords from a file using UTF-8 encoding."""
    if not os.path.exists(INDUSTRY_FILE):
        save_industry_keywords(DEFAULT_KEYWORDS)
    
    try:
        with open(INDUSTRY_FILE, "r", encoding="utf-8") as f:  # 🔹 Force UTF-8 encoding
            return [line.strip().lower() for line in f.readlines() if line.strip()]
    except UnicodeDecodeError as e:
        print(f"❌ Error reading file: {e}")
        return []


# In[215]:


def edit_industry_keywords():
    """Allows user to update the industry keyword list: add or remove entries."""
    keywords = load_industry_keywords()
    print(f"\n🔹 Current industry keywords: {', '.join(keywords)}")
    
    user_input = input("Enter new keywords to ADD (comma-separated) or press Enter to skip: ").strip()
    if user_input:
        keywords.extend([kw.strip().lower() for kw in user_input.split(",")])
    
    remove_input = input("Enter keywords to REMOVE (comma-separated) or press Enter to skip: ").strip()
    if remove_input:
        remove_list = set([kw.strip().lower() for kw in remove_input.split(",")])
        keywords = [kw for kw in keywords if kw not in remove_list]
    
    save_industry_keywords(keywords)
    print("✅ Updated industry keywords:", ", ".join(keywords))


# In[216]:


def construct_query(user_topic_keywords):
    """Combines user topic keywords with industry keywords for PubMed search."""
    industry_keywords = load_industry_keywords()
    industry_query = " OR ".join([f'"{word}"' for word in industry_keywords])  
    query = f"({user_topic_keywords}) AND ({industry_query})"
    return query.lower()


# In[217]:


def fetch_pubmed_ids(query, max_results=50):
    """Fetches PubMed article IDs based on the query."""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {"db": "pubmed", "term": query, "retmax": max_results, "retmode": "json"}
    response = requests.get(base_url, params=params)
    return response.json().get("esearchresult", {}).get("idlist", [])


# In[218]:


def fetch_article_details(pubmed_ids):
    """Fetches XML details for given PubMed article IDs."""
    if not pubmed_ids:
        return ""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {"db": "pubmed", "id": ",".join(pubmed_ids), "retmode": "xml"}
    response = requests.get(base_url, params=params)
    return response.text


# In[219]:


def extract_email(text):
    """Extracts emails from text."""
    return ", ".join(re.findall(r"[\w\.-]+@[\w\.-]+", text))


# In[227]:



def parse_article_details(xml_data):
    """Parses XML data to extract articles and corresponding author emails based on refined affiliation filtering."""
    root = ET.fromstring(xml_data)
    papers = []
    
    # Load industry and academic keywords
    industry_keywords = load_industry_keywords()
    industry_identifiers = {"inc", "ltd", "llc", "gmbh", "corp", "sa", "corporate", "co", "company", "srl" }
    academic_keywords = {"university", "school", "institute", "center", "centre","hospital", "education", "college", "medical", "department",
                         "national", "trust", "park", "consultant", "association", "initiative", "clinic"}

    def classify_affiliation(aff_text):
        """Classifies affiliation based on industry, academic, and identifier presence."""
        aff_lower = aff_text.lower()
        has_industry_keyword = any(word in aff_lower for word in industry_keywords)
        has_industry_identifier = any(word in aff_lower for word in industry_identifiers)
        has_academic_keyword = any(word in aff_lower for word in academic_keywords)

        # 🔹 True Positive: Industry keywords present, Industry Identifier present, No Academic Keywords
        if has_industry_keyword and has_industry_identifier and not has_academic_keyword or \
        (not has_industry_keyword and has_industry_identifier and not has_academic_keyword):
            return "True Positive"

        # 🔹 True Negative: No Industry Keywords, No Industry Identifier, Academic Keywords present
        if not has_industry_keyword and not has_industry_identifier and has_academic_keyword or \
        (not has_industry_keyword and not has_industry_identifier and not has_academic_keyword):
            return "True Negative"

        # 🔹 False Positive: Industry keywords present, No Industry Identifier, Academic Keywords present
        if has_industry_keyword and not has_industry_identifier and has_academic_keyword:
            return "False Positive"

       # 🔹 False Negative: Industry keywords present, No Industry Identifier, No Academic Keywords
       # 🔹 False Negative: No Industry Keywords, Industry Identifier present, Academic Keywords present

        if (has_industry_keyword and not has_industry_identifier and not has_academic_keyword) :
             return "False Negative"


        return "Unknown"

    for article in root.findall(".//PubmedArticle"):
        pubmed_id = article.findtext(".//PMID", default="N/A")
        title = article.findtext(".//ArticleTitle", default="N/A")
        pub_date = article.findtext(".//PubDate/Year", default="N/A")
        
        authors, industry_affiliations, all_emails, industry_emails = [], set(), [], []  # Use set() for unique affiliations
        valid_affiliation_found = False  # Track if article has at least one valid industry affiliation

        for author in article.findall(".//Author"):
            full_name = " ".join(filter(None, [
                author.findtext(".//ForeName", "").strip(),
                author.findtext(".//LastName", "").strip()
            ]))

            affiliation = author.find(".//AffiliationInfo/Affiliation")
            if affiliation is not None:
                aff_text = affiliation.text.strip()
                emails = extract_email(aff_text)

                # Classify affiliation
                affiliation_type = classify_affiliation(aff_text)

                # Track if we have a valid industry affiliation (True Positive or False Negative)
                if affiliation_type in ["True Positive", "False Negative"]:
                    valid_affiliation_found = True
                    industry_affiliations.add(aff_text)  # Store unique affiliations using set()
                    authors.append(full_name)
                    if emails:
                        industry_emails.append(emails)

                # Collect all emails
                if emails:
                    all_emails.append(emails)

        # Include only articles with at least one valid industry-affiliated author
        if valid_affiliation_found:
            papers.append({
                "PubmedID": pubmed_id,
                "Title": title,
                "Publication Date": pub_date,
                "Non-academic Author(s)": ", ".join(authors),
                "Company Affiliation(s)": ", ".join(industry_affiliations),  # Now using set() to remove duplicates
                "Corresponding Author Email": ", ".join(set(all_emails)) or "N/A"
            })

    return papers


# In[221]:


def save_to_csv(data, filename="pubmed_results.csv"):
    """Saves extracted data to a CSV file."""
    pd.DataFrame(data).to_csv(filename, index=False)
    print(f"✅ Data saved to {filename} with {len(data)} articles")


# In[228]:



def main():
    parser = argparse.ArgumentParser(description="Fetch PubMed articles based on industry-specific keywords.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode to print extra information.")
    parser.add_argument("-f", "--file", type=str, help="Specify filename to save results. If omitted, results save as 'pubmed_results.csv'.")
    args = parser.parse_args()

    industry_keywords = load_industry_keywords()
    print("\n📌 Current Industry Keywords:", ", ".join(industry_keywords))

    if input("\nDo you want to edit industry keywords? (yes/no): ").strip().lower() == "yes":
        edit_industry_keywords()
    
    # Interactive input for topic keywords
    user_topic = input("Enter your PubMed topic keywords: ").strip().lower()
    max_results = int(input("Enter the number of results to fetch: "))

    final_query = construct_query(user_topic)
    print("\n🔍 Searching PubMed with query:\n", final_query)

    pubmed_ids = fetch_pubmed_ids(final_query, max_results)
    print(f"\n📑 Found {len(pubmed_ids)} articles.")

    if pubmed_ids:
        xml_data = fetch_article_details(pubmed_ids)
        articles_data = parse_article_details(xml_data)

        # Save results based on user preference
        filename = args.file if args.file else "pubmed_results.csv"
        save_to_csv(articles_data, filename)
        print(f"✅ Results saved to {filename}")

        print("⚠️ Note: This filtering approach is not foolproof. Please review the results manually for accuracy.")
    else:
        print("❌ No relevant articles found.")

if __name__ == "__main__":
    main()

# In[ ]:




