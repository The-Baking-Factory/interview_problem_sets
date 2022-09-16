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
        CheckException(const std::string& msg) : std::invalid_argument("Data error: " + msg) { }
    };

    bool check_id(Database& db, const std::string& id, const char* sql, const char* id_name);

}

// standard struct
struct stock {
    // these are strings because the purpose is for display
    // need to be formatted during the scrape, before insertion
    // formatting not handled in these scripts
    std::string ticker;
    std::string website;
    std::string ratio_usd;
    std::string marketcap_usd;
    std::string price_change;
    std::string high_24h;
    std::string low_24h;
    std::string high_24h_change;
    std::string low_24h_change;
    std::string short_ratio;
    std::string held_per_insiders;
    std::string held_per_institutions;
    int64_t updated_at;
    // base constructor
    stock() {
        ticker = "";
        website = "";
        ratio_usd = "";
        marketcap_usd = "";
        price_change = "";
        high_24h = "";
        low_24h = "";
        high_24h_change = "";
        low_24h_change = "";
        short_ratio = "";
        held_per_insiders = "";
        held_per_institutions = "";
        updated_at = 0;
    }
};