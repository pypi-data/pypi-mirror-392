from argparse import ArgumentParser
import glob
import os
import shutil

CLEAN_FILES = "./build ./dist ./*.egg-info dd_data_dictionary.xml dd_data_dictionary_validation.txt IDSDef.xml IDSNames.txt ./html_documentation/*.html ./html_documentation/cocos/ids_cocos_transformations_symbolic_table.csv ./html_documentation/utilities/coordinate_identifier.xml ./install/*.*".split(
    " "
)
EXCEPTION_FILES = "./html_documentation/dd_versions.html".split(" ")

# read config file
PWD = os.path.realpath(os.path.dirname(__file__))


def run(files=None, exception_files=None):
    """
    function for cleanup
    """
    # Retain required file and then later on move them
    exception_file_dict = {}
    if exception_files is not None:
        for path_spec in exception_files:
            # Make paths absolute and relative to this path
            abs_paths = glob.glob(os.path.normpath(os.path.join(PWD, path_spec)))
            for path in [str(p) for p in abs_paths]:
                if not path.startswith(PWD):
                    # Die if path in files is absolute + outside this directory
                    raise ValueError("%s is not a path inside %s" % (path, PWD))
                head, tail = os.path.split(path)
                shutil.copyfile(
                    path,
                    tail,
                )
                exception_file_dict[path] = tail

    print("Removing " + " ".join(files))
    for path_spec in files:
        # Make paths absolute and relative to this path
        abs_paths = glob.glob(os.path.normpath(os.path.join(PWD, path_spec)))

        for path in [str(p) for p in abs_paths]:
            if not path.startswith(PWD):
                # Die if path in files is absolute + outside this directory
                raise ValueError("%s is not a path inside %s" % (path, PWD))
            print("removing %s" % os.path.relpath(path))
            if os.path.isdir(path) and not os.path.islink(path):
                try:
                    shutil.rmtree(path)
                except:
                    print("Error occurred while removing path" + path)

            elif os.path.islink(path):
                try:
                    os.unlink(path)
                except:
                    print("Error occurred while removing path" + path)
            else:
                try:
                    os.remove(path)
                except:
                    print("Error occurred while removing path" + path)

    # Move files
    for original_path, tmp_path in exception_file_dict.items():
        shutil.move(
            tmp_path,
            original_path,
        )


run(CLEAN_FILES, EXCEPTION_FILES)
