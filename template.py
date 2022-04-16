
from isbntools.app import *
import ast
from openpyxl import Workbook, load_workbook
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="YOUR_PATH\\GOOGLE_API_KEY.json"

def errorHandler(error, currentBookData):
    errorLogFile = open("YOUR_PATH\\errors.txt", "a")
    errorLogFile.write("\n")
    errorLogFile.write("==================START LOG==================")
    
    errorLogFile.write("CURRENT BOOK")
    errorLogFile.write("\n")
    errorLogFile.write(currentBookData)

    errorLogFile.write("\n")
    
    errorLogFile.write("ERROR")
    errorLogFile.write("\n")
    errorLogFile.write(error)

    errorLogFile.write("\n")

    errorLogFile.write("==================END LOG==================")
    errorLogFile.write("\n")
    errorLogFile.close()

def writeToDB(dict, ISBN):
    try:
        DB_FILE_NAME = r'YOUR_PATH\\EXECL_FILE_NAME.xlsx'
        bookDB = load_workbook(filename=DB_FILE_NAME)
        sheet = bookDB['bookDB']
        DATA_TO_APPEND = [dict['title'], dict['author'][0]['name'], ISBN]
        sheet.append(DATA_TO_APPEND)
        bookDB.save(DB_FILE_NAME)
        print("Successfully wrote to DB")
    except Exception as e:
        print("=========================ERROR DESC START=========================")
        print(e)
        print("=========================ERROR DESC END=========================")

def getISBN(dectectedTextArray):
    ISBN = -1
    LENGTH = len(dectectedTextArray)
    for idx in range(0, LENGTH):
        if (("isbn" in dectectedTextArray[idx].lower()) \
            and ((idx+1)<LENGTH)):
            ISBN = dectectedTextArray[idx+1]
    return ISBN

def detect_text(path):
    """Detects text in the file."""
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')
    dectectedTextArray = []
    for text in texts:
        dectectedTextArray.append(text.description)

        #vertices = (['({},{})'.format(vertex.x, vertex.y)
                    #for vertex in text.bounding_poly.vertices])

        #print('bounds: {}'.format(','.join(vertices)))
    
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    return dectectedTextArray

def start():
    PATH = "YOUR_PATH_TO_IMG_FOLDER"
    os.chdir(PATH)

    for file in os.listdir():
        try:
            if file.endswith(".jpg"):
                file_path = f"{PATH}\\{file}"

                dectectedTextArray = detect_text(file_path)
                
                ISBN = getISBN(dectectedTextArray)
                print(ISBN)

                bookData = registry.bibformatters['json'](meta(ISBN))
                dictionary = ast.literal_eval(bookData)
                print(dictionary)

                writeToDB(dictionary, ISBN)
            else:
                errorHandler("INVALID FILE FORMAT\nUPLOAD JPG IMAGES", f"{PATH}\\{file}")    

        except Exception as e:
            errorHandler(str(e), f"{PATH}\\{file}")
            

start()



