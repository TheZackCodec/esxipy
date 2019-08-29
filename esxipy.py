import os
import git
import json
import traceback
from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect


def get_vmware_samples():
    if helper.exists("pyvmomi-community-samples"):
        print("Updating pyvmomi-community-samples")
        git.cmd.Git(helper.path_from_src("pyvmomi-community-samples")).pull()
    else:
        print("Cloning pyvmomi-community-samples")
        git.Repo.clone_from("https://github.com/vmware/pyvmomi-community-samples.git",
                            helper.path_from_src("pyvmomi-community-samples"))


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


class Connection:

    connection = None

    def connect_No_SSL(self):  # Connects to ESXI without using Secure Sockets Layer
        self.connection = SmartConnectNoSSL(
            host=settings_dict["host"], user=settings_dict["username"], pwd=settings_dict["password"])

    def connect_SSL(self):  # Connects to the ESXI server using Secure Sockets Layer
        self.connection = SmartConnect(
            host=settings_dict["host"], user=settings_dict["username"], pwd=settings_dict["password"])

    def disconnect(self):
        if self.connection == None:
            print("no connection to close")
        else:
            print("closing connection")
            Disconnect(self.connection)


helper = Helper()
settings_dict = helper.get_json_as_dict("settings.json")


def main():

    try:
        print("\n---------- Starting esxipy ----------\n")

        get_vmware_samples()

        server = Connection()

        # server.connect_No_SSL()

    except KeyboardInterrupt:
        print("\nProgram stopped by user... ")

    except Exception:
        print("\n\n\nERROR!! - A fatal or unhandled error has been thrown!")
        print("\n!!!!!!!!!!!!!!!!!!!! ERROR DETAILS !!!!!!!!!!!!!!!!!!!!\n")
        print(traceback.format_exc())
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    finally:
        print("\n---------- Cleaning up ----------\n")

        print("Disconnecting from server")
        server.disconnect()

        print("\n---------- Clean up complete ----------\n")


if __name__ == "__main__":
    main()
