import traceback
from dotenv import load_dotenv
from langchain.callbacks import get_openai_callback
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
import pickle
import tkinter as tk
import pyautogui
import os
import json
import logging
import time
import sys
import shutil

# from streamlit_extras.add_vertical_space import add_vertical_space


# read the json file and process accordingly. Save the report back to json file.


def try_catch_error(func):

    def wrapper(*args, **kwargs):

        # print_note ("Wrapper func for EA Log -- Begin: {}".format(func.__name__))
        try:
            # print "main in wrapper"
            out = func(*args, **kwargs)
            # print_note ( "Wrapper func for EA Log -- Finish:")
            return out
        except Exception as e:
            # print(str(e))
            # print("Wrapper func for EA Log -- Error: " + str(e))
            error = traceback.format_exc()

            error += "\n\n######If you have EnneadTab UI window open, just close the window. Do no more action, otherwise the program might crash.##########\n#########Not sure what to do? Msg Sen Zhang, you have dicovered a important bug and we need to fix it ASAP!!!!!########"
            error_file = "{}\Documents\EnneadTab Settings\Local Copy Dump\error_log.txt".format(
                os.environ["USERPROFILE"])

            with open(error_file, "w") as f:
                f.write(error)
            os.startfile(error_file)

    return wrapper


class Solution:

    def process_pdf(self, file):
        pdf_reader = PdfReader(file)

        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        logging.info(text)
        self.process_text(text)

    def process_text(self, text):

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text=text)

        embeddings = OpenAIEmbeddings(openai_api_key=self.KEY)

        # FAISS is a vectorstore obj
        VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
        with open(self.local_embeding, "wb") as f:
            pickle.dump(VectorStore, f)

        self.vectors = VectorStore

    @property
    def local_embeding(self):
        return self.get_file_in_dump_folder(f"{self.store_name}.pkl")

    def is_vector_store_exists(self):

        if os.path.exists(self.local_embeding):
            with open(self.local_embeding, "rb") as f:
                self.vectors = pickle.load(f)
            return True
        return False

    def get_response(self, query):

        docs = self.vectors.similarity_search(query=query, k=5)

        llm = OpenAI(openai_api_key=self.KEY)
        chain = load_qa_chain(llm=llm, chain_type="stuff")
        with get_openai_callback() as cb:
            response = chain.run(input_documents=docs, question=query)
            print(cb)

        return response

    def get_data_file(self):
        return self.get_file_in_dump_folder("QAQC_REPORT_DATA.sexyDuck")

    def get_file_in_dump_folder(self, file):

        return "{}\Documents\EnneadTab Settings\Local Copy Dump\{}".format(os.environ["USERPROFILE"], file)

    def has_new_job(self):
        file = self.get_data_file()

        file = shutil.copyfile(
            file, self.get_file_in_dump_folder("QAQC_READER.sexyDuck"))
        with open(file, 'r') as f:
            # get dictionary from json file
            data = json.load(f)

        return data["direction"] == "IN"

    @try_catch_error
    def main(self):
        if "szhang" in os.environ["USERPROFILE"]:
            logging.basicConfig(filename="QAQC_SZ",
                                filemode='a',
                                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                                datefmt='%H:%M:%S',
                                level=logging.INFO)
        begin_time = time.time()
        file = self.get_data_file()
        with open(file, 'r') as f:
            # get dictionary from json file
            data = json.load(f)

        self.KEY = data.get('api_key')
        # this should be controled from Revit side to maintain consiststn over multiple query
        self.store_name = data.get('store_name')
        print(self.store_name)
        if not self.is_vector_store_exists():
            print("vect stroe no existent")
            logging.info("vector store not exists")
            method = data.get('method')
            if method == 'pdf':
                report_address = data["qaqc_file"]
                self.process_pdf(report_address)
            elif method == 'text':
                self.process_text(data.get("qaqc_text"))

        response = self.get_response(data.get("query"))
        print("Response = " + response)
        data["response"] = response
        data["direction"] = "OUT"
        data["compute_time"] = time.time() - begin_time
        logging.info("Response = " + response)
        logging.info("time = {}s".format(data['compute_time']))
        with open(file, 'w') as f:
            # get dictionary from json file
            json.dump(data, f)


EXE_NAME = u"Ennead_QAQC_AI"


def is_another_app_running():

    # print [x.title for x in pyautogui.getAllWindows()]
    for window in pyautogui.getAllWindows():
        # print window.title
        if window.title == EXE_NAME:
            return True
    return False

# make this into tkinter stand alone


class App:
    def __init__(self):
        self.solution = Solution()
        self.window = tk.Tk()
        self.window.title(EXE_NAME)
        self.is_thinking = False
        self.x = 900
        self.y = 700

        self.window_width = 550
        self.window_height = 120
        # 100x100 size window, location 700, 500. No space between + and numbers
        self.window.geometry("{}x{}+{}+{}".format(self.window_width,
                                                  self.window_height,
                                                  self.x,
                                                  self.y))

        self.talk_bubble = tk.Label(self.window, text="EnneadGPT is happy to help!", font=(
            "Comic Sans MS", 18), borderwidth=3, relief="solid")
        # pady ====> pad in Y direction
        self.talk_bubble.pack(pady=15)

        self.window.after(1, self.update)

    def update(self):
        self.window.after(1000, self.check_job)

    def check_job(self):
        if not self.is_thinking and self.solution.has_new_job():
            self.is_thinking = True
            self.talk_bubble.configure(text="Thinking...")
            self.solution.main()
            self.is_thinking = False
            self.talk_bubble.configure(text="Ready to work.")
            print("done!")
            logging.info("DONE!")
        self.window.after(1, self.update)

    def run(self):
        self.window.mainloop()


@try_catch_error
def main():
    if is_another_app_running():
        return
    app = App()
    app.run()


###############################################
if __name__ == "__main__":
    main()
