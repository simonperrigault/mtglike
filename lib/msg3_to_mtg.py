from os.path import join,realpath, basename
from datetime import datetime, timedelta
from multiprocessing import Process, Queue

from xarray import open_dataset

from .spatial_resolution import change_resolution

modele_file_MTG_1km = "modele/Multic1km_mtgi1_YYYYMMDD_hhmm.nc"
modele_file_MTG_2km = "modele/Multic2km_mtgi1_YYYYMMDD_hhmmss.nc"


def msg_extract_datetime(file_name):
    """
    Extract the datetime from the name of a msg file

    Args:
        file_name: name of the file
    Returns:
        Datetime
    """
    # msg : Mmultic3kmNC4_msg03_YYYYMMDDhhmm.nc
    _,_,string_datetime = file_name.split("_")
    year = int(string_datetime[0:4])
    month = int(string_datetime[4:6])
    day = int(string_datetime[6:8])
    hour = int(string_datetime[8:10])
    minute = int(string_datetime[10:12])
    dt = datetime(year,month,day,hour,minute)
    return dt


def modele_string_mtg1km(dt):
    """
    Create the name of the file for a NetCDF corresponding to
    the datetime in parameter, with the good format for a
    mtg file with a resolution of 1km

    Args:
        dt: datetime
    Returns:
        string: the name of the file
    """
    debut_str = "Multic1km_mtgi1_"
    string_datetime = dt.strftime("%Y%m%d_%H%M")
    file_name = debut_str+string_datetime+".nc"
    return file_name
def modele_string_mtg2km(dt):
    """
    Create the name of the file for a NetCDF corresponding to
    the datetime in parameter, with the good format for a
    mtg file with a resolution of 2km

    Args:
        dt: datetime
    Returns:
        string: the name of the file
    """
    debut_str = "Multic2km_mtgi1_"
    string_datetime = dt.strftime("%Y%m%d_%H%M%S")
    file_name = debut_str+string_datetime+".nc"
    return file_name


MINUTE_DURATION = 9
SECONDE_DURATION = 16 # both come from a mtg NetCDF

