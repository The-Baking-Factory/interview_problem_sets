#include "data_operations.h"

using namespace GuruChecks;

bool GuruChecks::check_id(
    Database& db,
    const std::string& id,
    const char* sql,
    const char* id_name
) {
    bool found = false;
    Statement select_stmt = db.create_statement(sql);
    select_stmt.bind(id_name,id);
    select_stmt.step();
    int id_count = select_stmt.column<int>(0);
    if (id_count > 0) {
        found = true;
    }
    return found;
}