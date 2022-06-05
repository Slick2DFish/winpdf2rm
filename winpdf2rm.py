import os
import glob
import uuid
import shutil
import zlib
import zipfile
from PyPDF2 import PdfFileWriter, PdfFileReader

for file in os.listdir(os.getcwd()):
    if file.endswith(".pdf"):
        inputpdf = PdfFileReader(open(file, "rb"))

        NUUID = uuid.uuid4()
        print(NUUID)
        dire = "tmp/under/" + str(NUUID)
        os.mkdir(dire)

        shutil.copy2("tmp/template/temp.content", "tmp/under/")
        shutil.copy2("tmp/template/temp.pagedata", "tmp/under/")

        os.rename("tmp/under/temp.content", "tmp/under/" + str(NUUID) + ".content")
        os.rename("tmp/under/temp.pagedata", "tmp/under/" + str(NUUID) + ".pagedata")

        for i in range(inputpdf.numPages):
            output = PdfFileWriter()
            output.addPage(inputpdf.getPage(i))
            with open("test%s.pdf" % i, "wb") as outputStream:
                output.write(outputStream)

        for i in range(inputpdf.numPages):
            command = "echo image test" + str(i) + ".pdf 1  0 0  0.7 | drawj2d -Trm "
            os.system(command)
            newName = str(i) + ".rm"
            os.rename("out.rm", newName)
            os.replace(newName, dire + "/" + newName)
            shutil.copy("tmp/template/0-metadatax.json", dire)
            os.rename(dire + "/" + "0-metadatax.json" , dire + "/" + str(i) + "-metadata.json")
        with open(dire + ".content", 'r+') as fd:
            contents = fd.readlines()
            for i in range(inputpdf.numPages -1):
                contents.insert(61 + i,"\"" +  str(uuid.uuid4()) + "\",\n")  # new_string should end in a newline
            contents.insert(60 + inputpdf.numPages, "\"" +  str(uuid.uuid4()) + "\"    ],\n")
            contents[59] = "    \"pageCount\": "+ str(inputpdf.numPages) + ",\n"
            fd.seek(0)  # readlines consumes the iterator, so we need to start over
            fd.writelines(contents)  # No need to truncate as we are increasing filesize


        compression = zipfile.ZIP_DEFLATED
        zf = zipfile.ZipFile(os.path.splitext(file)[0] + ".zip", mode="w")
        zf.write(os.path.join("tmp/under/",  str(NUUID) + ".content"),  str(NUUID) + ".content", compress_type=compression)
        zf.write(os.path.join("tmp/under/",  str(NUUID) + ".pagedata"),  str(NUUID) + ".pagedata", compress_type=compression)
        file = "./tmp/under/" +  str(NUUID)
        for root, dirs, files in os.walk(file):
                for file in files:
                    zf.write(os.path.join(root, file), str(NUUID) + "/" + file)
        zf.close()

        folder = 'tmp/under/'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
                
        for i in range(inputpdf.numPages):
            os.remove("test%s.pdf" % i)
