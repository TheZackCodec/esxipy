import os
import sys
import git
import json
import traceback
from pyVim.connect import vim
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


def PrintVmInfo(vm, depth=1):
    """
    Print information for a particular virtual machine or recurse into a folder
    or vApp with depth protection
    """
    maxdepth = 10

    # if this is a group it will have children. if it does, recurse into them
    # and then return
    if hasattr(vm, 'childEntity'):
        if depth > maxdepth:
            return
        vmList = vm.childEntity
        for c in vmList:
            PrintVmInfo(c, depth+1)
        return

    # if this is a vApp, it likely contains child VMs
    # (vApps can nest vApps, but it is hardly a common usecase, so ignore that)
    if isinstance(vm, vim.VirtualApp):
        vmList = vm.vm
        for c in vmList:
            PrintVmInfo(c, depth + 1)
        return

    summary = vm.summary
    print("Name       : ", summary.config.name)
    print("Path       : ", summary.config.vmPathName)
    print("Guest      : ", summary.config.guestFullName)
    print("UUID       : ", summary.config.uuid)
    annotation = summary.config.annotation
    if annotation != None and annotation != "":
        print("Annotation : ", annotation)
    print("State      : ", summary.runtime.powerState)
    if summary.guest != None:
        ip = summary.guest.ipAddress
        if ip != None and ip != "":
            print("IP         : ", ip)
    if summary.runtime.question != None:
        print("Question  : ", summary.runtime.question.text)

    print("")


class CLI():

    memory_dict = {}

    def start(self):
        while True:
            usr_input = input("\nESXIPY > " + settings_dict["host"] + " > ")


            if usr_input == "ls":
                self.list_vms(False)
            
            elif usr_input == "ls -al":
                self.list_vms(True)

            else:
                print(usr_input.split())

    def list_vms(self, verbose):
        for vm in vm_dict.values():
            print("Name  : ", vm.summary.config.name)
            if verbose:
                print("Guest : ", vm.summary.config.guestFullName)
                print("UUID  : ", vm.summary.config.uuid)
                print("")


helper = Helper()
settings_dict = helper.get_json_as_dict("settings.json")
vm_dict = {}


def main():

    try:
        print("\n---------- Starting esxipy ----------\n")

        server = Connection()
        server.connect_No_SSL()
        print("Succesfully connected to " + settings_dict["host"])

        content = server.connection.RetrieveContent()
        for datacenter in content.rootFolder.childEntity:
            print("Checking Datacenter " + str(datacenter) + " for VMs")
            if hasattr(datacenter, 'vmFolder'):
                vmFolder = datacenter.vmFolder
                vmList = vmFolder.childEntity
                print(str(len(vmList)) + " VMs found!")
                for vm in vmList:
                    vm_dict.update({vm.summary.config.name: vm})

        cli = CLI()

        cli.start()

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
