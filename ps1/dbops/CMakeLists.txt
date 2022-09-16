cmake_minimum_required(VERSION 3.15)
project(dbops LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

find_package(nlohmann_json REQUIRED)
find_package(SQLite3 REQUIRED)

find_library(LOG4CPLUS log4cplus)
find_library(GTEST gtest)

include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../common/")

set(LIBS
    "${LOG4CPLUS}")

set(COMMON_FILES
    ../common/file_utilities.h
    ../common/file_utilities.cpp)

set(SCRAPER_FILES
    src/data_operations.cpp
    src/guru_sqlite.cpp)

# main project executable
add_executable(dbops
               src/parse.cpp
               "${SCRAPER_FILES}"
               "${COMMON_FILES}")

# TODO: test executable
#add_executable(run_dbops_gtest
#               tests/run_gtests.cpp
#               tests/test_parser.cpp
#               "${SCRAPER_FILES}"
#               "${COMMON_FILES}")

target_link_libraries(dbops nlohmann_json::nlohmann_json "${LIBS}" sqlite3)
#target_link_libraries(run_dbops_gtest nlohmann_json::nlohmann_json "${LIBS}" sqlite3 "${GTEST}" -pthread)