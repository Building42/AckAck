#!/usr/bin/env python
"""AckAck acknowledgements generator."""

import getopt
import codecs
import os
import plistlib
import re
import sys

VERSION = '2.0'


def main():
    """Main entry point of application."""

    # Process input arguments
    try:
        opts, _ = getopt.getopt(
            sys.argv[1:],
            'hqvni:o:d:',
            ['help', 'quiet', 'version', 'no-clean',
             'input=', 'output=', 'max-depth=']
        )

    except getopt.GetoptError as err:
        print str(err)
        print ''
        show_help()
        sys.exit(2)

    # Arguments
    input_folder = None
    output_folder = None
    max_depth = 1
    clean_up = True
    quiet = False

    # Handle input arguments
    for option, arg in opts:
        if option in ("-h", "--help"):
            show_help()
            sys.exit()
        elif option in ("-q", "--quiet"):
            quiet = True
        elif option in ("-v", "--version"):
            print 'AckAck ' + VERSION
            sys.exit()
        elif option in ("-i", "--input"):
            input_folder = arg
        elif option in ("-o", "--output"):
            output_folder = arg
        elif option in ("-d", "--max-depth"):
            max_depth = int(arg)
        elif option in ("-n", "--no-clean"):
            clean_up = False
        else:
            assert False, "unhandled option"

    # No input folder? Find it
    if input_folder is None:
        input_folder = find_input_folder(quiet)

    # No output folder? Find it
    if output_folder is None:
        output_folder = find_output_folder(quiet)

    # Generate the acknowledgements
    generate(input_folder, output_folder, max_depth, clean_up, quiet)


def find_input_folder(quiet):
    """Finds the input folder based on the location of the Carthage folder."""

    # Find the Carthage Checkouts folder
    input_folder = find_folder(os.getcwd(), 'Carthage/Checkouts')

    # Otherwise look for the CocoaPods Pods folder
    if input_folder is None:
        input_folder = find_folder(os.getcwd(), 'Pods')

    # Still no input folder?
    if input_folder is None:
        print 'Input folder could not be detected, please specify it with -i or --input'
        sys.exit(2)
    elif not os.path.isdir(input_folder):
        print 'Input folder ' + input_folder + " doesn't exist or is not a folder"
        sys.exit(2)
    elif not quiet:
        print 'Input folder: ' + str(input_folder)

    return input_folder


def find_output_folder(quiet):
    """Finds the output folder based on the location of the Settings.bundle."""

    # Find the Settings.bundle
    output_folder = find_folder(os.getcwd(), 'Settings.bundle')

    # Still no output folder?
    if output_folder is None:
        print 'Output folder could not be detected, please specify it with -o or --output'
        sys.exit(2)
    elif not os.path.isdir(output_folder):
        print 'Output folder ' + output_folder + "doesn't exist or is not a folder"
        sys.exit(2)
    elif not quiet:
        print 'Output folder: ' + str(output_folder)

    return output_folder


def show_help():
    """Shows the help information."""

    print 'OVERVIEW:'
    print '  AckAck ' + VERSION + ' - Acknowledgements Plist Generator'
    print ''
    print '  Generates a Settings.plist for iOS based on your Carthage or CocoaPods frameworks.'
    print '  Visit https://github.com/Building42/AckAck for more information.'
    print ''
    print 'USAGE:'
    print ' ./ackack.py [options]'
    print ''
    print 'OPTIONS:'
    print '  -i or --input        manually provide the path to the input folder, e.g. Carthage/Checkouts'
    print '  -o or --output       manually provide the path to the output folder, e.g. MyProject/Settings.bundle'
    print '  -d or --depth        specify the maximum folder depth to look for licenses'
    print '  -n or --no-clean     do not remove existing license plists'
    print ''
    print '  -h or --help         displays the help information'
    print '  -q or --quiet        do not generate any output unless there are errors'
    print '  -v or --version      dispays the version information'
    print ''
    print 'If you run without any options, it will try to find the folders for you.'
    print 'This usually works fine if the script is in the project root or in a Scripts subfolder.'


