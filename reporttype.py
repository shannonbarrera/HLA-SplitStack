"""
python 3.13

Determines the type of HLA Fusion report contained in a PDF file.

This script scans the first page of a PDF report and identifies:
- Whether it is a PRA or SAB report.
- Whether it is Class I or Class II (or both).

Returns a string identifier such as "PRA C1", "PRA C2", "SAB C1", or "SAB C2"
that can be used for downstream report splitting and labeling.

Usage:
    Can be run standalone with a filepath argument or imported as a module.

Dependencies:
    - pypdf

By: Shannon Barrera
Date: 4/9/25
"""

import pypdf

def main(pdf_filepath, firstpage=0):
    """
    Determines the report type from a given PDF file.

    The function reads the text from a specified page (default is the first page)
    and identifies whether the report is a LABScreen PRA or LABScreen Single Antigen (SAB),
    and whether it is Class I (C1) or Class II (C2).

    Args:
        pdf_filepath (str): Path to the PDF report file.
        firstpage (int, optional): Page index to examine. Defaults to 0.

    Returns:
        str: One of the following report types:
             - "PRA C1"
             - "PRA C2"
             - "SAB C1"
             - "SAB C2"
        Returns None if the report type cannot be determined.
    """
    pra = False
    sab = False
    c1 = False
    c2 = False 
    with open(pdf_filepath, 'rb') as file:
        reader = pypdf.PdfReader(file)
        page = reader.pages[firstpage]
        text = page.extract_text()
        if text:
            lines = text.splitlines()
            if "LABScreen PRA Bead Report" in lines[0]:
                pra = True
            if "LABScreen Single Antigen" in lines[0]:
                sab = True
            classtwo = 0
            for line in lines:
                if "Class II" in line:
                    classtwo += 1

    if classtwo >= 2:
        c2 = True
    else:
        c1 = True

    if pra == True:
        if c1 == True:
            return "PRA C1"
        if c2 == True:
            return "PRA C2"
    if sab == True:
        if c1 == True:
            return "SAB C1"
        if c2 == True:
            return "SAB C2"

    return

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Please provide 1 arguments")
