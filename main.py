from flask import Flask,request,jsonify,send_file
import requests
import os
import subprocess
import pudb
import shutil
from Act_detection import load_model
import zipfile
import requests

app = Flask(__name__)

@app.route("/spacy",methods=["POST"])
def spacy():
    html_text = request.form["key"]
    detected_text=load_model(html_text)
    return detected_text

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

@app.route("/rebuildTraining",methods=["POST"])
def rebuild_training():
    zip_file = request.form["zip_link"]
    r = requests.get(zip_file, stream=True)
    with open("./link", 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
    with zipfile.ZipFile("link", 'r') as zip_ref:
        zip_ref.extractall("./zip")
    
    os.remove("link")
    if os.path.exists("./grobid-trainer/resources/dataset/fulltext/corpus"):
        shutil.rmtree("./grobid-trainer/resources/dataset/fulltext/corpus")
        
    dest = shutil.move("./zip/fulltext/corpus", "./grobid-trainer/resources/dataset/fulltext/corpus")
    
    subprocess.run(["./gradlew","train_fulltext"])
    
    return "200"
   
@app.route("/adding_to_training",methods=["POST"])
def add_to_training_data():
    model = request.form["model"]
    xml = request.form["xml"]
    name_of_file = request.form["name_of_file"]
    name_of_file = f"{name_of_file}.training.{model}.tei.xml"

    if model == "fulltext":
        path = f"./grobid-trainer/resources/dataset/{model}/corpus/tei/{name_of_file}"
    
    if model == "header":
        path = f"./grobid-trainer/resources/dataset/{model}/corpus/tei/{name_of_file}"
    
    if model == "segmentation":
        path = f"./grobid-trainer/resources/dataset/{model}/corpus/tei/{name_of_file}"

    with open(path,"w") as f:
        f.write(xml)

    return "Hello"
    

@app.route("/spacy_training",methods=['POST'])
def spacy_train():
    zip_file = request.files["zip"]
    zip_file.save(zip_file.filename)
    with zipfile.ZipFile(zip_file.filename, 'r') as zip_ref:
        zip_ref.extractall("./")
    # src = zip_file.filename
    subprocess.call(['python3','train_data.py'])
    subprocess.call(['python3','section_train_model.py'])
    return "200"

@app.route("/train_model",methods=["POST"])
def train():
    name_of_model = request.form["name"]

    if name_of_model == "fulltext":
        subprocess.run(["./gradlew","train_fulltext"])

    if name_of_model == "header":
        subprocess.run(["./gradlew","train_header"])
    if name_of_model == "segmentation":
        subprocess.run(["./gradlew","train_segmentation"])

    return "done"

# @app.route("/Evaluation",methods=["POST"])
# def evaluate():
#     link = request.form["key"]
#     response = requests.get(link)
#     name_of_pdf = link.split("/")

#     if not os.path.exists("./grobid_client_python/resources/test_pdf"):
#         os.makedirs("./grobid_client_python/resources/test_pdf")
#         os.makedirs("./grobid_client_python/resources/test_out")

#     #for saving the response into pfd.
#     with open("./grobid_client_python/resources/test_pdf/"+name_of_pdf[-1],"wb") as f:
#         f.write(response.content) 
    
#     name = name_of_pdf[-1]
#     name = name.split(".")

#     # calling the grobid for fullText model.
#     client = GrobidClient(config_path="./grobid_client_python/config.json")
#     client.process("processFulltextDocument", "./grobid_client_python/resources/test_pdf", output="grobid_client_python/resources/test_out/",force=True)

#     with open(f"./grobid_client_python/resources/test_out/{name[0]}.tei.xml","r") as f:
#         data = f.read()
    
#     #removing the directories to make sure that memory is not used much
#     shutil.rmtree("./grobid_client_python/resources/test_pdf")
#     shutil.rmtree("./grobid_client_python/resources/test_out")

#     return data

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
    
json = {"xml":" xml content","raw":" content of raw "}