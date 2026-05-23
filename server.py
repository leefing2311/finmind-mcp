"""FinMind MCP Server v3 - COMPLETE coverage of all 75+ FinMind datasets.

Coverage:
- Taiwan: 53 datasets (技術/籌碼/基本面/即時/可轉債/期貨選擇權/其他)
- International: 9 datasets (美股/英股/歐股/日股)
- Global Economic: 6 datasets (匯率/利率/黃金/原油/美債/CNN恐慌指數)

Tier markers:
- [Free]    : 免費版 + token (600 req/hr) 即可使用
- [Backer]  : 需小額贊助會員
- [Sponsor] : 需高階贊助會員（含即時 tick、分 K、分點等）
"""
import os
import logging
from typing import Optional
import httpx
from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

FINMIND_TOKEN = os.environ.get("FINMIND_TOKEN", "")
FINMIND_API = "https://api.finmindtrade.com/api/v4/data"
FINMIND_REPORT_API = "https://api.finmindtrade.com/api/v4/taiwan_stock_trading_daily_report"
FINMIND_SECID_AGG_API = "https://api.finmindtrade.com/api/v4/taiwan_stock_trading_daily_report_secid_agg"
PORT = int(os.environ.get("PORT", "8000"))

mcp = FastMCP("FinMind Taiwan Stock MCP")


async def _query(dataset: str, **params) -> dict:
    """Generic FinMind API query with Bearer auth."""
    clean = {"dataset": dataset}
    for k, v in params.items():
        if v is not None and v != "":
            clean[k] = v
    headers = {"Authorization": f"Bearer {FINMIND_TOKEN}"} if FINMIND_TOKEN else {}
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(FINMIND_API, params=clean, headers=headers)
        r.raise_for_status()
        return r.json()


async def _query_custom(url: str, **params) -> dict:
    """Custom endpoint query (for non-/data routes)."""
    clean = {k: v for k, v in params.items() if v is not None and v != ""}
    headers = {"Authorization": f"Bearer {FINMIND_TOKEN}"} if FINMIND_TOKEN else {}
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(url, params=clean, headers=headers)
        r.raise_for_status()
        return r.json()


# ============================================================
# 一、台股總覽 / 交易日 (4 個)
# ============================================================

@mcp.tool
async def get_stock_info(stock_id: Optional[str] = None) -> dict:
    """[Free] 台股總覽（產業、ISIN、上市日）。不傳 stock_id 回全市場。"""
    return await _query("TaiwanStockInfo", data_id=stock_id)


@mcp.tool
async def get_stock_info_with_warrant() -> dict:
    """[Free] 台股總覽含權證。"""
    return await _query("TaiwanStockInfoWithWarrant")


@mcp.tool
async def get_warrant_target_mapping(stock_id: str, start_date: str) -> dict:
    """[Sponsor] 台股權證標的對照表。"""
    return await _query("TaiwanStockInfoWithWarrantSummary", data_id=stock_id, start_date=start_date)


@mcp.tool
async def get_trading_dates() -> dict:
    """[Free] 台股交易日列表。"""
    return await _query("TaiwanStockTradingDate")


# ============================================================
# 二、技術面 / 股價 K 線 (12 個)
# ============================================================