def find_folder(base_path, search):
    """Finds a folder recursively."""

    # First look in the script's folder
    if search.startswith(os.path.basename(base_path)) and os.path.isdir(base_path):
        return base_path
    if os.path.isdir(os.path.join(base_path, search)):
        return os.path.join(base_path, search)

    # Look in subfolders
    for root, dirs, _ in os.walk(base_path):
        for dir_name in dirs:
            if search.startswith(dir_name):
                result = os.path.join(root, search)
                if os.path.isdir(result):
                    return result

    parent_path = os.path.abspath(os.path.join(base_path, '..'))

    # Try parent folder if it contains a Cartfile
    if os.path.exists(os.path.join(parent_path, 'Cartfile')):
        return find_folder(parent_path, search)

    # Try parent folder if it contains a Podfile
    if os.path.exists(os.path.join(parent_path, 'Podfile')):
        return find_folder(parent_path, search)

    return None


def generate(input_folder, output_folder, max_depth, clean_up, quiet):
    """Generates the acknowledgements."""
    frameworks = []

    # Create license folder path
    plists_path = os.path.join(output_folder, 'Licenses')
    if not os.path.exists(plists_path):
        if not quiet:
            print 'Creating Licenses folder'
        os.makedirs(plists_path)
    elif clean_up:
        if not quiet:
            print 'Removing old license plists'
        remove_files(plists_path, ".plist", quiet)

    # Scan the input folder for licenses
    if not quiet:
        print 'Searching licenses...'

    for root, _, files in os.walk(input_folder):
        for file_name in files:
            # Igore licenses in deep folders
            relative_path = os.path.relpath(root, input_folder)
            if relative_path.count(os.path.sep) >= max_depth:
                continue

            # Look for license files
            l_filename = file_name.lower()
            if l_filename.endswith('license') or l_filename.endswith('license.txt') or l_filename.endswith('license.md'):
                license_path = os.path.join(root, file_name)

                # We found a license
                framework = os.path.basename(os.path.dirname(license_path))
                frameworks.append(framework)
                if not quiet:
                    print 'Creating license plist for ' + framework

                # Generate a plist
                plist_path = os.path.join(plists_path, framework + '.plist')
                create_license_plist(license_path, plist_path)

    # Did we find any licenses?
    if not quiet and not frameworks:
        print 'No licenses found'

    # Create the acknowledgements plist
    if not quiet:
        print 'Creating acknowledgements plist'

    plist_path = os.path.join(output_folder, 'Acknowledgements.plist')
    create_acknowledgements_plist(frameworks, plist_path)


def create_license_plist(license_path, plist_path):
    """Generates a plist for a single license, start with reading the license."""

    # Read and clean up the text
    license_text = codecs.open(license_path, 'r', 'utf-8').read()
    license_text = license_text.replace('  ', ' ')
    license_text = re.sub(
        r'(\S)[ \t]*(?:\r\n|\n)[ \t]*(\S)', '\\1 \\2',
        license_text
    )

    # Create the plist
    plistlib.writePlist({
        'PreferenceSpecifiers': [{
            'Type': 'PSGroupSpecifier',
            'FooterText': license_text
        }]
    }, plist_path)


def create_acknowledgements_plist(frameworks, plist_path):
    """Generates a plist combining all the licenses."""
    licenses = []

    # Walk through the frameworks
    for framework in sorted(frameworks):
        licenses.append({
            'Type': 'PSChildPaneSpecifier',
            'File': 'Licenses/' + framework, 'Title': framework
        })

    # Create the plist
    plistlib.writePlist(
        {'PreferenceSpecifiers': licenses},
        plist_path
    )


def remove_files(folder, extension, quiet):
    """Removes files with a specific extension from a folder."""

    for root, _, files in os.walk(folder):
        for file_name in files:
            if file_name.endswith(extension):
                full_path = os.path.join(root, file_name)
                try:
                    os.remove(full_path)
                except OSError:
                    if not quiet:
                        print 'Could not remove ' + full_path


# Main entry point
if __name__ == "__main__":
    main()
