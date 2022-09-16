#include <fstream>
#include <string>
#include <stdexcept>
#include <stdio.h>
#include <errno.h>
#include <cstring>
#include <sys/stat.h>
#include <filesystem>

#include "file_utilities.h"

using namespace std;

/**
 * Reads the specified file into a string and returns it
 *
 * @param fpath [in] the path to the file to read
 *
 * @return a string with the file contents
 * @throws ReadFileException if read_file fails for ANY reason
 */
string FileUtilities::read_file(const string& fpath) {
    ifstream file_in;
    file_in.open(fpath, ifstream::in);
    if (!file_in.is_open() || !file_in.good()) {
        const char* error_str = strerror(errno);
        throw FileUtilities::FileException(fpath, error_str);
    }

    return string( (istreambuf_iterator<char>(file_in) ),
                    (istreambuf_iterator<char>() ));
}

/**
 * Writes the contents to the file path, creates a new file if it
 * doesn't already exist
 *
 * @param fpath [in] the path to the file to read
 * @param contents [in] the contents to write
 * @param perms [in] the unix file permissions bit (none by default)
 */
void FileUtilities::write_file(const string& fpath, const string& contents,
                               const int perms)
{
    ofstream file_out;

    file_out.open(fpath, ios::out | ios::trunc);
    if (!file_out.is_open() || !file_out.good()) {
        const char* error_str = strerror(errno);
        throw FileUtilities::FileException(fpath, error_str);
    }

    file_out << contents;
    file_out.close();

    //set new file permissions if applicable
    if (perms != -1) {
        if (chmod(fpath.c_str(), perms) != 0) {
            const char* error_str = strerror(errno);
            throw FileUtilities::FileException(fpath, error_str);
        }
    }
}

/**
 * Gets all filenames in the specified directory with the specified
 * file extension
 *
 * @param directory [in] the directory to check from
 * @param ext [in] the file extension
 */
vector<string> FileUtilities::get_fnames_from_ext(const string& directory,
                                                  const string& ext)
{
    vector<string> out;
    for (const auto& p : std::filesystem::recursive_directory_iterator(directory)) {
        if (p.path().extension() == ext) {
            out.push_back(p.path().string());
        }
    }
    return out;
}