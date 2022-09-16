#pragma once

#include <fstream>
#include <string>
#include <stdexcept>
#include <stdio.h>
#include <errno.h>
#include <cstring>
#include <vector>

using namespace std;

/**
 * This file holds utility functions for working with regular system files
 * i.e. reading/writing/renaming, etc
 */
namespace FileUtilities {

    //error thrown on file read
    class FileException : public std::invalid_argument {
    public:
        FileException(const std::string& file, const std::string& msg)
            : std::invalid_argument("Failed to read file '" + file + "' due to: " + msg) { }
        FileException(const std::string& msg)
            : std::invalid_argument(msg) { }
    };

    string read_file(const string& fpath);
    void write_file(const string& fpath, const string& contents,
                    const int perms = -1);
    vector<string> get_fnames_from_ext(const string& directory, const string& ext);

    /**
     * RAII wrapper around FILE (used for executing python files)
     * w/ error handling
     */
    class FileDescriptor {
        public:
        FileDescriptor(const string& fpath, const bool caller_will_close = true) {
            cwc = caller_will_close;
            fd = fopen(fpath.c_str(), "r");

            if (!fd) {
                const char* error_str = strerror(errno);
                throw FileUtilities::FileException(fpath, error_str);
            }
        }

        ~FileDescriptor() {
            if (!cwc) {
                fclose(fd);
            }
        }

        FILE* operator()() {
            return fd;
        }

        private:
        FILE* fd;
        bool cwc;
    };
}