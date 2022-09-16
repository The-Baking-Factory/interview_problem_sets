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
    std::string ticker;
    std::string ratio_usd;
    std::string marketcap_usd;
    std::string price_change;
    std::string high_24h;
    std::string low_24h;
    int64_t updated_at;
    // base constructor
    stock() {
        ticker = "";
        ratio_usd = "";
        marketcap_usd = "";
        price_change = "";
        high_24h = "";
        low_24h = "";
        updated_at = 0;
    }
};