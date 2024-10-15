from os import mkdir, remove, symlink
from os.path import exists, islink, abspath, realpath, join, basename

import pyinotify

from lib.to_tif import mtg_to_tif, msg_to_tif
from lib.msg3_to_mtg import msg3_to_mtg
from lib .mtg_to_msg3 import mtg_to_msg3
from lib.to_texted_tif import to_texted_tif

def handle_reception(src):
    """
    Handle the creation of a file in the reception directory.
    Create symbolink links according to the name of the file.

    Args:
        src: the path of the file created.
    Returns:
        None
    """

    abs_path = abspath(realpath(src))
    file_name = basename(src)

    if file_name.find("_msg") != -1:
        # we have received a msg file so we want to convert it into a mtg one
        # we need the _ because the project is in a directory called mtglike
        # so the string 'mtg' is in the path but not _mtg
        symlink(abs_path, join("automate/application/msg3_to/mtg1", file_name))
        symlink(abs_path, join("automate/application/msg3_to/mtg2", file_name))
    
    elif file_name.find("_mtg") != -1:
        if file_name.find("1km") != -1:
            symlink(abs_path, join("automate/application/to_msg3/mtg1", file_name))
        elif file_name.find("2km") != -1:
            symlink(abs_path, join("automate/application/to_msg3/mtg2", file_name))

def handle_transmission(src):
    """
    Handle the creation of a file in the transmission directory.
    Create symbolink links according to the name of the file.

    Args:
        src: the path of the file created.
    Returns:
        None
    """

    abs_path = abspath(realpath(src))
    file_name = basename(src)

    if file_name.find(".nc") != -1:
        if file_name.find("_msg") != -1:
            symlink(abs_path, join("automate/application/to_tif/msg", file_name))
        elif file_name.find("_mtg") != -1:
            symlink(abs_path, join("automate/application/to_tif/mtg", file_name))
    
    if file_name.find(".tif") != -1:
        if file_name.find("texted") == -1:
            symlink(abs_path, join("automate/application/to_texted_tif", file_name))

class HandleEvent(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        """
        Function called when a file is created in the automation directory
        and its subdirectories. Call the appropriate function according to
        the path of the new file

        Args:
            event: an Event object, containing informations about the new file.
        Returns:
            None
        """

        src = event.pathname

        produits = []

        if src.find("reception") != -1:
            # we are in the reception directory
            print("reception")
            handle_reception(src)

        elif src.find("transmission") != -1:
            print("transmission")
            handle_transmission(src)

        elif src.find("msg3_to") != -1:
            print("msg3 to ", end="")
            if src.find("mtg1") != -1:
                print("mtg1")
                produits += msg3_to_mtg(src, "automate/produits", 1)
            elif src.find("mtg2") != -1:
                print("mtg2")
                produits += msg3_to_mtg(src, "automate/produits", 2)
        
        elif src.find("to_msg3") != -1:
            print("to msg3 ", end="")
            if src.find("mtg1") != -1:
                print("from mtg1")
                produits += mtg_to_msg3(src, "automate/produits", 1)
            elif src.find("mtg2") != -1:
                print("from mtg1")
                produits += mtg_to_msg3(src, "automate/produits", 2)

        elif src.find("to_tif") != -1:
            print("to tif ", end="")
            if src.find("_msg") != -1:
                print("from msg")
                produits += msg_to_tif(src, "automate/produits")
            elif src.find("_mtg") != -1:
                print("from mtg")
                produits += mtg_to_tif(src, "automate/produits")
        
        elif src.find("to_texted_tif") != -1:
            print("to texted tif")
            produits += to_texted_tif(src, "automate/produits")

        for produit in produits:
            # we add all the files created to transmission to handle them
            symlink(abspath(produit), join("automate/transmission", basename(produit)))

        if islink(src):
            remove(src)

def mkdir_if_not_exists(src):
    """
    Create a directory if it doesn't exist

    Args:
        src: the path of the directory to create.
    Returns:
        None
    """
    if not exists(src):
        mkdir(src)

# list of all the directories needed by the automate to work
dir_to_make = ["automate", "automate/reception", "automate/transmission",
               "automate/produits", "automate/application",
               "automate/application/msg3_to", "automate/application/msg3_to/mtg1",
               "automate/application/msg3_to/mtg2",
               "automate/application/to_tif", "automate/application/to_tif/mtg",
               "automate/application/to_tif/msg",
               "automate/application/to_msg3", "automate/application/to_msg3/mtg1",
               "automate/application/to_msg3/mtg2",
               "automate/application/to_texted_tif"
]

for dir in dir_to_make:
    mkdir_if_not_exists(dir)

watchmanager = pyinotify.WatchManager()
events = pyinotify.IN_CREATE # we only watch the file creation, not modification or removing

notifier_controller = pyinotify.Notifier(watchmanager, HandleEvent())

watchmanager.add_watch("automate", events, rec=True) # rec = True to watch subdirectories

notifier_controller.loop()

