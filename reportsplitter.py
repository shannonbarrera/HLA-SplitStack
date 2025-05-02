"""
python 3.13

This script processes multi-report HLA Fusion PDFs and splits them into individual  reports based on the report type (e.g., PRA or SAB). It extracts Sample IDs from the reports, generates filenames, and saves each report as a separate 
PDF file in the original directory.

Functions:
- get_path_filename(filepath): Extracts the folder path from a file path.
- countpages(pdffilename): Returns the number of pages in a PDF.
- getfirstpageindices(pdffilename): Returns first-page indices for reports.
- getoutputfilenames(pdffilename, firstpages, reporttype): Generates filenames from Sample ID.
- splitpages(pdffilename, firstpage, nextreport, path, outputfilename): Extracts and saves an individual report.
- main(filepath, filetype): Orchestrates the report splitting based on detected report type.

Usage:
    python reportsplitter.py <path_to_pdf> <report_type>

Dependencies:
    - pypdf
    - reporttype (custom module for identifying report type)

Note:
    This script is designed for use in labs processing batch PDF exports 
    from HLA Fusion. Output files are named using Sample ID when available.

By: Shannon Barrera
Date: 04/09/2025
"""
import re
import pypdf
import reporttype
import os




def countpages(pdffilename):
    """
    Counts the number of pages in a PDF file.

    Args:
        pdffilename (str): Path to the PDF file.

    Returns:
        int: The number of pages in the PDF.
    """
    with open(pdffilename, 'rb') as file:
        reader = pypdf.PdfReader(file)
        num_pages = len(reader.pages)
    return num_pages


  

def getfirstpageindices(pdffilename):
    """
    Identifies the starting page indices for reports by locating pages 
    that contain "Page 1 of"

    Args:
        pdffilename (str): Path to the PDF file.

    Returns:
        list: A list of page indices indicating the first page of each report.
    """
    with open(pdffilename, 'rb') as file:
        reader = pypdf.PdfReader(file)
        indices = []
        currentpage = -1
        for page in reader.pages:
            currentpage += 1
            text = page.extract_text()
            if text:
                if "Page 1 of" in text:
                    indices.append(currentpage)
                else:
                    continue
    return indices


def getoutputfilenames(pdffilename, firstpages, reporttype):
    """
    Generates a list of output filenames for each report in the PDF
    by extracting the Sample ID from the text.

    Args:
        pdffilename (str): Path to the PDF file.
        firstpages (list): List of page indices where reports start.
        reporttype (str): Type of report ('PRA C1', 'SAB C2', etc.).

    Returns:
        list: List of Sample IDs to use as filenames.
    """
    with open(pdffilename, 'rb') as file:
        reader = pypdf.PdfReader(file)
        names = []
        output_filename = ""
        for i in firstpages:
            if reporttype in ["SAB C1", "SAB C2"]:
                page = reader.pages[i]
                text = page.extract_text()
                if text:
                    lines = text.splitlines()                  
                    for line in lines:
                        if "Sample ID:" in line:
                            output_filename = line
                if output_filename == "":
                    output_filename = f"report{i+1}"
            if reporttype in ["PRA C1", "PRA C2"]:
                secondpage = i + 1
                page = reader.pages[secondpage]
                text = page.extract_text()
                if text:
                    lines = text.splitlines()
                    output_filename = lines[1]
                if output_filename == "":
                    output_filename = f"report{int(i/3)+1}"
            output_filename = output_filename.replace("Sample ID", "")
            output_filename = output_filename.replace("Local ID", "")
            output_filename = output_filename.replace("Patient ID", "")
            output_filename = output_filename.replace(":", "")
            output_filename = output_filename.replace(".", "")
            output_filename = re.sub(r'\d+', '', output_filename)
            output_filename = output_filename.strip()
            names.append(output_filename)

    return names


#Takes the file, first page index, output folder path, Sample ID, and PRA class and writes each report to its own pdf, saving it under the Sample ID.
def splitpages(pdffilename,firstpage,nextreport,outputfilename):
    """
    Splits out a single report from a PDF based on the start and end page
    and writes it to a new PDF named after the Sample ID.

    Args:
        pdffilename (str): Path to the source PDF file.
        firstpage (int): Index of the first page of the report.
        nextreport (int): Index of the first page of the next report.
        path (str): Destination folder path.
        outputfilename (str): Filename (without extension) to save the split report under.

    Returns:
        None
    """
    pages = []
    pageinreport = firstpage
    for i in range(int(firstpage),int(nextreport)):
        pages.append(pageinreport)
        pageinreport += 1
    report_type = reporttype.main(pdffilename, firstpage)
    if report_type.startswith("PRA"):
        outputfilename = outputfilename + " " + report_type + ".pdf"
    else:
        outputfilename = outputfilename + " " + report_type + "-1.pdf"

    filepath = os.path.dirname(pdffilename)
    filepath = filepath + "/" + outputfilename

    filename, extension = os.path.splitext(filepath)
    counter = 1
    while os.path.exists(filepath):
        filepath = f"{filename}_{counter}{extension}"
        counter += 1
    output = pypdf.PdfWriter(filepath)
    input_pdf = pypdf.PdfReader(pdffilename)
    pagenum = -1
    for page in input_pdf.pages:
        pagenum += 1
        if pagenum in pages:
            output.add_page(page)

    with open(filepath, "wb") as output_stream:
        output.write(output_stream)
    return


def main(filepath):
    """
    Main function to split a multi-report PDF into individual reports named by Sample ID.

    Args:
        filepath (str): Full path to the input PDF.
        filetype (str): Type of the report (not directly used here).

    Returns:
        None
    """
    report_type = reporttype.main(filepath)
    pagecount = countpages(filepath)
    firstpages = getfirstpageindices(filepath)
    outputfilenames = getoutputfilenames(filepath, firstpages, report_type)
    
    for i in range(len(firstpages)):
        if i < len(firstpages)-1:
            splitpages(filepath, firstpages[i], firstpages[i+1], outputfilenames[i])
        if i == len(firstpages)-1:
            splitpages(filepath, firstpages[i], (pagecount), outputfilenames[i])
    return



if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Please provide 1 argument")
