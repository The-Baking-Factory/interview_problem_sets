/* Request param structs */

#[derive(Debug, Deserialize)]
pub struct StockParams {
    pub ticker: String,
}

#[derive(Debug, Deserialize)]
pub struct ServerParams {
    pub server_id: String,
}