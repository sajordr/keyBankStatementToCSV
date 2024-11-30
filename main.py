import os
import pypdf
import sys

def readPdfs(folderPath):
    pdfTexts = {}
    for fileName in os.listdir(folderPath):
        if fileName.endswith('.pdf'):
            filePath = os.path.join(folderPath, fileName)
            with open(filePath, 'rb') as file:
                reader = pypdf.PdfReader(file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text()
                pdfTexts[fileName] = text
    return pdfTexts

def splitText(text):
    return text.split("\n")

def getCsvLine(date, transaction, amount):
    return date.strip() + "|" + transaction.strip() + "|" + amount.strip() + "\n"

def writeToCsv(content, fileName):
    with open(fileName, 'w') as file:
        file.write(content)

def main():
    # Probably more calculation efficient to process letter by letter
    # ie look for past n letters to match "deposit" or newLine or "Total Deposits"
    # instead of by text and then by line and then splitting the line...
    # but this is also easier to write and read.
    input_folder = 'input'
    pdfTexts = readPdfs(input_folder)
    
    depositsString = ""
    withdrawalsString = ""
    pdfsRead = 0
    
    for fileName, text in pdfTexts.items():
        pdfsRead += 1
        #print(f'Parsing {fileName}...')
        lines = splitText(text)
        
        printMe = False
        currentlyChecking = "neither"
        detectedYear = "9999" # if 9999 shows up in the date for results, something went terribly wrong
        
        for line in lines:
            if line.startswith("Ending Balance on"):
                # this line usually looks like 'Ending Balance on October 27, 2020 $XXXXXXX'
                detectedYear = line.split(",")[1].strip().split(" ")[0]
            
            if line.startswith("Cleveland,") or line == "Deposits":
                currentlyChecking = "Deposits"
                printMe = True
            elif line == "Withdrawals":
                currentlyChecking = "Withdrawals"
                printMe = True
                
            if line.startswith("Total Withdrawals") or line.startswith("Total Deposits"):
                currentlyChecking = "neither"
                printMe = False
            
            # the relevant lines start with a number, so we can filter out the rest
            if printMe and (line.startswith("01") or line.startswith("02") or line.startswith("03") or line.startswith("04") or line.startswith("05") or line.startswith("06") or line.startswith("07") or line.startswith("08") or line.startswith("09") or line.startswith("10") or line.startswith("11") or line.startswith("12") ):
                if currentlyChecking == "Deposits":
                    date = line.split(" ", 1)[0] + "/" + detectedYear
                    transaction = line.split(" ", 1)[1].split("$", 1)[0] # the leading $ for the amount is a good delimiter
                    amount = line.split("$", 1)[1]
                    depositsString += getCsvLine(date, transaction, amount)
                elif currentlyChecking == "Withdrawals":
                    date = line.split(" ", 1)[0] + "/" + detectedYear
                    transaction = line.split(" ", 1)[1].split("$", 1)[0]
                    amount = line.split("$", 1)[1]
                    withdrawalsString += getCsvLine(date, transaction, amount)
                else:
                    print("bad line")
                    print(line)
        
    writeToCsv(depositsString, "output/deposits.csv")
    writeToCsv(withdrawalsString, "output/withdrawals.csv")
    print("Done! Processed " + str(pdfsRead) + " statements.")
        
        
if __name__ == "__main__":
    sys.exit(main())