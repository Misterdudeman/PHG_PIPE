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

    def __init__(self, steps=None, recursive=None,
                 verbose=None, high=None, low=None, cwd=None):
        """Initialize class arguments."""
        self.steps = steps
        self.recursive = recursive
        self.verbose = verbose
        self.high = high
        self.low = low
        self.cwd = cwd

    def logging(self, verbose):
        """Initialize logging."""
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.propagate = verbose
        logger.info('Starting logs')

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
        parser.add_argument('--v',
                            action="store_true",
                            help="set verbose")
        parser.add_argument('--hi',
                            type=str,
                            help="high res image format",
                            default="cr2")
        parser.add_argument('--lo',
                            type=str,
                            help="low res image format",
                            default="jpg")

        args, not_used = parser.parse_known_args(argv)
        self.args = args
        self.steps = args.s
        self.recursive = args.r
        self.verbose = args.v
        self.high = args.hi
        self.low = args.lo
        self.cwd = os.getcwd()

    def sort_by_type(self, files, file_list, type_list):
        """Sorts files into type lists."""
        hr_list, lr_list, bin = file_list
        hr_type, lr_type = type_list
        for file in files:
                kind = filetype.guess_extension(file)
                if kind == hr_type:
                    logging.info("Image is High Res: " + file)
                    hr_list.append(file)
                    pass
                elif kind == lr_type:
                    logging.info("Image is Low Res: " + file)
                    lr_list.append(file)
                    pass
                else:
                    logging.info("File is Other: " + file)
                    bin.append(file)
                    pass
        return file_list

    def get_image_types(self, arguments, cwd):
        """Get images by type."""
        if arguments:
            highres_list, lowres_list, bin = ([] for i in range(3))
            file_list = [highres_list, lowres_list, bin]

            highres_type = arguments.hi
            lowres_type = arguments.lo
            type_list = [highres_type, lowres_type]

            if arguments.r:
                for root, dirs, files in os.walk(cwd):
                    logging.info("Script is collecting images recursively")
                    out_lists = self.sort_by_type(files, file_list, type_list)

            else:
                logging.info('Script is collecting images locally')
                files = os.listdir(cwd)
                out_lists = self.sort_by_type(files, file_list, type_list)
        return out_lists

    def check_lists(self, sorted_lists):
        """Check image lists and throw warnings."""
        hr_list, lr_list, bin_list = sorted_lists
        hr_len = len(hr_list)
        lr_len = len(lr_list)
        if hr_len != lr_len:
            logging.warning("High Res Images do not match proxy.")
        elif len(bin_list) > max(len(hr)):
            logging.warning("Too many unrecognized files.")

    def make_set(self, high, low):
        """Make image set."""
        self.high = high
        self.low = low

    def sort_image_sets(self, sorted_lists, steps):
        """Sort images into sets."""
        counter = 0
        set_count = 0
        high_set_list = []
        low_set_list = []
        for high, low in enumerate(sorted_lists):
            print(counter)
            if counter >= steps:
                set_count += 1
                logging.info("Set: " + set_count)
                counter = 0
            else:
                counter += 1

if __name__ == "__main__":
    mhs = merg_hdr_sets()
    mhs.parse_args(['--s 3', '--r'])
    mhs.logging(mhs.verbose)
    images = mhs.get_image_types(mhs.args, mhs.cwd)
    mhs.sort_image_sets(images, mhs.steps)
