from subprocess import run

def tif_to_avi(liste_images, dest, width, height):
    """
    Create an avi video from a list of tif pictures
    and save it to dest

    Args:
        liste_images: list of tif pictures
        dest: name of the output file
        width: width of the pictures
        height: height of the pictures
    Returns:
        None
    """
    str_liste_images = ",".join(liste_images)
    command = [
        "mencoder",
        f"mf://{str_liste_images}",
        "-mf",
        f"w={width}:h={height}:fps=2:type=tif",
        "-ovc",
        "x264",
        "-o",
        f"{dest}",
        "-noskip"
    ]
    print(f"We execute : {' '.join(command)}")
    run(command)

