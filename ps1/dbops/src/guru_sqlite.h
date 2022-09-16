#pragma once
#include <sqlite3.h>
#include <stdexcept>
#include <string>
#include <stdio.h>
#include <iostream>
#include <log4cplus/logger.h>
#include <log4cplus/loggingmacros.h>

using namespace std;
using namespace log4cplus;

const Logger logger = Logger::getInstance("dbops");

namespace GuruSqlite {

    //forward declaration
    class Database;

    //custom exceptions go here
    class SqliteException : public std::invalid_argument {
    public:
        SqliteException(const std::string& msg) : std::invalid_argument("Database Error: " + msg) { }
    };

    class Statement {
        // essentially wrapper for sqlite3 prepared statement, this will have
        // all stuff related to executing a statement for a specified db (using the
        // db wrapper class below)
        public:
        Statement(Database& db, const char* sql);

        /**
         * Binds the specified param to the value
         * @param name [in] the field name to bind
         * @param val [in] the value to bind to the field
         * @return a reference to the current statement (so we can chain it)
         */
        template<typename T>
        Statement& bind(const char* name, const T& val) {
            const int idx = sqlite3_bind_parameter_index(sqlite_stmt, name);
            if (idx == 0) {
                throw SqliteException("Failed to bind parameter: does not exist");
            }
            bind(idx, val);
            return *this;
        }

        /**
         * Binds the various data type to its param using the generic function above
         */
        void bind(const int idx, const int v) {
            const int rc = sqlite3_bind_int(sqlite_stmt, idx, v);
            if (rc != SQLITE_OK) {
                throw SqliteException(sqlite3_errstr(rc));
            }
        }
        void bind(const int idx, const int64_t v) {
            const int rc = sqlite3_bind_int64(sqlite_stmt, idx, v);
            if (rc != SQLITE_OK) {
                throw SqliteException(sqlite3_errstr(rc));
            }
        }
         void bind(const int idx, const uint64_t v) {
            const int rc = sqlite3_bind_int64(sqlite_stmt, idx, v);
            if (rc != SQLITE_OK) {
                throw SqliteException(sqlite3_errstr(rc));
            }
        }
        /**
         * @todo
         * add a bind for string data type similar to the above
         */
        void bind(const int idx, const string& v) {
            // additional arguments added
            const int rc = sqlite3_bind_text(sqlite_stmt, idx, v.c_str(), -1, SQLITE_STATIC);
            if (rc != SQLITE_OK) {
                throw SqliteException(sqlite3_errstr(rc));
            }
        }
        /**
         * @todo
         * add a bind for double data type similar to the above
         */
        void bind(const int idx, const double v) {
            const int rc = sqlite3_bind_double(sqlite_stmt, idx, v);
            if (rc != SQLITE_OK) {
                throw SqliteException(sqlite3_errstr(rc));
            }
        }

        /**
         * Returns the specified value of the current column being examined
         * by step
         *
         * @param idx [in] the index of the column to retrieve
         * @return the value at the index
         * @throw runtime_error if the column idx is invalid
         *
         * ex: auto size = stmt.column<int>(1);
         *     auto name = stmt.column<string>(5);
         */
        template<typename T>
        T column(const int idx) {
            T v;
            column(idx, v);
            return v;
        }

        /**
         * Gets the value of the current statement at the index
         *
         * @param idx [in] index of the column to retrieve
         * @param out [out] the out parameter to the result value
         * @return a reference to the statement
         * @throw runtime_error if the index is invalid
         */
        void column(const int idx, int &out);
        void column(const int idx, int64_t& out);
        void column(const int idx, bool& out);
        void column(const int idx, std::string& out);

        bool step();
        void exec();

        ~Statement() noexcept {
            if (sqlite_stmt != nullptr) {
                sqlite3_finalize(sqlite_stmt);
            }
        }
        sqlite3_stmt* operator()() {
            return sqlite_stmt;
        }

        private:
        sqlite3_stmt* sqlite_stmt;
        const char* stmt_tail;

        int check_col_index(int i);
    };

    class Database {
        public:
        Database(const string& fpath);
        Statement create_statement(const std::string& sql);

        ~Database() noexcept {
            if (sqlite_ptr != nullptr) {
                if (sqlite3_close(sqlite_ptr) == SQLITE_LOCKED) {
                    LOG4CPLUS_WARN(logger, "Unable to close: Database is locked");
                }
            }
        }
        /**
         * @todo
         * return sqlite3 pointer
         */
        sqlite3* operator()() {
            return sqlite_ptr;
        }
        /**
         * @todo
         * return Database class pointer
         */
        Database& operator*() {
            return *this;
        }

        private:
        sqlite3* sqlite_ptr;
    };

    class Transaction {
        public:
        Transaction(Database& db);
        void commit();
        void rollback();

        private:
        bool done;
        Database& db;
    };
}