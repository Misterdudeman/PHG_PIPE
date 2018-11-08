import argparse
import filetype
import logging
import os


class merg_hdr_sets(object):
    """
    Merge Image Sets into HDRIs.

    Checks a folder for image sets,
    organises each set and outputs finished HDRIs.

    Args:
        steps (int): Steps per image set
        recursive (bool): Searches through subfolders as well
        high (str): Format for the high resolution images
        low (str): Format for the low resolution images

    Returns:
        type: description

    Raises:
        Exception: description

    """

    def __init__(self, steps=None, recursive=None, high=None, low=None, cwd=None):
        """Initialize class arguments."""
        self.steps = steps
        self.recursive = recursive
        self.high = high
        self.low = low
        self.cwd = cwd

    def parse_args(self, argv=None):
        """Parse Args from class and argparse."""
        parser = argparse.ArgumentParser(
                        description="Ingest and process image sets into HDRIs")
        parser.add_argument('-s',
                            type=int, help='steps per set',
                            default=3)
        parser.add_argument('--r',
                            help="set recursive folder search",
                            action="store_true")
        parser.add_argument('--hi',
                            type=str,
                            help="high res image format",
                            default="cr2")
        parser.add_argument('--lo',
                            type=str,
                            help="low res image format",
                            default="jpg")

        args, not_used = parser.parse_known_args(argv)
        self.steps = args.s
        self.recursive = args.r
        self.high = args.hi
        self.low = args.lo

    def sort_by_type(self, files, file_list, type_list):
        """Sorts files into type lists."""
        hr_list, lr_list, bin = file_list
        hr_type, lr_type = type_list
        for file in files:
                kind = filetype.guess_extension(file)
                if kind == hr_type:
                    hr_list.append(file)
                    pass
                elif kind == lr_type:
                    lr_list.append(file)
                    pass
                else:
                    bin.append(file)
                    pass
        return file_list

    def get_image_types(self, arguments, cwd):
        """"""
        if arguments:
            highres_list, lowres_list, bin = ([] for i in range(3))
            file_list = [highres_list, lowres_list, bin]

            highres_type = arguments.hi
            lowres_type = arguments.lo
            type_list = [highres_type, lowres_type]

            if arguments.r:
                for root, dirs, files in os.walk(cwd):
                    file_list = self.sort_by_type(files, file_list, type_list)

            else:
                for files in os.listdir(cwd):
                    file_list = self.sort_by_type(files, file_list, type_list)
if __name__ == "__main__":
    mhs = merg_hdr_sets.parse_args(['--s 3', '--r'])
