use crate::database::PoolType;
use crate::errors::ApiError;
use crate::helpers::{respond_json};
use actix_web::web::{block, Data, Json, Query};
use rayon::prelude::*;
use serde::Serialize;
use crate::models::stocks::{
    stock_by_ticker,
    stocks_list,
    Stock,
    StockList,
};
use crate::handlers::params::{
    StockParams
};

#[derive(Debug, Deserialize, Serialize, PartialEq)]
pub struct StockResponse {
    ticker: String,
    ratio_usd: Option<String>,
    marketcap_usd: Option<String>,
    price_change: Option<String>,
    high_24h: Option<String>,
    low_24h: Option<String>,
    updated_at: i64,
}

#[derive(Debug, Deserialize, Serialize, PartialEq)]
pub struct StockListResponse {
    ticker: String,
    ratio_usd: Option<String>,
}

#[derive(Debug, Deserialize, Serialize, PartialEq)]
pub struct StocksResponse(pub Vec<StockResponse>);

#[derive(Debug, Deserialize, Serialize, PartialEq)]
pub struct StocksListResponse(pub Vec<StockListResponse>);

pub async fn get_stock_by_ticker(
    Query(param): Query<StockParams>,
    pool: Data<PoolType>,
) -> Result<Json<StocksResponse>, ApiError> {
    let stocks = block(move || stock_by_ticker(&pool, &param.ticker)).await?;
    respond_json(stocks)
}

pub async fn get_stocks_list(
    pool: Data<PoolType>,
) -> Result<Json<StocksListResponse>, ApiError> {
    let stocks = block(move || stocks_list(&pool)).await?;
    respond_json(stocks)
}

impl From<Stock> for StockResponse {
    fn from(s: Stock) -> Self {
        StockResponse {
            ticker: s.ticker.to_string(),
            ratio_usd: s.ratio_usd.to_owned(),
            marketcap_usd: s.marketcap_usd.to_owned(),
            price_change: s.price_change.to_owned(),
            high_24h: s.high_24h.to_owned(),
            low_24h: s.low_24h.to_owned(),
            updated_at: s.updated_at,
        }
    }
}

impl From<StockList> for StockListResponse {
    fn from(s: StockList) -> Self {
        StockListResponse {
            ticker: s.ticker.to_string(),
            ratio_usd: s.ratio_usd.to_owned(),
        }
    }
}

impl From<Vec<Stock>> for StocksResponse {
    fn from(gs: Vec<Stock>) -> Self {
        StocksResponse(gs.into_par_iter().map(|g| g.into()).collect())
    }
}

impl From<Vec<StockList>> for StocksListResponse {
    fn from(gs: Vec<StockList>) -> Self {
        StocksListResponse(gs.into_par_iter().map(|g| g.into()).collect())
    }
}

