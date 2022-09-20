#pragma once

#include <string>
#include <vector>
#include <map>

#include "guru_sqlite.h"

using namespace GuruSqlite;

namespace GuruChecks {

    //custom exceptions go here
    class CheckException : public std::invalid_argument {
    public:
        CheckException(const std::string& msg) : std::invalid_argument("Data Error: " + msg) { }
    };

    bool check_id(Database& db, const std::string& id, const char* sql, const char* id_name);

}

/**
 * @todo
 * create a struct for stock objects based on the schema
 * hint: don't forget a base constructor in the struct
 */
struct stock {
    // these are strings because the purpose is for display
    // need to be formatted during the scrape, before insertion
    // formatting not handled in these scripts
    /* TODO */
};