from os.path import join,realpath, basename
from datetime import datetime, timedelta
from multiprocessing import Process, Queue

from xarray import open_dataset

from .spatial_resolution import change_resolution

modele_file_MSG_3km = "modele/Mmultic3kmNC4_msg03_YYYYMMDDhhmm.nc"

def mtg_extract_datetime(file):
    """
    Extract the datetime from the name of a mtg file

    Args:
        file_name: name of the file
    Returns:
        Datetime
    """
    # mtg : Multic2km_mtgi1_YYYYMMDD_hhmmss.nc
    _,_,date,time = file.split("_")
    year = int(date[0:4])
    month = int(date[4:6])
    day = int(date[6:8])
    hour = int(time[0:2])
    minute = int(time[2:4])
    # we don't need the seconds
    dt = datetime(year,month,day,hour,minute)
    return dt


def modele_string_msg3km(dt):
    """
    Create the name of the file for a NetCDF corresponding to
    the datetime in parameter, with the good format for a
    msg file with a resolution of 3km

    Args:
        dt: datetime
    Returns:
        string: the name of the file
    """
    debut_str = "Mmultic3kmNC4_msg03_"
    string_datetime = dt.strftime("%Y%m%d%H%M")
    dest = debut_str+string_datetime+".nc"
    return dest

MINUTE_DURATION = 12
SECONDE_DURATION = 32 # both come from a msg NetCDF

def modify_and_save(mtg_reader, dest_directory, dt_mtg, deltaminute, res_in, queue_produits):
    """
    Read a mtg file and store the corresponding channels into a msg file with
    the good format of data, the good file name and good metadata

    Args:
        mtg_reader: Dataset of the mtg to read
        dest_directory: directory where to save the output msg file
        dt_mtg: datetime of the coverage start of mtg
        deltaminute: timedelta between the dt_mtg and the coverage start of msg
        res_in: resolution of the input mtg file
        queue_produits: Queue to return the path of the output file between processes
    Returns:
        None
    """
    # we change the coverage start time
    datetime_msg = dt_mtg + timedelta(minutes=deltaminute)

    dest = join(dest_directory, modele_string_msg3km(datetime_msg))
    msg_writer = open_dataset(modele_file_MSG_3km, mode="r", decode_cf=False, decode_times=False)
    

    print("Modification des attributs...")
    datetime_msg = datetime.strptime(mtg_reader.attrs["time_coverage_start"], "%Y-%m-%dT%H:%M:%SZ")
    datetime_msg += timedelta(minutes=deltaminute)
    msg_writer.attrs["time_coverage_start"] = datetime_msg.strftime("%Y-%m-%dT%H:%M:%SZ")
    datetime_msg += timedelta(minutes=MINUTE_DURATION, seconds=SECONDE_DURATION)
    msg_writer.attrs["time_coverage_end"] = datetime_msg.strftime("%Y-%m-%dT%H:%M:%SZ")

    msg_writer.attrs["Rate_of_valid_data"] = mtg_reader.attrs["Rate_of_valid_data"]

    str_now = datetime_msg.strftime("%Y-%m-%d %H:%M")
    msg_writer.attrs["date_created"] = str_now
    msg_writer.attrs["history"] = "Created on " + str_now + " by CMS-Lannion : simulated MSG data from MTG data"
    # id ?


    print("Modification des data_vars...")
    msg_writer.data_vars["time"].data = mtg_reader.data_vars["time"].data - 60*deltaminute
    if res_in == 1: 
        msg_writer.data_vars["VIS006"].data = change_resolution(mtg_reader.data_vars["VIS006"].data, 1, 3)
        # msg_writer.data_vars["VIS008"].data = change_resolution(mtg_reader.data_vars["VIS008"].data, 1, 3)
        # msg_writer.data_vars["IR_016"].data = change_resolution(mtg_reader.data_vars["IR_016"].data, 1, 3)
    elif res_in == 2:
        msg_writer.data_vars["VIS006"].data = change_resolution(mtg_reader.data_vars["VIS006"].data, 2, 3)
        # msg_writer.data_vars["VIS008"].data = change_resolution(mtg_reader.data_vars["VIS008"].data, 2, 3)
        # msg_writer.data_vars["IR_016"].data = change_resolution(mtg_reader.data_vars["IR_016"].data, 2, 3)
        # msg_writer.data_vars["IR_039"].data = change_resolution(mtg_reader.data_vars["IR_038"].data, 2, 3)
        # msg_writer.data_vars["WV_062"].data = change_resolution(mtg_reader.data_vars["WV_063"].data, 2, 3)
        # msg_writer.data_vars["WV_073"].data = change_resolution(mtg_reader.data_vars["WV_073"].data, 2, 3)
        # msg_writer.data_vars["IR_087"].data = change_resolution(mtg_reader.data_vars["IR_087"].data, 2, 3)
        # msg_writer.data_vars["IR_097"].data = change_resolution(mtg_reader.data_vars["IR_097"].data, 2, 3)
        msg_writer.data_vars["IR_108"].data = change_resolution(mtg_reader.data_vars["IR_105"].data, 2, 3)
        # msg_writer.data_vars["IR_120"].data = change_resolution(mtg_reader.data_vars["IR_123"].data, 2, 3)
        # msg_writer.data_vars["IR_134"].data = change_resolution(mtg_reader.data_vars["IR_133"].data, 2, 3)
    
    print("Ecriture...")
    msg_writer.to_netcdf(dest, mode="w")

    # to return the path of the file created to another process
    queue_produits.put(dest)


def mtg_to_msg3(src, dest_directory, res_in):
    """
    Convert a mtg file with a resolution of res_in into a msg file
    and save it into dest_directory

    Args:
        src: path of the mtg file
        dest_directory: directory where to save the output msg file
        res_in: resolution of the input mtg file
    Returns:
        List of paths of the output files
    """
    produits_faits = []
    queue = Queue()

    file_name = basename(realpath(src))

    dt_mtg = mtg_extract_datetime(file_name)

    # list of the delta between the start of the msg and
    # the mtg we will create
    deltatime_to_handle = []

    if dt_mtg.minute % 30 == 0:
        deltatime_to_handle = [0]
    elif dt_mtg.minute % 30 == 10:
        deltatime_to_handle = []
    elif dt_mtg.minute % 30 == 20:
        deltatime_to_handle = [-5]

    mtg_reader = open_dataset(src, decode_cf=False, decode_times=False)
    process_list = []
    for deltaminute in deltatime_to_handle:
        process_list.append(Process(target=modify_and_save,
                                        args=[mtg_reader, dest_directory, dt_mtg,
                                              deltaminute, res_in, queue]))
        process_list[-1].start()
    
    # we wait for all the processes to finish and
    # we collect the paths of the products thanks to the queue
    for process in process_list:
        process.join()
        produits_faits.append(queue.get())
    
    return produits_faits

