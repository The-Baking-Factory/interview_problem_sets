#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <iomanip>
#include <nlohmann/json.hpp>

#include <log4cplus/logger.h>
#include <log4cplus/loggingmacros.h>
#include <log4cplus/configurator.h>

#include "data_operations.h"
#include "parser_thread.h"
#include "file_utilities.h"
#include "guru_sqlite.h"

#define LOG_CONF_FILE "./config/log_conf.yaml"
#define DB_PATH "../../ps2/api/botbunny.db"

using namespace Parser;
using namespace nlohmann;
using namespace GuruSqlite;
using namespace GuruChecks;
using namespace InsertStatements;
using namespace UpdateStatements;
using namespace DeleteStatements;
using namespace Ops;


/**
 * Runs json parsing, calls relevant parse functions
 * @param file_path [in] the file path corresponding to the data json
 * @param data_type [in] the argument structure of data being read
 * @param j [in] the data json
 * @throws UnsupportedCommandException, UnsupportedDatabaseException
 */
void parse_json(
    Database& db,
    const std::string& file_path,
    const std::string& data_type,
    const json& j
) {
    LOG4CPLUS_INFO(logger, LOG4CPLUS_TEXT(data_type+" parse"));
    if (data_type == "stocks") {
        parse_stocks(db, j);
    } else {
        throw UnsupportedCommandException(data_type);
    }
}

int main(int argc, char* argv[]) {

    // logger initialize, config
    initialize();
    PropertyConfigurator config(LOG_CONF_FILE);
    config.configure();

    json j = read_json(argv[1]); // read json
    std::string db_path = DB_PATH; // set database path
    Database db(db_path); // db object
    parse_json(db, argv[1], argv[2], j); // json parse

    return 0;
}