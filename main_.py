from flask import Flask,request,jsonify,send_file
import requests
import os
import subprocess
import pudb
import shutil
import zipfile
import requests
from math import floor

app = Flask(__name__)

@app.route("/createTraining",methods=["POST"])
def main():
    if not os.path.exists("./saving_pdfs"):
        os.makedirs("./saving_pdfs")
    
    try:
        if not os.path.exists("./output_from_server"):
            os.makedirs("./output_from_server")
    except:
        pass

    pdf = request.files["pdf"]
    pdf.save("./saving_pdfs/"+pdf.filename) 
    filename = pdf.filename
    filename = filename.split(".")[0]
    print(filename)
    subprocess.run(["java","-Xmx4G","-jar","grobid-core/build/libs/grobid-core-0.7.1-SNAPSHOT-onejar.jar", "-gH","grobid-home", "-dIn", "./saving_pdfs","-dOut", "./output_from_server","-exe" ,"createTraining"])

    s = os.listdir("./output_from_server")
    src = "./output_from_server"
    data = {"fulltext_xml":"","fulltext_raw":"","segmentation_xml":"","segmentation_raw":""}

    for i in s:
        if i == f"{filename}.training.fulltext.tei.xml":
            print(i)
            fulltext_xml = open(f"./output_from_server/{i}","r")
            data["fulltext_xml"] = fulltext_xml.read()
        
        if i == f"{filename}.training.fulltext":
            fulltext_raw = open(f"./output_from_server/{i}","r")
            data["fulltext_raw"] = fulltext_raw.read()
        
        if i == f"{filename}.training.segmentation.tei.xml":
            segmentation_xml = open(f"./output_from_server/{i}","r")
            data["segmentation_xml"] = segmentation_xml.read()
        
        if i == f"{filename}.training.segmentation":
            segmentation__raw = open(f"./output_from_server/{i}","r")
            data["segmentation_raw"] = segmentation__raw.read()
        
        os.remove(f"./output_from_server/{i}")
    
    os.remove("./saving_pdfs/"+pdf.filename)

    return data

@app.route("/trainmodel", methods=["POST"])
def trainmodel():

    fulltext = "./grobid-trainer/resources/dataset/fulltext"
    segmentation = "./grobid-trainer/resources/dataset/segmentation"

    if os.path.exists(fulltext):
        shutil.rmtree(fulltext)

    if os.path.exists(segmentation):
        shutil.rmtree(segmentation)

    zip_file = request.form["zip_link"]
    r = requests.get(zip_file, stream=True)
    with open("./link", 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)

    with zipfile.ZipFile("link", 'r') as zip_ref:
        zip_ref.extractall(f"./tempdir")

    os.remove("link")

    if os.path.exists("./tempdir"):
        os.makedirs("./ftfiles")
        os.makedirs("./segfiles")

    for (root,dirs,files) in os.walk("./tempdir"):
        if root == "./tempdir/segmentation/corpus/tei":
            thresh = floor(0.9*len(os.listdir(root)))
            for i, file in enumerate(os.listdir(root)):
                shutil.move(os.path.join(root, file), os.path.join("./segfiles", file))
                if i > len(os.listdir(root))-thresh:
                    break

        elif root == "./tempdir/segmentation/corpus/raw":
            thresh = floor(0.9*len(os.listdir(root)))
            for i, file in enumerate(os.listdir(root)):
                shutil.move(os.path.join(root, file), os.path.join("./segfiles", file))
                if i > len(os.listdir(root))-thresh:
                    break

        elif root == "./tempdir/fulltext/corpus/tei":
            thresh = floor(0.9*len(os.listdir(root)))
            for i, file in enumerate(os.listdir(root)):
                shutil.move(os.path.join(root, file), os.path.join("./ftfiles", file))
                if i > len(os.listdir(root))-thresh:
                    break

        elif root == "./tempdir/fulltext/corpus/raw":
            thresh = floor(0.9*len(os.listdir(root)))
            for i, file in enumerate(os.listdir(root)):
                shutil.move(os.path.join(root, file), os.path.join("./ftfiles", file))
                if i > len(os.listdir(root))-thresh:
                    break


    for f in os.listdir("./tempdir"):
        if f == 'fulltext':
            shutil.move("./tempdir/fulltext", fulltext)

        if f == 'segmentation':
            shutil.move("./tempdir/segmentation", segmentation)

    shutil.rmtree("./tempdir")

    if os.path.exists("./ftfiles") and os.path.exists("./segfiles"):
        os.makedirs(os.path.join(fulltext, "evaluation/raw"))
        os.makedirs(os.path.join(fulltext, "evaluation/tei"))
        os.makedirs(os.path.join(segmentation, "evaluation/raw"))
        os.makedirs(os.path.join(segmentation, "evaluation/tei"))
                
        for f in os.listdir("./ftfiles"):
            if f.split('.')[-1] == "xml":
                shutil.move(os.path.join("./ftfiles",f), os.path.join("./grobid-trainer/resources/dataset/fulltext/evaluation/tei", f))
            else:
                shutil.move(os.path.join("./ftfiles",f), os.path.join("./grobid-trainer/resources/dataset/fulltext/evaluation/raw", f))

        for f in os.listdir("./segfiles"):
            if f.split('.')[-1] == "xml":
                shutil.move(os.path.join("./segfiles",f), os.path.join("./grobid-trainer/resources/dataset/segmentation/evaluation/tei", f))
            else:
                shutil.move(os.path.join("./segfiles",f), os.path.join("./grobid-trainer/resources/dataset/segmentation/evaluation/raw", f))

    os.rmdir("./ftfiles")
    os.rmdir("./segfiles")
    
    return "200"

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
    
json = {"xml":" xml content","raw":" content of raw "}
