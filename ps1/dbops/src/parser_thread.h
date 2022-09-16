#pragma once
#include <log4cplus/logger.h>
#include <ctime>
#include "guru_sqlite.h"
#include "data_operations.h"
#include "file_utilities.h"

using namespace log4cplus;
using namespace nlohmann;
using namespace GuruSqlite;
using namespace GuruChecks;

/* Parser namespace */
namespace Parser {

    //custom exceptions go here
    class UnsupportedCommandException : public std::invalid_argument {
    public:
        UnsupportedCommandException(const std::string& cmd) : std::invalid_argument("The command: \'" + cmd + "\' is not implemented") { }
    };

    /**
     * Reads json file with FileUtilities::read_file
     * @param file_name [in] the file name
     * @return the read json
     * @throws FileUtilities::FileException
     */
    json read_json(const std::string file_name) {

        std::string contents;
        try {
            contents = FileUtilities::read_file(file_name);
        } catch (const FileUtilities::FileException& e) {
            //log and rethrow
            LOG4CPLUS_ERROR(logger, e.what());
            throw FileUtilities::FileException(e.what());
        }

        json out;
        if (!contents.empty()) {
            std::istringstream in_str(contents);
            std::string token;
            out = json::parse(contents);
        }

        return out;
    }

    /**
     * @todo
     * function to get current time as int64
     */
    int64_t get_unix_time() {
        std::time_t unix_time = std::time(nullptr);
        int64_t int_unix_time = *((int64_t*)&unix_time);
        return int_unix_time;
    }

}

/* Insertion Statements namespace */
namespace InsertStatements {

    void insert_stock(
        Database& db,
        stock& stk
    ) {
        /**
         * @todo
         * function to create and execute an insertion statement for stocks, using all the columns
         * hint: don't forget to bind stk struct attributes
         */
        db.create_statement(
            "INSERT INTO stocks (ticker, ratio_usd, marketcap_usd, price_change, high_24h, low_24h, updated_at)"
            " VALUES (:ticker, :ratio_usd, :marketcap_usd, :price_change, :high_24h, :low_24h, :updated_at)")
        .bind(":ticker", stk.ticker)
        .bind(":ratio_usd", stk.ratio_usd)
        .bind(":marketcap_usd", stk.marketcap_usd)
        .bind(":price_change", stk.price_change)
        .bind(":high_24h", stk.high_24h)
        .bind(":low_24h", stk.low_24h)
        .bind(":updated_at", stk.updated_at)
        .exec();
    }

}

/* Update Statements namespace */
namespace UpdateStatements {

    /**
     * @todo
     * function to create and execute an update statement for stocks, using all the columns
     * hint: don't forget to bind stk struct attributes
     */
    void update_stock(
        Database& db,
        stock& stk
    ) {
        std::string update = "UPDATE stocks SET ";
        update += "ratio_usd = :ratio_usd, marketcap_usd = :marketcap_usd, price_change = :price_change";
        update += ", high_24h = :high_24h, low_24h = :low_24h, updated_at = :updated_at";
        update += " WHERE ticker = :ticker";
        Statement update_stmt = db.create_statement(update);
        update_stmt.bind(":ratio_usd", stk.ratio_usd);
        update_stmt.bind(":marketcap_usd", stk.marketcap_usd);
        update_stmt.bind(":price_change", stk.price_change);
        update_stmt.bind(":high_24h", stk.high_24h);
        update_stmt.bind(":low_24h", stk.low_24h);
        update_stmt.bind(":updated_at", stk.updated_at);
        update_stmt.bind(":ticker", stk.ticker);
        update_stmt.exec();
    }
}

/* Delete Statements namespace */
namespace DeleteStatements {

    /**
     * @todo
     * function to create and execute an delete statement for stocks, that deletes every row
     */
    void flush_all_stocks(
        Database& db
    ) {
        std::string flush = "DELETE FROM stocks";
        Statement flush_stmt = db.create_statement(flush);
        flush_stmt.exec();
    }
}

/* db operations */
namespace Ops {

    void parse_stocks(
        Database& db,
        const json& j
        //const std::string& unix_time
    ) {
        // iterate through json items
        for(auto &item : j["parse"]) {
            // if values are not null
            if (!(item["ticker"].is_null())) {
                stock stk;
                stk.ticker = item["ticker"];
                stk.ratio_usd = item["ratio_usd"];
                stk.marketcap_usd = item["marketcap_usd"];
                stk.price_change = item["price_change"];
                stk.high_24h = item["high_24h"];
                stk.low_24h = item["low_24h"];
                stk.updated_at = Parser::get_unix_time();
                /**
                 * @todo
                 * check_id function to check whether ticker exists in stocks table, in which case update, o/w insert
                 */
                if (check_id(db, stk.ticker, "SELECT COUNT (DISTINCT ticker) FROM stocks WHERE ticker = :ticker", ":ticker")) {
                    LOG4CPLUS_INFO(logger, "UPDATE: "+stk.ticker);
                    UpdateStatements::update_stock(db, stk);
                } else {
                    LOG4CPLUS_INFO(logger, "INSERT: "+stk.ticker);
                    InsertStatements::insert_stock(db, stk);
                }
            }
        }
    }
}