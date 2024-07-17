#### this has to run in python 3.x
import traceback
import os
import sys
import io
import json
sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib')
sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Dependency Modules')

#
from EnneadTab import ENVIRONMENT
#sys.path.append(ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)


#from pyChatGPT import ChatGPT
import openai


def secure_folder(path):
    from os import makedirs as OS_MAKEDIRS
    try:
        OS_MAKEDIRS(path)

    except Exception as e:

        #print_note( "folder cannot be secured")
        #print_note(e)
        pass
    return path

def get_user_folder():
    from os import environ as OS_ENV
    #print OS_ENV["USERPROFILE"]
    return "{}\Documents".format(OS_ENV["USERPROFILE"])

def get_EA_setting_folder():
    folder = get_user_folder() + "\EnneadTab Settings"
    #print folder
    return secure_folder(folder)


def get_special_folder_in_EA_setting(folder_name):
    folder = get_EA_setting_folder() + "\{}".format(folder_name)
    return secure_folder(folder)

def get_EA_local_dump_folder():
    return get_special_folder_in_EA_setting("Local Copy Dump")


def read_json_as_dict(filepath, use_encode = True):

    if use_encode:
        with io.open(filepath, encoding='utf8') as f:
            data = json.load(f)
        return data

    else:
        with open(filepath,"r") as f:
            data = json.load(f)
        return data


def save_dict_to_json(dict, filepath, use_encode = True):

    if use_encode:
        with io.open(filepath, 'w', encoding='utf-8') as f:
            # Serialize the data and write it to the file
            json.dump(dict, f, ensure_ascii=False)
            return

    else:
        with open(filepath,"w") as f:
            json.dump(dict, f)


def is_file_exist_in_folder(check_file_name, folder):
    import os
    print(os.listdir(folder))
    for file_name in os.listdir(folder):
        print (file_name)
        if check_file_name == file_name:
            return True
    return False


class PromptData:

    def __init__(self):
        file_name = "EA_TRANSLATE.json"
        dump_folder = get_EA_local_dump_folder()
        file_path = "{}\{}".format(dump_folder, file_name)
        if not is_file_exist_in_folder(file_name, dump_folder):
            print ("not found")
            return

        data = read_json_as_dict(file_path)
        if data["direction"] != "input":
            print ("direction not input")
            return
        self.session_token = data["session_token"]
        # Extract the recipient, sender email, and email content from the JSON data
        self.conversation_history = data["conversation_history"]
        #"The following is a conversation with an AI assistant for problems in Rhino and Revit. The assistant is helpful, creative, clever, friendly and very funny.\n\nYou: How do I create a sheet in Revit\nEnneadTab Copilot:"
        self.ai_name = data["ai_name"]
        self.human_name = data["human_name"]
        self.key_prompt = data["key_prompt"]
        self.max_tokens = data["max_tokens"]

    def store(self):
        file_name = "EA_TRANSLATE.json"
        dump_folder = get_EA_local_dump_folder()
        file_path = "{}\{}".format(dump_folder, file_name)
        data = read_json_as_dict(file_path)
        """
        if self.ai_name in self.response:
            self.conversation_history += "{}".format(self.response)
        else:
            self.conversation_history += "\n{}{}".format(self.ai_name, self.response)
        """
        self.conversation_history += "{}".format( self.response)

        self.conversation_history += "\n\n"
        data["conversation_history"] = self.conversation_history
        data["direction"] = "output"
        print (self.conversation_history)
        """
        for attr in dir(self):
            if "__" in attr:
                continue
            data[attr] = getattr(self, attr)
        """


        save_dict_to_json(data, file_path)

    def process(self):



        openai.api_key =  self.session_token

        response = openai.Completion.create(model = "text-davinci-003",
                                            prompt = self.conversation_history,
                                            temperature = 0.9,
                                            max_tokens = self.max_tokens,
                                            top_p = 1,
                                            frequency_penalty = 0.0,
                                            presence_penalty = 0.6,
                                            stop = ["Bye bye" ]# stop means when conversation encounter those items, it will stop generating .
                                            )
        print (response)
        self.response = response["choices"][0]["text"]



def main():
    data = PromptData()
    if not hasattr(data, "ai_name"):
        return
    print ("processing")
    data.process()
    data.store()



if __name__ == "__main__":
    try:
        main()
        print ("finished")
    except:
        error = traceback.format_exc()
        error += "\n\n##########################\n\n There is a issue about token limit.\nYou should reduce the sample translation counts or reduce the items to translate.\nThis is the balance between accuracy and capacity."
        error_file = "{}\error_log.txt".format(get_EA_local_dump_folder())
        with open(error_file, "w") as f:
            f.write(error)
        import subprocess, os
        os.startfile(error_file)
