import re
import os
import sys
import zipfile
import argparse


def find_matches(archive, pattern):
    regex = re.compile(pattern)
    for f in archive.filelist:
        if not f.is_dir() and regex.match(f.filename):
            yield f.filename


def extract_file(archive, filename, directory):
    basename = os.path.basename(filename)
    dest = os.path.join(directory, basename)
    if os.path.exists(dest):
        print('File %s already exists in directory %s' % (basename, directory))
    else:
        print('Extracting file %s' % basename)
        content = archive.read(filename)
        with open(dest, 'w') as f:
            f.write(content.decode())


def extract_matches(archivename, pattern, directory):
    archive = zipfile.ZipFile(archivename)
    for filename in find_matches(archive, pattern):
        extract_file(archive, filename, directory)


def main(args):
    parser = argparse.ArgumentParser(description='Extraction of files in a .zip archive according to a pattern')
    parser.add_argument('archive', type=str,
                        help='The archive to extract files from')
    parser.add_argument('regex', type=str,
                        help='A regex specifying the pattern to match')
    parser.add_argument('--output', '-o', type=str, default='/tmp',
                        help='The destination directory for the files')
    args = parser.parse_args(args)
    try:
        extract_matches(args.archive, args.regex, args.output)
    except FileNotFoundError:
        sys.exit('File %s does not exist' % args.archive)
    except zipfile.BadZipfile:
        sys.exit('File %s is not a ZIP archive' % args.archive)
    except re.error:
        sys.exit('Pattern "%s" is not a valid regular expression' % args.regex)


if __name__ == '__main__':
    main(sys.argv[1:])
