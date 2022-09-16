use crate::database::PoolType;
use crate::errors::ApiError;
use diesel::prelude::*;
use crate::schema::*;
use crate::diesel::sql_types::{Integer,BigInt,Text,Float,Nullable};
use crate::handlers::stocks::{
    StocksListResponse,
    StocksResponse,
};

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Identifiable, Queryable, Insertable)]
#[primary_key(ticker)]
#[table_name = "stocks"]
pub struct Stock {
    pub ticker: String,
    pub website: Option<String>,
    pub ratio_usd: Option<String>,
    pub marketcap_usd: Option<String>,
    pub price_change: Option<String>,
    pub high_24h: Option<String>,
    pub low_24h: Option<String>,
    pub high_24h_change: Option<String>,
    pub low_24h_change: Option<String>,
    pub short_ratio: Option<String>,
    pub held_per_insiders: Option<String>,
    pub held_per_institutions: Option<String>,
    pub updated_at: i64,
}

#[derive(QueryableByName)]
pub struct StockList {
    #[sql_type = "Text"]
    pub ticker: String,
    #[sql_type = "Nullable<Text>"]
    pub website: Option<String>,
    #[sql_type = "Nullable<Text>"]
    pub ratio_usd: Option<String>,
}

pub fn stock_by_ticker(
    pool: &PoolType,
    tckr: &String,
) -> Result<StocksResponse, ApiError> {
    use crate::schema::stocks::dsl::*;

    let conn = pool.get()?;
    let data: Vec<Stock> = stocks
        .filter(ticker.eq(tckr))
        .select((
            ticker,
            website,
            ratio_usd,
            marketcap_usd,
            price_change,
            high_24h,
            low_24h,
            high_24h_change,
            low_24h_change,
            short_ratio,
            held_per_insiders,
            held_per_institutions,
            updated_at,
        ))
        .load(&conn)?;
    Ok(data.into())
}

/* @todo
 * write a sql statement to select ticker, website, and ratio_usd from the stocks table
 * make sure the rows returned are ordered by marketcap_usd, descending
 * hint: marketcap_usd is a TEXT with commas, we want to order it as an integer
 */
pub fn stocks_list(
    pool: &PoolType,
) -> Result<StocksListResponse, ApiError> {
    use crate::diesel::sql_query;
    let sql_stmt: &str = "
        SELECT
            stocks.ticker AS 'ticker',
            stocks.website AS 'website',
            stocks.ratio_usd AS 'ratio_usd'
        FROM stocks
        ORDER BY CAST(replace(marketcap_usd, ',','') AS INTEGER) DESC
    ";
    let conn = pool.get()?;
    let data: Vec<StockList> = sql_query(
        sql_stmt
    ).get_results(&conn).unwrap();
    Ok(data.into())
}

