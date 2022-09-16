#include "guru_sqlite.h"

using namespace GuruSqlite;
using namespace std;

/**
 * Constructor which loads the sqlite3 DB ptr
 *
 * @throws runtime_error if the connection is unable to be established
 */
Database::Database(const string& fpath) {
    if (sqlite3_open_v2(fpath.c_str(), &(Database::sqlite_ptr),
                        SQLITE_OPEN_READWRITE, NULL) != SQLITE_OK)
	{
        // throw runtime error if we can't open the db just fail
        throw runtime_error(sqlite3_errmsg(Database::sqlite_ptr));
    }
}

/**
 * Creates a statement for the current db instance
 * @param sql [in] the sql for the statement
 */
Statement Database::create_statement(const string& sql) {
	return Statement(*this, sql.c_str());
}

//Statement stuff goes here
Statement::Statement(Database& db, const char* sql) {
    int rc = sqlite3_prepare_v2(db(), sql, -1, &sqlite_stmt, &stmt_tail);
    if (rc != SQLITE_OK) {
        throw SqliteException(sqlite3_errstr(rc));
    } else {
        LOG4CPLUS_INFO(logger, LOG4CPLUS_TEXT("DB STATEMENT '"+string(sql)+"' OK"));
    }
}

/**
 * Returns the index if it is valid, throws sqlite exception if not
 * @param stmt [in] the sqlite_stmt to check
 * @param i [in] the index
 * @return the index if valid
 */
int Statement::check_col_index(int i) {
	int cols = sqlite3_column_count(sqlite_stmt);
	if (i < 0 || i > cols) {
		throw SqliteException("Index " + to_string(i) + " is out of bounds");
	}
	return i;
}

void Statement::column(const int idx, int& out) {
	out = sqlite3_column_int(sqlite_stmt, check_col_index(idx));
}

void Statement::column(const int idx, int64_t& out) {
	out = sqlite3_column_int64(sqlite_stmt, check_col_index(idx));
}

void Statement::column(const int idx, bool& out) {
	out = sqlite3_column_int(sqlite_stmt, check_col_index(idx));
}

void Statement::column(const int idx, string& out) {
	out = string(reinterpret_cast<const char*>(
		sqlite3_column_text(sqlite_stmt, check_col_index(idx))),
		sqlite3_column_bytes(sqlite_stmt, check_col_index(idx)));
}

/**
 * Steps once through the current statement
 * @return true if there currently is data or the statement has finished successfully
 */
bool Statement::step() {
	int rc = sqlite3_step(sqlite_stmt);

	if (rc == SQLITE_ROW) {
		return true;
	}
	//statement finished successfully
	else if (rc == SQLITE_DONE) {
		return false;
	}
	else if (rc == SQLITE_BUSY) {
		throw SqliteException("Database engine was unable to aquire the lock for step");
	}
	else if (rc == SQLITE_ERROR) {
		throw SqliteException(sqlite3_errstr(rc));
	}
	else if (rc == SQLITE_MISUSE) {
		throw SqliteException("Step was called innappropriately");
	}
	return false;
}

/**
 * Executes the specified sql commands without getting any values
 * @param sql [in] the sql to execute
 */
void Statement::exec() {
	while(step());
}

Transaction::Transaction(Database& db) : db(db), done(false) {
	db.create_statement("BEGIN TRANSACTION;")
	  .exec();
}

/**
 * Commits the current transaction
 */
void Transaction::commit() {
	if (!done) {
		db.create_statement("COMMIT;")
	  	  .exec();
		done = true;
	}
	else {
		throw SqliteException("The transaction cannot be committed, it is already over");
	}
}

/**
 * Rolls back the current transaction
 */
void Transaction::rollback() {
	if (!done) {
		db.create_statement("ROLLBACK;")
	      .exec();
	}
	else {
		throw SqliteException("The transaction cannot be rollbacked, it is already over");
	}
}