import os
import json
import traceback
from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect


class Helper:

    def path_from_src(self, path):  # Returns a filepath from the src directory given a string
        return os.path.join(path)

    # Creates specified directory in the source folder if it does not already exist
    def make_dir_if_nonexistant(self, dir):
        os.makedirs(self.path_from_src(dir), exist_ok=True)

    # Returns a dictionary given a valid .json file
    def convert_json_to_dict(self, file_dir):
        return json.load(open(self.path_from_src(file_dir)))

    def exists(self, file_path):  # Returns true if a file already exists
        return os.path.exists(self.path_from_src(file_path))

    # Returns dictionary from the specified file if it exists, otherwise it returns with an empty dict
    def get_json_as_dict(self, path):
        # This will import the data from "drink_list.json" in the "data" folder if it exists
        if self.exists(path):
            print(path + " already exists", end=" ")
            try:
                dictionary = self.convert_json_to_dict(path)
                print(". Converting Json file into dictionary")
            except:
                print(", but is corrupt or blank")
                dictionary = {}
        else:
            print(path + " does not exist. Returning blank dictionary.")
            dictionary = {}

        return dictionary


helper = Helper()


def main():

    try:
        print("\n---------- Starting esxipy ----------\n")

        settings_dict = helper.get_json_as_dict("settings.json")
        server = SmartConnect(
            host=settings_dict["host"], user=settings_dict["password"], pwd=settings_dict["password"])

    except KeyboardInterrupt:
        print("\nProgram stopped by user... ")

    except Exception:
        print("\n\n\nERROR!! - A fatal or unhandled error has been thrown!")
        print("\n!!!!!!!!!!!!!!!!!!!! ERROR DETAILS !!!!!!!!!!!!!!!!!!!!\n")
        print(traceback.format_exc())
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    finally:
        print("\n---------- Cleaning up ----------\n")

        print("\n---------- Clean up complete ----------\n")


if __name__ == "__main__":
    main()