@mcp.tool
async def get_stock_price(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 個股日 K 線 OHLCV（上市/上櫃/興櫃皆可）。資料起 1994-10-01。"""
    return await _query("TaiwanStockPrice", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_stock_price_adj(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 還原股價（除權息已還原），長期報酬計算用。"""
    return await _query("TaiwanStockPriceAdj", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_stock_tick(stock_id: str, start_date: str) -> dict:
    """[Backer/Sponsor] 個股歷史逐筆 tick（單日）。"""
    return await _query("TaiwanStockPriceTick", data_id=stock_id, start_date=start_date)


@mcp.tool
async def get_stock_per_pbr(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 個股本益比 PER、股價淨值比 PBR、殖利率。"""
    return await _query("TaiwanStockPER", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_5sec_order_stats(start_date: str) -> dict:
    """[Free] 每 5 秒委託成交統計（單日）。"""
    return await _query("TaiwanStockStatisticsOfOrderBookAndTrade", start_date=start_date)


@mcp.tool
async def get_taiex_5sec(start_date: str) -> dict:
    """[Free] 加權指數每 5 秒走勢（單日）。"""
    return await _query("TaiwanVariousIndicators5Seconds", start_date=start_date)


@mcp.tool
async def get_day_trading(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 當沖交易標的及成交量值。"""
    return await _query("TaiwanStockDayTrading", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_total_return_index(index_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 加權/櫃買報酬指數。index_id: 'TAIEX' 或 'TPEx'。"""
    return await _query("TaiwanStockTotalReturnIndex", data_id=index_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_stock_10year(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 個股 10 年線資料。"""
    return await _query("TaiwanStock10Year", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_stock_kbar_minute(stock_id: str, start_date: str) -> dict:
    """[Sponsor] 分 K（單日）。"""
    return await _query("TaiwanStockKBar", data_id=stock_id, start_date=start_date)


@mcp.tool
async def get_stock_week_price(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 週 K。"""
    return await _query("TaiwanStockWeekPrice", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_stock_month_price(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 月 K。"""
    return await _query("TaiwanStockMonthPrice", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_every_5sec_index(start_date: str) -> dict:
    """[Backer/Sponsor] 每 5 秒指數統計（單日）。"""
    return await _query("TaiwanStockEvery5SecondsIndex", start_date=start_date)


@mcp.tool
async def get_suspended(start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 暫停交易公告。"""
    return await _query("TaiwanStockSuspended", start_date=start_date, end_date=end_date)


@mcp.tool
async def get_day_trading_suspension(start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 暫停先賣後買當沖預告。"""
    return await _query("TaiwanStockDayTradingSuspension", start_date=start_date, end_date=end_date)


@mcp.tool
async def get_stock_price_limit(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 每日漲跌停價（含 ETF 槓桿型、興櫃無漲跌幅）。"""
    return await _query("TaiwanStockPriceLimit", data_id=stock_id, start_date=start_date, end_date=end_date)


# ============================================================
# 三、籌碼面 / 法人 / 融資融券 (18 個)
# ============================================================

@mcp.tool
async def get_margin_purchase_short_sale(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 個股融資融券餘額連續多日。"""
    return await _query("TaiwanStockMarginPurchaseShortSale", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_total_margin_purchase(start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 整體市場融資融券彙總。"""
    return await _query("TaiwanStockTotalMarginPurchaseShortSale", start_date=start_date, end_date=end_date)


@mcp.tool
async def get_institutional_investors(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 個股三大法人連續多日買賣超（外資/投信/自營）。上市/上櫃/興櫃通吃。"""
    return await _query("TaiwanStockInstitutionalInvestorsBuySell", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_total_institutional_investors(start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 整體三大市場法人買賣彙總。"""
    return await _query("TaiwanStockTotalInstitutionalInvestors", start_date=start_date, end_date=end_date)


@mcp.tool
async def get_foreign_shareholding(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 外資及陸資持股表（持股比率、剩餘可買額度）。"""
    return await _query("TaiwanStockShareholding", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_holding_shares_per(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 股權持股分級表（持股級距人數）。"""
    return await _query("TaiwanStockHoldingSharesPer", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_securities_lending(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 借券成交明細。"""
    return await _query("TaiwanStockSecuritiesLending", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_margin_short_sale_suspension(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 暫停融券賣出（除權息平盤下不得放空）。"""
    return await _query("TaiwanStockMarginShortSaleSuspension", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_daily_short_sale_balances(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 信用額度總量管制餘額表（融券/借券融券）。"""
    return await _query("TaiwanDailyShortSaleBalances", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_securities_trader_info() -> dict:
    """[Free] 證券商資訊（券商編號對照名稱）。"""
    return await _query("TaiwanSecuritiesTraderInfo")


@mcp.tool
async def get_trading_daily_report(stock_id: Optional[str] = None, 
                                   securities_trader_id: Optional[str] = None,
                                   date: Optional[str] = None) -> dict:
    """[Sponsor] 台股分點資料（單日）。可由個股或券商查詢。專屬 endpoint。"""
    return await _query_custom(FINMIND_REPORT_API, data_id=stock_id, 
                                securities_trader_id=securities_trader_id, date=date)


@mcp.tool
async def get_warrant_trading_daily_report(stock_or_broker_id: str, start_date: str) -> dict:
    """[Sponsor] 台股權證分點資料。data_id 可為權證代號或券商代號。"""
    return await _query("TaiwanStockWarrantTradingDailyReport", data_id=stock_or_broker_id, start_date=start_date)


@mcp.tool
async def get_government_bank_buysell(start_date: str, end_date: Optional[str] = None) -> dict:
    """[Sponsor] 台股八大行庫買賣（國安基金概念）。"""
    return await _query("TaiwanstockGovernmentBankBuySell", start_date=start_date, end_date=end_date)


@mcp.tool
async def get_total_exchange_margin_maintenance(start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 台灣大盤融資維持率。"""
    return await _query("TaiwanTotalExchangeMarginMaintenance", start_date=start_date, end_date=end_date)


@mcp.tool
async def get_trading_daily_report_secid_agg(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Sponsor] 當日券商分點統計表。專屬 endpoint。"""
    return await _query_custom(FINMIND_SECID_AGG_API, data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_block_trading_daily_report(start_date: str, end_date: Optional[str] = None) -> dict:
    """[Sponsor] 鉅額交易買賣日報表。"""
    return await _query("TaiwanStockBlockTradingDailyReport", start_date=start_date, end_date=end_date)


@mcp.tool
async def get_block_trade(stock_id: Optional[str], start_date: str, end_date: Optional[str] = None) -> dict:
    """[Sponsor] 鉅額交易日成交資訊。"""
    return await _query("TaiwanStockBlockTrade", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_loan_collateral_balance(stock_id: Optional[str], start_date: str, end_date: Optional[str] = None) -> dict:
    """[Sponsor] 借貸款項擔保品餘額表。"""
    return await _query("TaiwanStockLoanCollateralBalance", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_disposition_securities(stock_id: Optional[str], start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 公布處置有價證券表。"""
    return await _query("TaiwanStockDispositionSecuritiesPeriod", data_id=stock_id, start_date=start_date, end_date=end_date)


# ============================================================
# 四、基本面 / 財報 (12 個)
# ============================================================

@mcp.tool
async def get_income_statement(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 綜合損益表（季報）。上市/上櫃/興櫃皆支援。"""
    return await _query("TaiwanStockFinancialStatements", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_balance_sheet(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 資產負債表（季報）。上市/上櫃/興櫃皆支援。"""
    return await _query("TaiwanStockBalanceSheet", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_cash_flow(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 現金流量表（季報）。上市/上櫃/興櫃皆支援。"""
    return await _query("TaiwanStockCashFlowsStatement", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_dividend_policy(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 股利政策表（除權除息預告）。"""
    return await _query("TaiwanStockDividend", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_dividend_result(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 除權除息結果表（含填權息表現）。"""
    return await _query("TaiwanStockDividendResult", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_monthly_revenue(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 個股每月營收。上市/上櫃/興櫃皆支援。"""
    return await _query("TaiwanStockMonthRevenue", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_capital_reduction(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 減資恢復買賣參考價格。"""
    return await _query("TaiwanStockCapitalReductionReferencePrice", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_stock_market_value(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 個股市值連續多日。"""
    return await _query("TaiwanStockMarketValue", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_delisting() -> dict:
    """[Free] 台股下市櫃名單。"""
    return await _query("TaiwanStockDelisting")


@mcp.tool
async def get_market_value_weight(stock_id: Optional[str], start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 台股市值比重表（含上市/上櫃 type 區分）。"""
    return await _query("TaiwanStockMarketValueWeight", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_split_price() -> dict:
    """[Free] 台股分割後參考價。"""
    return await _query("TaiwanStockSplitPrice")


@mcp.tool
async def get_par_value_change(start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 台股變更面額恢復買賣參考價格。"""
    return await _query("TaiwanStockParValueChange", start_date=start_date, end_date=end_date)


# ============================================================
# 五、期貨 / 選擇權 (16 個)
# ============================================================

@mcp.tool
async def get_futures_overview() -> dict:
    """[Free] 期貨選擇權商品總覽（商品代號列表）。"""
    return await _query("TaiwanFutOptDailyInfo")


@mcp.tool
async def get_futures_daily(futures_id: Optional[str], start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 期貨日成交（TX 台指期/MTX 小台/TE 電子期）。不傳 id 取全部。"""
    return await _query("TaiwanFuturesDaily", data_id=futures_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_option_daily(option_id: Optional[str], start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 選擇權日成交（TXO 台指選）。不傳 id 取全部。"""
    return await _query("TaiwanOptionDaily", data_id=option_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_futures_tick(futures_id: str, start_date: str) -> dict:
    """[Backer/Sponsor] 期貨交易明細（單日 tick）。"""
    return await _query("TaiwanFuturesTick", data_id=futures_id, start_date=start_date)


@mcp.tool
async def get_option_tick(option_id: str, start_date: str) -> dict:
    """[Backer/Sponsor] 選擇權交易明細（單日 tick）。"""
    return await _query("TaiwanOptionTIck", data_id=option_id, start_date=start_date)


@mcp.tool
async def get_futures_institutional(futures_id: Optional[str], start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 期貨三大法人買賣。"""
    return await _query("TaiwanFuturesInstitutionalInvestors", data_id=futures_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_option_institutional(option_id: Optional[str], start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 選擇權三大法人買賣（分 Call/Put）。"""
    return await _query("TaiwanOptionInstitutionalInvestors", data_id=option_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_futures_institutional_after_hours(futures_id: Optional[str], start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 期貨夜盤三大法人買賣。"""
    return await _query("TaiwanFuturesInstitutionalInvestorsAfterHours", data_id=futures_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_option_institutional_after_hours(option_id: Optional[str], start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 選擇權夜盤三大法人買賣。"""
    return await _query("TaiwanOptionInstitutionalInvestorsAfterHours", data_id=option_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_futures_dealer_daily(futures_id: Optional[str], start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 期貨各券商每日交易。"""
    return await _query("TaiwanFuturesDealerTradingVolumeDaily", data_id=futures_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_option_dealer_daily(option_id: Optional[str], start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 選擇權各券商每日交易。"""
    return await _query("TaiwanOptionDealerTradingVolumeDaily", data_id=option_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_futures_oi_large_traders(futures_id: Optional[str], start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 期貨大額交易人未沖銷部位。"""
    return await _query("TaiwanFuturesOpenInterestLargeTraders", data_id=futures_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_option_oi_large_traders(option_id: Optional[str], start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 選擇權大額交易人未沖銷部位。"""
    return await _query("TaiwanOptionOpenInterestLargeTraders", data_id=option_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_futures_spread(futures_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 期貨價差行情表。"""
    return await _query("TaiwanFuturesSpreadTrading", data_id=futures_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_futures_settlement(futures_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 期貨最後結算價。"""
    return await _query("TaiwanFuturesFinalSettlementPrice", data_id=futures_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_option_settlement(option_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 選擇權最後結算價。"""
    return await _query("TaiwanOptionFinalSettlementPrice", data_id=option_id, start_date=start_date, end_date=end_date)


# ============================================================
# 六、即時報價 (4 個)
# ============================================================

@mcp.tool
async def get_realtime_stock_snapshot(stock_id: Optional[str] = None) -> dict:
    """[Sponsor] 台股即時 tick snapshot（盤中即時）。不傳 id 取全市場。"""
    return await _query("taiwan_stock_tick_snapshot", data_id=stock_id)


@mcp.tool
async def get_realtime_futopt_info() -> dict:
    """[Free] 期貨選擇權即時報價總覽（商品列表）。"""
    return await _query("TaiwanFutOptTickInfo")


@mcp.tool
async def get_realtime_futures_snapshot(futures_id: Optional[str] = None) -> dict:
    """[Sponsor] 期貨即時 snapshot。不傳 id 取全部。"""
    return await _query("taiwan_futures_snapshot", data_id=futures_id)


@mcp.tool
async def get_realtime_options_snapshot(option_id: Optional[str] = None) -> dict:
    """[Sponsor] 選擇權即時 snapshot。不傳 id 取全部。"""
    return await _query("taiwan_options_snapshot", data_id=option_id)


# ============================================================
# 七、可轉換公司債 (4 個)
# ============================================================

@mcp.tool
async def get_convertible_bond_info() -> dict:
    """[Backer/Sponsor] 可轉債總覽。"""
    return await _query("TaiwanStockConvertibleBondInfo")


@mcp.tool
async def get_convertible_bond_daily(cb_id: Optional[str], start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 可轉債日成交。"""
    return await _query("TaiwanStockConvertibleBondDaily", data_id=cb_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_convertible_bond_institutional(cb_id: Optional[str], start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 可轉債三大法人。"""
    return await _query("TaiwanStockConvertibleBondInstitutionalInvestors", data_id=cb_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_convertible_bond_overview(cb_id: Optional[str], start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 可轉債每日總覽（轉換價、贖回價等）。"""
    return await _query("TaiwanStockConvertibleBondDailyOverview", data_id=cb_id, start_date=start_date, end_date=end_date)


# ============================================================
# 八、新聞 / 景氣 / 產業鏈 (3 個)
# ============================================================

@mcp.tool
async def get_stock_news(stock_id: str, start_date: str) -> dict:
    """[Free] 個股相關新聞（單日）。"""
    return await _query("TaiwanStockNews", data_id=stock_id, start_date=start_date)


@mcp.tool
async def get_business_indicator(start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] 台灣每月景氣對策信號（紅黃藍燈）。"""
    return await _query("TaiwanBusinessIndicator", start_date=start_date, end_date=end_date)


@mcp.tool
async def get_industry_chain() -> dict:
    """[Backer/Sponsor] 個股所屬產業鏈分類。"""
    return await _query("TaiwanStockIndustryChain")


# ============================================================
# 九、國際市場 (9 個)
# ============================================================

@mcp.tool
async def get_us_stock_info() -> dict:
    """[Free] 美股總覽（市值、IPO 年、產業）。"""
    return await _query("USStockInfo")


@mcp.tool
async def get_us_stock_price(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 美股日 K（ADR/普通股/指數）。如 NVDA/TSM/HIMX/AAPL/^DJI/^GSPC/^IXIC。"""
    return await _query("USStockPrice", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_us_stock_minute(stock_id: str, start_date: str) -> dict:
    """[Backer/Sponsor] 美股分 K。"""
    return await _query("USStockPriceMinute", data_id=stock_id, start_date=start_date)


@mcp.tool
async def get_uk_stock_info() -> dict:
    """[Free] 英股總覽。"""
    return await _query("UKStockInfo")


@mcp.tool
async def get_uk_stock_price(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 英股日 K（如 BP.L）。"""
    return await _query("UKStockPrice", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_europe_stock_info() -> dict:
    """[Free] 歐股總覽。"""
    return await _query("EuropeStockInfo")


@mcp.tool
async def get_europe_stock_price(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 歐股日 K（如 AALB.AS）。"""
    return await _query("EuropeStockPrice", data_id=stock_id, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_japan_stock_info() -> dict:
    """[Free] 日股總覽。"""
    return await _query("JapanStockInfo")


@mcp.tool
async def get_japan_stock_price(stock_id: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 日股日 K（如 7203.T 豐田）。"""
    return await _query("JapanStockPrice", data_id=stock_id, start_date=start_date, end_date=end_date)


# ============================================================
# 十、全球總體經濟 (6 個)
# ============================================================

@mcp.tool
async def get_exchange_rate(currency: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 外幣對台幣匯率。
    currency 可選: USD/EUR/JPY/GBP/CNY/HKD/AUD/CAD/CHF/IDR/KRW/MYR/NZD/PHP/SEK/SGD/THB/VND/ZAR
    """
    return await _query("TaiwanExchangeRate", data_id=currency, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_interest_rate(country_code: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 央行利率。country_code: FED(美)/BOE(英)/RBA(澳)/PBOC(中)/BOC(加)/ECB(歐)/RBNZ(紐)/RBI(印)/CBR(俄)/BCB(巴西)/BOJ(日)/SNB(瑞士)。"""
    return await _query("InterestRate", data_id=country_code, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_gold_price(start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 黃金價格。"""
    return await _query("GoldPrice", start_date=start_date, end_date=end_date)


@mcp.tool
async def get_crude_oil(oil_type: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 原油價格。oil_type: 'WTI' 或 'Brent'。"""
    return await _query("CrudeOilPrices", data_id=oil_type, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_us_treasury_yield(tenor: str, start_date: str, end_date: Optional[str] = None) -> dict:
    """[Free] 美國國債殖利率。
    tenor 可選: "United States 1-Month" / "United States 3-Month" / "United States 6-Month" /
              "United States 1-Year" / "United States 2-Year" / "United States 3-Year" /
              "United States 5-Year" / "United States 7-Year" / "United States 10-Year" /
              "United States 20-Year" / "United States 30-Year"
    """
    return await _query("GovernmentBondsYield", data_id=tenor, start_date=start_date, end_date=end_date)


@mcp.tool
async def get_cnn_fear_greed(start_date: str, end_date: Optional[str] = None) -> dict:
    """[Backer/Sponsor] CNN 恐懼貪婪指數。"""
    return await _query("CnnFearGreedIndex", start_date=start_date, end_date=end_date)


# ============================================================
# 啟動
# ============================================================

if __name__ == "__main__":
    logger.info(f"Starting FinMind MCP server v3 on port {PORT}")
    logger.info(f"Token configured: {'yes' if FINMIND_TOKEN else 'NO - set FINMIND_TOKEN env var'}")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=PORT)
