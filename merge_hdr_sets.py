import argparse
import filetype
import logging
import os
import re
import time
import shutil
# Write HDRMerge install location in .ini


class image_set(object):
    """Image set class for processing pairs."""

    def __init__(self, high, low):
        """Make image set."""
        self.high = high
        self.low = low
        self.path_high = None
        self.path_low = None
        self.path_hdr = None
        self.__str__,
        self.__repr__ = "High Res: {} :: Low Res: {} ".format(high, low)

    # def set_path(self, path, set_path=""):
    #     """Set Image set paths."""
    #     if set_path == "high":
    #         self.path_high = path
    #
    #     if set_path == "low":
    #         self.path_low = path
    #
    #     else:
    #         raise ValueError('set_path must be high or low')


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

    def __init__(self, name=None, steps=None, recursive=None,
                 verbose=None, high=None, low=None, cwd=None):
        """Initialize class arguments."""
        self.name = name
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
        if not verbose:
            logging.disable(logging.INFO)
            logging.disable(logging.WARN)
        logger.info('Starting logs')

    def parse_args(self, argv=None):
        """Parse Args from class and argparse."""
        parser = argparse.ArgumentParser(
                        description="Ingest and process image sets into HDRIs")
        parser.add_argument('-n',
                            type=str, help='Photo set name',
                            default=None)
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
        self.cwd = os.getcwd()
        self.name = args.n
        if self.name is None:
            self.name = os.path.basename(self.cwd)
        else:
            self.name = self.name.lstrip()
            self.name = self.name.replace(" ", "_")

        self.steps = args.s
        self.recursive = args.r
        self.verbose = args.v
        self.high = args.hi
        self.low = args.lo

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

    def match_pairs(self, list1, list2, verbose):
        """Take 2 lists and return bool list of matching pairs."""
        pair_match = []
        for index, (item1, item2) in enumerate(zip(list1, list2)):
            if item1 == item2:
                pair_match.append(True)
                if verbose:
                    logging.info('{} and {} are a match'.format(item1, item2))
            else:
                pair_match.append(False)
                if verbose:
                    logging.info('{} and {} are not the same'.format(item1,
                                                                     item2))
        return pair_match

    def numbers_list(self, list):
        """List of numbers from list of names."""
        numbers_list = []
        for item in list:
            n = re.findall("\d{3}.", item)[0]
            numbers_list.append(n)
        return numbers_list

    def list_math(self, list1, list2, ops='out', index=False):
        """Return list items or list indexs by operation."""
        if ops == 'out':
            if index:
                new_list = [i for i, x in enumerate(list1) if x not in list2]
            else:
                new_list = [x for i, x in enumerate(list1) if x not in list2]
        elif ops == 'in':
            if index:
                new_list = [i for i, x in enumerate(list1) if x in list2]
            else:
                new_list = [x for i, x in enumerate(list1) if x in list2]
        elif ops == 'match':
            if index:
                new_list = [i for i, x in enumerate(list1) if i in list2]
            else:
                new_list = [x for i, x in enumerate(list1) if i in list2]
        else:
            raise Exception('Ops requires in, out or match operation')
        return new_list

    def remove_non_matching(self, list1, list2):
        """Remove none matching elements from 2 lists."""
        num_list1 = self.numbers_list(list1)
        num_list2 = self.numbers_list(list2)
        logging.debug("NUMBERS LISTS: {}, {} ".format(num_list1, num_list2))

        num_idx_list1_remove = self.list_math(num_list1, num_list2, index=True)
        num_idx_list2_remove = self.list_math(num_list2, num_list1, index=True)
        logging.debug("NUMBERS TO REMOVE: {}, {}".format(num_idx_list1_remove,
                                                         num_idx_list2_remove))

        num_list1_clean = self.list_math(num_list1, num_list2, ops='in')
        num_list2_clean = self.list_math(num_list2, num_list1, ops='in')
        logging.info("CLEAN NUMBERS LIST: {}, {}".format(num_list1_clean,
                                                         num_list2_clean))

        list1_remove = self.list_math(list1, num_idx_list1_remove, ops='match')
        list2_remove = self.list_math(list2, num_idx_list2_remove, ops='match')
        logging.debug("REMOVE LIST: {}, {}".format(list1_remove, list2_remove))

        list1_clean = self.list_math(list1, list1_remove, ops='out')
        list2_clean = self.list_math(list2, list2_remove, ops='out')
        logging.debug("CLEAN LIST: {}, {}".format(list1_clean, list2_clean))

        match_list = self.match_pairs(num_list1_clean,
                                      num_list2_clean,
                                      mhs.verbose)

        new_list1 = []
        new_list2 = []
        matching = [new_list1, new_list2]
        bin1 = []
        bin2 = []
        non_matching = [bin1, bin2]
        for idx, (item1, item2, match) in enumerate(zip(list1_clean,
                                                        list2_clean,
                                                        match_list)):
            if match:
                new_list1.append(item1)
                new_list2.append(item2)
            else:
                bin1.append(item1)
                bin2.append(item1)
                logging.warn(("{}:: {} and {}" +
                             "do not match. Removed").format(idx,
                                                             item1,
                                                             item2))
        return matching, non_matching

    def check_lists(self, sorted_lists):
        """Check image lists and throw warnings."""
        hr_list, lr_list, bin_list = sorted_lists
        matching, non_matching = self.remove_non_matching(hr_list, lr_list)
        print(bin_list, non_matching)
        hr_list_new = sorted(matching[0])
        lr_list_new = sorted(matching[1])
        cleaned_list = [hr_list_new, lr_list_new]
        hr_len = len(hr_list_new)
        lr_len = len(lr_list_new)
        if hr_len != lr_len:
            logging.warning("High Res Images do not match proxy.")
        elif len(bin_list) > max(hr_len, lr_len):
            logging.warning("Too many unrecognized files.")
        return cleaned_list

    def set_check_matching(self, set, steps):
        """Check if image sets match."""
        is_matching = False
        counter = 0

        for (high, low) in zip(set.high, set.low):
            h = re.findall("\d{3}.", high)[0]
            l = re.findall("\d{3}.", low)[0]

            if h == l:
                logging.info("{} and {} match!".format(high, low))
                counter = counter + 1

            if counter > steps:
                is_matching = True
                logging.info("Set Match!")
        return is_matching

    def sort_image_sets(self, sorted_lists, steps):
        """Sort images into sets."""
        steps = steps-1
        counter = 0
        set_count = 0
        # Set up image sets
        high_set_list = []
        low_set_list = []
        set_list = []

        discarded = []

        high = sorted_lists[0]
        low = sorted_lists[1]

        for (hi, lo) in zip(high, low):
            if counter > steps:
                # Make image set
                img_set = image_set(high_set_list, low_set_list)

                # Append image set to set_list
                check = self.set_check_matching(img_set, steps)

                if check:
                    set_list.append(img_set)
                    # Reset image_set_lists
                    high_set_list = []
                    low_set_list = []
                    # Add 1 to Set Counter
                    set_count += 1
                    logging.info("Set: " + str(img_set.high)
                                 + " " + str(img_set.low))
                else:
                    discarded.append(img_set)
                    logging.warning("Set: " + str(img_set.high)
                                    + " " + str(img_set.low) + " DISCARDED")
                    high_set_list = []
                    low_set_list = []
                counter = 0
            else:
                high_set_list.append(hi)
                low_set_list.append(lo)
                logging.info("Adding High: " + str(hi))
                logging.info("Adding Low: " + str(lo))
                counter += 1
        return set_list, discarded

    def folder_name(self, images, steps, type=None):
        """Make folder name."""
        first = images[0].split('.')[0]
        last = images[steps].split('.')[0][-2:]
        fname = first + '-' + last
        if type is None:
            return fname
        else:
            fname_type = fname + '_{}'.format(type)
            # top = re.findall("\d{3}.", fname)[0]
            return fname_type

    def build_folders(self, args, cwd, set, steps, name=None):
        """Build folders based on set."""
        # Shift number of steps to last index
        steps = steps-1
        parent = self.folder_name(set.high, steps)
        folder_name_high = self.folder_name(set.high, steps, args.hi)
        folder_name_low = self.folder_name(set.low, steps, args.lo)
        folder_name_hdr = self.folder_name(set.high, steps, "hdr")

        if name:
            root = os.path.join(self.cwd, name)
            high_dir = os.path.join(cwd, root, parent, folder_name_high)
            low_dir = os.path.join(cwd, root, parent, folder_name_low)
            hdr_dir = os.path.join(cwd, root, parent, folder_name_hdr)

        else:
            root = cwd
            high_dir = os.path.join(cwd, parent, folder_name_high)
            low_dir = os.path.join(cwd, parent, folder_name_low)
            hdr_dir = os.path.join(cwd, parent, folder_name_hdr)

        if not os.path.exists(high_dir):
            os.makedirs(high_dir)

        set.path_high = high_dir

        if not os.path.exists(low_dir):
            os.makedirs(low_dir)

        set.path_low = low_dir

        if not os.path.exists(hdr_dir):
            os.makedirs(hdr_dir)

        set.path_hdr = hdr_dir
        return set

    def move_set(self, set):
        """Move image set to folders."""
        high_set = set.high
        low_set = set.low
        high_dir = set.path_high
        low_dir = set.path_low
        logging.info(high_dir)

        for h, l in zip(high_set, low_set):
            hi = os.path.join(self.cwd, h)
            lo = os.path.join(self.cwd, l)

            if hi != high_dir:
                shutil.move(hi, high_dir)
            if lo != low_dir:
                shutil.move(lo, low_dir)

if __name__ == "__main__":
    mhs = merg_hdr_sets()
    mhs.parse_args(['-n Intersection', '--s 3', '--r', '--v'])
    mhs.logging(mhs.verbose)
    images = mhs.get_image_types(mhs.args, mhs.cwd)
    # logging.info(images)
    logging.info("==============got=images===============")

    matching = mhs.check_lists(images)
    # logging.info(matching)
    logging.info("=============check=lists===============")
    sets, bin = mhs.sort_image_sets(matching, mhs.steps)
    print(bin)
    logging.info("=============sort=images===============")
    for set in sets:
        set = mhs.build_folders(mhs.args, mhs.cwd, set, mhs.steps, mhs.name)
        mhs.move_set(set)
