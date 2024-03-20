import os
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

def extract_species(description):
    print(description)
    pattern = r'^(?:\S+\s+)(.*?)\s*(?:chromosome|DNA|Scaffold*|NODE*|contig*)'
    match = re.search(pattern, description)
    if match:
        species_name = re.sub(r'\b(species|strain)\b', '', match.group(1)).strip()
        return species_name
    else:
        return None
        
def scrape_genome_data(organism):
    """
    Scrapes genome data from NCBI Assembly for the given organism.

    Args:
    - organism (str): The full organism name to use for the search.

    Returns:
    - DataFrame: DataFrame containing the scraped genome data.
    """
    # Define the pattern to match species and strain
    pattern = r"(.+)\s(\w+)\s(\d+)"
    
    # Match the pattern in the text
    organism_split = re.match(pattern, organism)
    
    if organism_split:
        species = organism_split.group(1)
        strain = organism_split.group(2) + " " + organism_split.group(3)
        print("Species:", species)
        print("Strain:", strain)
    else:
        print("Pattern not found in text.")

    genbank = None
    refseq = None
    # Open a Chrome browser
    driver = webdriver.Chrome()
    
    try:
        # Construct the search URL for assembly
        search_url = f"https://www.ncbi.nlm.nih.gov/assembly/?term={organism.replace(' ', '+')}"
    
        # Navigate to the search URL
        driver.get(search_url)
    
        # Find elements containing the organism name
        elements_1 = driver.find_elements(By.XPATH, "//*[contains(text(), 'JCM 5058')]")
        # Find elements containing both "Streptomyces anthocyanicus" and "JCM 5058"
        #elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Streptomyces anthocyanicus') and contains(text(), 'JCM 5058')]")

    
        elements_2 = driver.find_elements(By.XPATH, "//*[contains(text(), 'NCBI RefSeq assembly')]")#{search_term}
    
        if elements_1:
            print(f"{organism}' found on the webpage.")
            # Loop through elements containing the organism name
            for element in elements_1:
                # Find the parent element of the matched element
                parent_element = element.find_element(By.XPATH, "..")
                # Find the GenBank assembly accession element within the parent element
                genbank_element = parent_element.find_element(By.XPATH, "//dl[contains(., 'JCM 5058')]/following-sibling::dl[6]")
                RefSeq_element = parent_element.find_element(By.XPATH, "//dl[contains(., 'JCM 5058')]/following-sibling::dl[7]")
                genbank = genbank_element.text.split(": ")[1].replace(" (latest)", "")
                refseq = RefSeq_element.text.split(": ")[1].replace(" (latest)", "")
                print("GenBank assembly accession:", genbank)
                print("RefSeq assembly accession:", refseq)
                break
            
       
        elif elements_2:
            print(f"{organism}' found on the webpage.")
            # Loop through elements containing the organism name
            for element in elements_2:
                # Find the parent element of the matched element
                parent_element = element.find_element(By.XPATH, "..") # for sibling"following-sibling::*[1]" #for parents ".." and for grand parents "../.." 
                genbank = parent_element.find_element(By.XPATH, ".//dt[contains(text(), 'Submitted GenBank assembly')]/following-sibling::dd[1]").text.strip()
                refseq = parent_element.find_element(By.XPATH, ".//dt[contains(text(), 'NCBI RefSeq assembly')]/following-sibling::dd[1]").text.strip()
                print("GenBank assembly accession:", genbank)
                print("RefSeq assembly accession:", refseq)
                  
        else:
            print(f"{organism} not found on the webpage.")
    
    except Exception as e:
        print("An error occurred:", e)
    
    finally:
        # Quit the browser
        driver.quit()# Create a DataFrame
    data = [{"Organism": organism, "GenBank Accession Number": genbank, "RefSeq assembly accession": refseq}]
    df = pd.DataFrame(data)

    return df
    
# Example usage:
folder_path = "MDU_10_genome_2"
# Initialize an empty list to store DataFrame
genome_data_dfs = []

for filename in os.listdir(folder_path):
    if filename.endswith(('.fna', '.fasta')):
        full_path = os.path.join(folder_path, filename)
        
        # Open the file
        with open(full_path, 'r') as file:
            # Read the description line (usually the first line)
            description = file.readline().strip()

            # Extract the species
            species = extract_species(description)
            print("Species", species, "is being scraped from NCBI")

            # Scrape genome data
            genome_data_df = scrape_genome_data(species)
            
            # Append the DataFrame to the list
            genome_data_dfs.append(genome_data_df)

# Concatenate all DataFrames in the list into a single DataFrame
result_df = pd.concat(genome_data_dfs, ignore_index=True)

# Write the result to a CSV file
result_df.to_csv("genome_data_results.csv", index=False)