def modify_and_save(msg_reader, dest_directory, dt_msg, deltaminute, res_out, queue_produits):
    """
    Read a msg file and store the corresponding channels into a mtg file with
    the good format of data, the good file name and good metadata

    Args:
        msg_reader: Dataset of the msg to read
        dest_directory: directory where to save the output mtg file
        dt_msg: datetime of the coverage start of msg
        deltaminute: timedelta between the dt_msg and the coverage start of mtg
        res_out: wanted resolution for the output mtg file
        queue_produits: Queue to return the path of the output file between processes
    Returns:
        None
    """
    # we change the coverage start time
    datetime_mtg = dt_msg + timedelta(minutes=deltaminute)
    if res_out == 1:
        dest = join(dest_directory, modele_string_mtg1km(datetime_mtg))
        mtg_writer = open_dataset(modele_file_MTG_1km, mode="r", decode_cf=False, decode_times=False)
    elif res_out == 2:
        dest = join(dest_directory, modele_string_mtg2km(datetime_mtg))
        mtg_writer = open_dataset(modele_file_MTG_2km, mode="r", decode_cf=False, decode_times=False)
    

    print("Modification des attributs...")
    datetime_mtg = datetime.strptime(msg_reader.attrs["time_coverage_start"][:-3], "%Y-%m-%dT%H:%M:%SZ")
    datetime_mtg += timedelta(minutes=deltaminute)
    mtg_writer.attrs["time_coverage_start"] = datetime_mtg.strftime("%Y-%m-%dT%H:%M:%SZ")
    datetime_mtg += timedelta(minutes=MINUTE_DURATION, seconds=SECONDE_DURATION)
    mtg_writer.attrs["time_coverage_end"] = datetime_mtg.strftime("%Y-%m-%dT%H:%M:%SZ")

    mtg_writer.attrs["Rate_of_valid_data"] = msg_reader.attrs["Rate_of_valid_data"]

    str_now = datetime_mtg.strftime("%Y-%m-%d %H:%M")
    mtg_writer.attrs["date_created"] = str_now
    mtg_writer.attrs["history"] = "Created on " + str_now + " by CMS-Lannion : simulated MTG data from MSG data"
    # id ?


    print("Modification des data_vars...")
    mtg_writer.data_vars["time"].data = msg_reader.data_vars["time"].data - 60*deltaminute
    if res_out == 1: 
        mtg_writer.data_vars["VIS006"].data = change_resolution(msg_reader.data_vars["VIS006"].data, 3, 1)
        # mtg_writer.data_vars["VIS008"].data = change_resolution(msg_reader.data_vars["VIS008"].data, 3, 1)
        # mtg_writer.data_vars["IR_016"].data = change_resolution(msg_reader.data_vars["IR_016"].data, 3, 1)
    elif res_out == 2:
        mtg_writer.data_vars["VIS006"].data = change_resolution(msg_reader.data_vars["VIS006"].data, 3, 2)
        # mtg_writer.data_vars["VIS008"].data = change_resolution(msg_reader.data_vars["VIS008"].data, 3, 2)
        # mtg_writer.data_vars["IR_016"].data = change_resolution(msg_reader.data_vars["IR_016"].data, 3, 2)
        # mtg_writer.data_vars["IR_038"].data = change_resolution(msg_reader.data_vars["IR_039"].data, 3, 2)
        # mtg_writer.data_vars["WV_063"].data = change_resolution(msg_reader.data_vars["WV_062"].data, 3, 2)
        # mtg_writer.data_vars["WV_073"].data = change_resolution(msg_reader.data_vars["WV_073"].data, 3, 2)
        # mtg_writer.data_vars["IR_087"].data = change_resolution(msg_reader.data_vars["IR_087"].data, 3, 2)
        # mtg_writer.data_vars["IR_097"].data = change_resolution(msg_reader.data_vars["IR_097"].data, 3, 2)
        mtg_writer.data_vars["IR_105"].data = change_resolution(msg_reader.data_vars["IR_108"].data, 3, 2)
        # mtg_writer.data_vars["IR_123"].data = change_resolution(msg_reader.data_vars["IR_120"].data, 3, 2)
        # mtg_writer.data_vars["IR_133"].data = change_resolution(msg_reader.data_vars["IR_134"].data, 3, 2)
    
    print("Ecriture...")
    mtg_writer.to_netcdf(dest, mode="w")

    # to return the path of the file created to another process
    queue_produits.put(dest)


def msg3_to_mtg(src, dest_directory, res_out):
    """
    Convert a msg file with a resolution of 3km into a mtg file with the resolution res_out
    and save it into dest_directory

    Args:
        src: path of the msg file
        dest_directory: directory where to save the output mtg file
        res_out: wanted resolution of the output mtg file
    Returns:
        List of paths of the output files
    """
    produits_faits = []
    queue = Queue()

    file_name = basename(realpath(src))

    dt_msg = msg_extract_datetime(file_name)

    # list of the delta between the start of the msg and
    # the mtg we will create
    deltatime_to_handle = []

    if dt_msg.minute % 30 == 0:
        deltatime_to_handle = [10]
    elif dt_msg.minute % 30 == 15:
        deltatime_to_handle = [5, 15]

    msg_reader = open_dataset(src, decode_cf=False, decode_times=False)
    process_list = []
    for deltaminute in deltatime_to_handle:
        process_list.append(Process(target=modify_and_save,
                                        args=[msg_reader, dest_directory, dt_msg,
                                              deltaminute, res_out, queue]))
        process_list[-1].start()
    
    # we wait for all the processes to finish and
    # we collect the paths of the products thanks to the queue
    for process in process_list:
        process.join()
        produits_faits.append(queue.get())
    
    return produits_faits

