"""
Stock Screener Module
Get top tickers by market, sector, and market cap with geographic diversification
"""

from typing import List, Dict, Optional, Literal
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# GEOGRAPHIC DISTRIBUTION LISTS
# ============================================================================

# USA - Top companies by market cap (500 tickers)
USA_TOP_TICKERS = [
    # Mega Cap Tech (>$1T)
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA",
    
    # Large Cap Tech ($100B-$1T)
    "AVGO", "ORCL", "ADBE", "CRM", "CSCO", "INTC", "AMD", "QCOM", "TXN", "AMAT",
    "ADI", "LRCX", "KLAC", "SNPS", "CDNS", "MCHP", "MRVL", "NXPI", "MU", "WDAY",
    "PANW", "SNOW", "NET", "DDOG", "CRWD", "ZS", "OKTA", "FTNT", "CYBR", "S",
    "NOW", "TEAM", "ATLR", "ZM", "TWLO", "DOCU", "PLTR", "PATH", "U", "BILL",
    
    # Financial Services
    "BRK-B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "C", "BLK",
    "SPGI", "AXP", "SCHW", "USB", "PNC", "TFC", "COF", "BK", "STT", "NTRS",
    "CME", "ICE", "MCO", "AON", "MMC", "AJG", "BRO", "ALLY", "SYF", "DFS",
    "PRU", "MET", "AIG", "AFL", "ALL", "TRV", "PGR", "CB", "CNA", "WRB",
    
    # Healthcare
    "UNH", "JNJ", "LLY", "ABBV", "MRK", "TMO", "ABT", "DHR", "PFE", "BMY",
    "AMGN", "GILD", "REGN", "VRTX", "ISRG", "CI", "CVS", "HUM", "ELV", "CNC",
    "BSX", "MDT", "SYK", "EW", "ZBH", "BAX", "HOLX", "ALGN", "RMD", "DXCM",
    "MRNA", "BNTX", "BIIB", "ILMN", "A", "WAT", "IDXX", "IQV", "MTD", "PKI",
    
    # Consumer Cyclical
    "AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "LOW", "TJX", "BKNG", "MAR",
    "GM", "F", "HLT", "CMG", "YUM", "DRI", "ORLY", "AZO", "ROST", "TGT",
    "EBAY", "ETSY", "W", "CHWY", "CVNA", "KMX", "AN", "LAD", "SAH", "ABG",
    "TPR", "RL", "CPRI", "PVH", "VFC", "HBI", "DECK", "CROX", "SKX", "FL",
    
    # Consumer Defensive
    "WMT", "PG", "KO", "PEP", "COST", "PM", "MO", "MDLZ", "CL", "KMB",
    "GIS", "K", "CPB", "CAG", "SJM", "HRL", "TSN", "BG", "ADM", "CHD",
    "CLX", "EL", "KHC", "HSY", "KDP", "MNST", "CELH", "TAP", "STZ", "BF-B",
    "KR", "SYY", "DLTR", "DG", "BJ", "GO", "NGVC", "ACI", "WBA", "CVS",
    
    # Energy
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL",
    "BKR", "WMB", "KMI", "OKE", "LNG", "FANG", "DVN", "HES", "MRO", "APA",
    "CTRA", "EQT", "AR", "CNX", "RRC", "SM", "PR", "MTDR", "MGY", "NOG",
    
    # Industrials
    "UPS", "HON", "UNP", "RTX", "CAT", "BA", "LMT", "GE", "MMM", "DE",
    "GD", "NOC", "EMR", "ETN", "ITW", "PH", "CMI", "PCAR", "ROK", "DOV",
    "FDX", "CSX", "NSC", "UBER", "LYFT", "DAL", "UAL", "AAL", "LUV", "ALK",
    "WM", "RSG", "FAST", "CHRW", "JBHT", "ODFL", "XPO", "KNX", "EXPD", "LSTR",
    
    # Communication Services
    "META", "GOOGL", "GOOG", "NFLX", "DIS", "CMCSA", "T", "VZ", "TMUS", "CHTR",
    "PARA", "WBD", "FOXA", "FOX", "NWSA", "NWS", "NYT", "MSGS", "OMC", "IPG",
    
    # Real Estate
    "PLD", "AMT", "EQIX", "PSA", "WELL", "DLR", "O", "SPG", "VICI", "CBRE",
    "AVB", "EQR", "VTR", "ESS", "MAA", "UDR", "CPT", "AIV", "ELS", "SUI",
    
    # Utilities
    "NEE", "DUK", "SO", "D", "AEP", "EXC", "SRE", "XEL", "WEC", "ES",
    "PEG", "ED", "EIX", "AWK", "PPL", "CMS", "DTE", "AEE", "LNT", "EVRG",
    
    # Materials
    "LIN", "APD", "SHW", "ECL", "NEM", "FCX", "NUE", "DD", "DOW", "ALB",
    "VMC", "MLM", "CTVA", "FMC", "EMN", "CF", "MOS", "LYB", "PPG", "RPM",
    
    # Mid Cap Growth
    "DKNG", "PENN", "RSI", "CZR", "MGM", "WYNN", "LVS", "MLCO", "RCL", "CCL",
    "NCLH", "H", "HLT", "MAR", "IHG", "EXPE", "BKNG", "ABNB", "TRIP", "TXRH",
    "WING", "BLMN", "PLAY", "CAKE", "DIN", "BJRI", "PZZA", "DPZA", "WEN", "MCD",
    
    # Small Cap Value
    "SLG", "BXP", "KRC", "DEI", "PDM", "HIW", "PGRE", "VNO", "CUZ", "ESRT",
    "JBGS", "OFC", "CLI", "SLG", "ARE", "BMR", "REXR", "FR", "EGP", "BDN",
    
    # ETFs for diversification
    "SPY", "QQQ", "DIA", "IWM", "VTI", "VOO", "VEA", "VWO", "AGG", "BND",
    "GLD", "SLV", "USO", "UNG", "XLE", "XLF", "XLK", "XLV", "XLI", "XLP",
    "XLU", "XLB", "XLRE", "XLC", "XLY", "IYR", "VNQ", "SCHD", "JEPI", "JEPQ",
    
    # Crypto-related
    "COIN", "MSTR", "RIOT", "MARA", "CLSK", "CIFR", "HUT", "BITF", "ARBK", "BTBT",
    
    # REITs
    "AMT", "PLD", "EQIX", "PSA", "WELL", "DLR", "O", "SPG", "VICI", "CBRE",
    "SBAC", "CCI", "AVB", "EQR", "VTR", "ESS", "MAA", "UDR", "CPT", "INVH",
    
    # Biotech
    "MRNA", "BNTX", "NVAX", "VRTX", "REGN", "GILD", "BIIB", "ILMN", "ALNY", "INCY",
    "SGEN", "BMRN", "TECH", "UTHR", "EXEL", "RARE", "FOLD", "IONS", "ARWR", "RGEN",
    
    # Cloud/SaaS
    "CRM", "NOW", "WDAY", "ADBE", "ORCL", "SAP", "SNOW", "DDOG", "NET", "CRWD",
    "ZS", "OKTA", "PANW", "FTNT", "S", "MDB", "ESTC", "CFLT", "GTLB", "PATH",
    
    # Semiconductors
    "NVDA", "AMD", "INTC", "QCOM", "AVGO", "TXN", "ADI", "LRCX", "KLAC", "AMAT",
    "MU", "MRVL", "NXPI", "MCHP", "ON", "SWKS", "QRVO", "MPWR", "ALGM", "SITM",
]

# Europe - Top companies (150 tickers)
EUROPE_TOP_TICKERS = [
    # UK - FTSE 100
    "BP.L", "SHEL.L", "HSBA.L", "AZN.L", "ULVR.L", "DGE.L", "GSK.L", "RIO.L",
    "BATS.L", "REL.L", "NG.L", "LSEG.L", "BARC.L", "LLOY.L", "VOD.L", "PRU.L",
    "CRH.L", "ABF.L", "ENT.L", "IMB.L", "INF.L", "BA.L", "EXPN.L", "FERG.L",
    "RKT.L", "BRBY.L", "AUTO.L", "SMDS.L", "RR.L", "WEIR.L",
    
    # Germany - DAX
    "SAP.DE", "SIE.DE", "ALV.DE", "AIR.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "DAI.DE",
    "DB1.DE", "DBK.DE", "DTE.DE", "EOAN.DE", "FRE.DE", "HEI.DE", "HEN3.DE", "IFX.DE",
    "MRK.DE", "MTX.DE", "MUV2.DE", "RWE.DE", "VOW3.DE", "VNA.DE", "1COV.DE", "ADS.DE",
    "BEI.DE", "CON.DE", "HNR1.DE", "LIN.DE", "PUM.DE", "QIA.DE",
    
    # France - CAC 40
    "MC.PA", "OR.PA", "SAN.PA", "AIR.PA", "BNP.PA", "SU.PA", "TTE.PA", "SAF.PA",
    "DG.PA", "RMS.PA", "CDI.PA", "CS.PA", "BN.PA", "CAP.PA", "SGO.PA", "EL.PA",
    "EN.PA", "VIE.PA", "VIV.PA", "KER.PA", "ACA.PA", "PUB.PA", "STM.PA", "DSY.PA",
    "URW.AS", "WLN.PA", "TEP.PA", "GLE.PA", "LR.PA", "STLA.PA",
    
    # Switzerland
    "NESN.SW", "ROG.SW", "NOVN.SW", "UHR.SW", "ABBN.SW", "ZURN.SW", "CFR.SW", "SREN.SW",
    "UBSG.SW", "CSGN.SW", "GIVN.SW", "LONN.SW", "SLHN.SW", "GEBN.SW", "ALC.SW", "SIKA.SW",
    
    # Netherlands
    "ASML.AS", "PHIA.AS", "INGA.AS", "HEIA.AS", "AD.AS", "ABN.AS", "KPN.AS", "RAND.AS",
    "UNA.AS", "DSM.AS", "AKZA.AS", "WKL.AS", "AGN.AS", "MT.AS", "SHELL.AS", "ADYEN.AS",
    
    # Spain
    "ITX.MC", "SAN.MC", "BBVA.MC", "IBE.MC", "TEF.MC", "REP.MC", "CABK.MC", "FER.MC",
    "ENG.MC", "ACS.MC", "IAG.MC", "AENA.MC", "ELE.MC", "SAB.MC", "GRF.MC", "MAP.MC",
    
    # Italy
    "ENI.MI", "ISP.MI", "UCG.MI", "ENEL.MI", "STM.MI", "TIT.MI", "G.MI", "CPR.MI",
    "RACE.MI", "ATL.MI", "STLA.MI", "PRY.MI", "AMP.MI", "MB.MI", "BGN.MI", "TEN.MI",
    
    # Nordics (Sweden, Denmark, Norway, Finland)
    "VOLV-B.ST", "ERIC-B.ST", "SEB-A.ST", "HM-B.ST", "SAND.ST", "ATCO-A.ST", "SKF-B.ST", "ABB.ST",
    "NOVO-B.CO", "DSV.CO", "CARLB.CO", "VWS.CO", "MAERSK-B.CO", "TRYG.CO", "COLO-B.CO", "ORSTED.CO",
    "EQNR.OL", "DNB.OL", "MOWI.OL", "TEL.OL", "ORK.OL", "YAR.OL", "REC.OL", "STB.OL",
    "NOKIA.HE", "FORTUM.HE", "SAMPO.HE", "KNEBV.HE", "STERV.HE", "UPM.HE", "NESTE.HE", "ORNBV.HE",
]

# Asia - Top companies (100 tickers)
ASIA_TOP_TICKERS = [
    # China/Hong Kong - Hang Seng + A-Shares
    "0700.HK", "9988.HK", "0941.HK", "0939.HK", "1299.HK", "2318.HK", "3690.HK", "9618.HK",
    "0005.HK", "0388.HK", "1398.HK", "3988.HK", "0001.HK", "0002.HK", "0003.HK", "0011.HK",
    "0016.HK", "0027.HK", "0066.HK", "0083.HK", "0175.HK", "0267.HK", "0288.HK", "0386.HK",
    "0688.HK", "0857.HK", "0883.HK", "0968.HK", "1109.HK", "1113.HK", "1928.HK", "2007.HK",
    "2382.HK", "2388.HK", "3328.HK", "9999.HK", "6098.HK", "9626.HK", "2269.HK", "1024.HK",
    
    # Japan - Nikkei 225
    "7203.T", "6758.T", "6861.T", "8306.T", "9984.T", "9983.T", "8035.T", "6902.T",
    "6501.T", "6954.T", "6762.T", "4063.T", "4502.T", "4503.T", "4568.T", "8031.T",
    "8058.T", "8001.T", "8002.T", "8411.T", "8306.T", "8316.T", "9432.T", "9433.T",
    "9434.T", "9437.T", "9531.T", "9532.T", "9766.T", "9843.T",
    
    # South Korea - KOSPI
    "005930.KS", "000660.KS", "035420.KS", "051910.KS", "005380.KS", "006400.KS", "035720.KS", "005490.KS",
    "012330.KS", "028260.KS", "055550.KS", "066570.KS", "096770.KS", "105560.KS", "207940.KS", "323410.KS",
    
    # Taiwan - TWSE
    "2330.TW", "2317.TW", "2454.TW", "2882.TW", "1301.TW", "1303.TW", "2308.TW", "2412.TW",
    "3008.TW", "2891.TW", "2886.TW", "2303.TW", "2002.TW", "1216.TW", "2881.TW", "2912.TW",
    
    # India - NSE
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "BHARTIARTL.NS",
    "ITC.NS", "SBIN.NS", "BAJFINANCE.NS", "LT.NS", "ASIANPAINT.NS", "AXISBANK.NS", "MARUTI.NS", "WIPRO.NS",
]

# Rest of World - Emerging & Other Markets (50 tickers)
OTHER_MARKETS_TICKERS = [
    # Canada - TSX
    "SHOP.TO", "RY.TO", "TD.TO", "BMO.TO", "BNS.TO", "ENB.TO", "CNQ.TO", "SU.TO",
    "CP.TO", "CNR.TO", "TRP.TO", "WCN.TO", "MFC.TO", "SLF.TO", "FNV.TO", "ABX.TO",
    
    # Australia - ASX
    "BHP.AX", "CBA.AX", "CSL.AX", "NAB.AX", "WBC.AX", "ANZ.AX", "WES.AX", "MQG.AX",
    "WOW.AX", "FMG.AX", "RIO.AX", "WDS.AX", "GMG.AX", "TCL.AX", "TLS.AX", "WTC.AX",
    
    # Brazil - BOVESPA
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA", "B3SA3.SA", "WEGE3.SA", "RENT3.SA",
    
    # Mexico
    "AMXL.MX", "WALMEX.MX", "GFNORTEO.MX", "CEMEXCPO.MX", "ALFAA.MX", "FEMSAUBD.MX",
    
    # Singapore
    "D05.SI", "O39.SI", "U11.SI", "C31.SI", "Z74.SI", "BN4.SI",
]


# ============================================================================
# SECTOR-BASED DISTRIBUTION
# ============================================================================

SECTORS = {
    "Technology": [
        "AAPL", "MSFT", "GOOGL", "GOOG", "NVDA", "META", "AVGO", "ORCL", "ADBE", "CRM",
        "CSCO", "INTC", "AMD", "QCOM", "TXN", "AMAT", "ADI", "LRCX", "KLAC", "SNPS",
        "CDNS", "MCHP", "MRVL", "NXPI", "MU", "WDAY", "PANW", "SNOW", "NET", "DDOG",
        "CRWD", "ZS", "OKTA", "FTNT", "NOW", "TEAM", "SAP.DE", "ASML.AS", "0700.HK", "7203.T",
    ],
    "Healthcare": [
        "UNH", "JNJ", "LLY", "ABBV", "MRK", "TMO", "ABT", "DHR", "PFE", "BMY",
        "AMGN", "GILD", "REGN", "VRTX", "ISRG", "CI", "CVS", "HUM", "ELV", "CNC",
        "BSX", "MDT", "SYK", "MRNA", "BNTX", "AZN.L", "GSK.L", "NOVN.SW", "ROG.SW", "SAN.PA",
    ],
    "Financial Services": [
        "BRK-B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "C", "BLK",
        "SPGI", "AXP", "SCHW", "USB", "PNC", "TFC", "COF", "BNP.PA", "HSBA.L", "DBK.DE",
        "HDFCBANK.NS", "ICICIBANK.NS", "005930.KS", "8306.T", "CBA.AX", "RY.TO", "TD.TO", "ITUB4.SA",
    ],
    "Consumer Cyclical": [
        "AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "LOW", "TJX", "BKNG", "MAR",
        "GM", "F", "HLT", "CMG", "YUM", "MC.PA", "BMW.DE", "DAI.DE", "VOW3.DE", "ITX.MC",
        "HM-B.ST", "RACE.MI", "SHOP.TO", "9984.T", "MARUTI.NS",
    ],
    "Energy": [
        "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "BP.L", "SHEL.L",
        "TTE.PA", "SU.PA", "ENI.MI", "REP.MC", "EQNR.OL", "SU.TO", "CNQ.TO", "PETR4.SA", "WDS.AX",
    ],
    "Industrials": [
        "UPS", "HON", "UNP", "RTX", "CAT", "BA", "LMT", "GE", "MMM", "DE",
        "GD", "NOC", "EMR", "AIR.PA", "SIE.DE", "ABB.ST", "CP.TO", "CNR.TO", "BHP.AX",
    ],
    "Communication Services": [
        "META", "GOOGL", "GOOG", "NFLX", "DIS", "CMCSA", "T", "VZ", "TMUS", "CHTR",
        "VIV.PA", "TEF.MC", "VOD.L", "9984.T", "9432.T", "BHARTIARTL.NS",
    ],
    "Consumer Defensive": [
        "WMT", "PG", "KO", "PEP", "COST", "PM", "MO", "MDLZ", "NESN.SW", "UNA.AS",
        "ULVR.L", "DGE.L", "OR.PA", "NOVO-B.CO", "HINDUNILVR.NS", "ITC.NS", "WOW.AX",
    ],
    "Real Estate": [
        "PLD", "AMT", "EQIX", "PSA", "WELL", "DLR", "O", "SPG", "VICI", "URW.AS",
    ],
    "Utilities": [
        "NEE", "DUK", "SO", "D", "AEP", "EOAN.DE", "RWE.DE", "EDF.PA", "NG.L", "ENEL.MI",
    ],
    "Basic Materials": [
        "LIN", "APD", "SHW", "ECL", "BAS.DE", "AIR.PA", "RIO.L", "VALE3.SA", "BHP.AX", "FMG.AX",
    ],
}


# ============================================================================
# MAIN API FUNCTIONS
# ============================================================================

def get_top_tickers(
    count: int = 800,
    by: Literal["geography", "sector", "market_cap", "balanced"] = "balanced",
    market: Literal["US", "Europe", "Asia", "global", "all"] = "global",
    sectors: Optional[List[str]] = None,
    limit: Optional[int] = None,
) -> List[str]:
    """
    Get top tickers with geographic diversification and sector balancing.
    
    Args:
        count: Number of tickers to return (default: 800)
        by: Distribution method:
            - "geography": Distribute by geographic regions
            - "sector": Distribute evenly across sectors
            - "market_cap": Sort by market cap (requires live data)
            - "balanced": Mix of geography + sector (default)
        market: Which markets to include:
            - "US": USA only
            - "Europe": Europe only
            - "Asia": Asia only
            - "global": USA + Europe + Asia
            - "all": Global + other markets
        sectors: Optional list of sectors to filter by (e.g., ["Technology", "Healthcare"])
        limit: Alias for count (for compatibility)
    
    Returns:
        List of ticker symbols
        
    Examples:
        >>> # Get 800 tickers with global diversification
        >>> tickers = get_top_tickers(800, by="balanced", market="global")
        
        >>> # Get 200 US tech stocks
        >>> tickers = get_top_tickers(200, market="US", sectors=["Technology"])
        
        >>> # Get 100 tickers per sector
        >>> tickers = get_top_tickers(1000, by="sector")
    """
    # Use limit if provided (for compatibility)
    if limit is not None:
        count = limit
    
    if by == "geography":
        return _get_by_geography(count, market)
    elif by == "sector":
        return _get_by_sector(count, sectors)
    elif by == "balanced":
        return _get_balanced(count, market, sectors)
    else:
        logger.warning(f"Method '{by}' not fully implemented, falling back to 'balanced'")
        return _get_balanced(count, market, sectors)


def _get_by_geography(count: int, market: str) -> List[str]:
    """Get tickers distributed by geographic regions."""
    
    if market == "US":
        return USA_TOP_TICKERS[:count]
    elif market == "Europe":
        return EUROPE_TOP_TICKERS[:count]
    elif market == "Asia":
        return ASIA_TOP_TICKERS[:count]
    elif market == "global":
        # Distribution: 60% US, 20% Europe, 20% Asia
        us_count = int(count * 0.60)
        eu_count = int(count * 0.20)
        asia_count = count - us_count - eu_count
        
        result = []
        result.extend(USA_TOP_TICKERS[:us_count])
        result.extend(EUROPE_TOP_TICKERS[:eu_count])
        result.extend(ASIA_TOP_TICKERS[:asia_count])
        return result
    else:  # "all"
        # Distribution: 50% US, 20% Europe, 15% Asia, 15% Other
        us_count = int(count * 0.50)
        eu_count = int(count * 0.20)
        asia_count = int(count * 0.15)
        other_count = count - us_count - eu_count - asia_count
        
        result = []
        result.extend(USA_TOP_TICKERS[:us_count])
        result.extend(EUROPE_TOP_TICKERS[:eu_count])
        result.extend(ASIA_TOP_TICKERS[:asia_count])
        result.extend(OTHER_MARKETS_TICKERS[:other_count])
        return result


def _get_by_sector(count: int, sectors_filter: Optional[List[str]] = None) -> List[str]:
    """Get tickers distributed evenly across sectors."""
    
    # Filter sectors if requested
    if sectors_filter:
        active_sectors = {k: v for k, v in SECTORS.items() if k in sectors_filter}
    else:
        active_sectors = SECTORS
    
    if not active_sectors:
        logger.warning("No sectors matched filter, using all sectors")
        active_sectors = SECTORS
    
    # Calculate tickers per sector
    per_sector = count // len(active_sectors)
    remainder = count % len(active_sectors)
    
    result = []
    for i, (sector_name, tickers) in enumerate(active_sectors.items()):
        # Give extra ticker to first sectors if there's a remainder
        sector_count = per_sector + (1 if i < remainder else 0)
        result.extend(tickers[:sector_count])
    
    return result[:count]  # Ensure exact count


def _get_balanced(
    count: int, 
    market: str = "global", 
    sectors_filter: Optional[List[str]] = None
) -> List[str]:
    """
    Get tickers with balanced distribution across both geography and sectors.
    This is the recommended default method.
    """
    
    # Step 1: Get geographic base
    geo_tickers = set(_get_by_geography(count * 2, market))  # Get more than needed
    
    # Step 2: Get sector distribution
    sector_tickers = set(_get_by_sector(count * 2, sectors_filter))
    
    # Step 3: Combine with priority to intersection (tickers in both lists)
    intersection = geo_tickers & sector_tickers
    geo_only = geo_tickers - sector_tickers
    sector_only = sector_tickers - geo_tickers
    
    # Build result: prioritize intersection, then fill from both sets
    result = list(intersection)
    
    if len(result) < count:
        # Add from geo_only
        needed = count - len(result)
        result.extend(list(geo_only)[:needed // 2])
    
    if len(result) < count:
        # Add from sector_only
        needed = count - len(result)
        result.extend(list(sector_only)[:needed])
    
    if len(result) < count:
        # Still need more? Add remaining from geo
        needed = count - len(result)
        remaining = [t for t in USA_TOP_TICKERS if t not in result]
        result.extend(remaining[:needed])
    
    return result[:count]  # Ensure exact count


def get_sector_tickers(sector: str, count: int = 100) -> List[str]:
    """
    Get top tickers for a specific sector.
    
    Args:
        sector: Sector name (e.g., "Technology", "Healthcare")
        count: Number of tickers to return
    
    Returns:
        List of ticker symbols for that sector
        
    Example:
        >>> tech_stocks = get_sector_tickers("Technology", 50)
    """
    if sector not in SECTORS:
        available = list(SECTORS.keys())
        raise ValueError(f"Unknown sector '{sector}'. Available: {available}")
    
    return SECTORS[sector][:count]


def get_market_tickers(market: str, count: int = 500) -> List[str]:
    """
    Get top tickers for a specific market/region.
    
    Args:
        market: Market region ("US", "Europe", "Asia", "Other")
        count: Number of tickers to return
    
    Returns:
        List of ticker symbols for that market
        
    Example:
        >>> europe_stocks = get_market_tickers("Europe", 100)
    """
    market_map = {
        "US": USA_TOP_TICKERS,
        "Europe": EUROPE_TOP_TICKERS,
        "Asia": ASIA_TOP_TICKERS,
        "Other": OTHER_MARKETS_TICKERS,
    }
    
    if market not in market_map:
        available = list(market_map.keys())
        raise ValueError(f"Unknown market '{market}'. Available: {available}")
    
    return market_map[market][:count]


def get_available_sectors() -> List[str]:
    """Get list of all available sectors."""
    return list(SECTORS.keys())


def get_ticker_count_by_market() -> Dict[str, int]:
    """Get count of available tickers per market."""
    return {
        "US": len(USA_TOP_TICKERS),
        "Europe": len(EUROPE_TOP_TICKERS),
        "Asia": len(ASIA_TOP_TICKERS),
        "Other": len(OTHER_MARKETS_TICKERS),
        "Total": len(USA_TOP_TICKERS) + len(EUROPE_TOP_TICKERS) + 
                len(ASIA_TOP_TICKERS) + len(OTHER_MARKETS_TICKERS),
    }


def get_ticker_count_by_sector() -> Dict[str, int]:
    """Get count of available tickers per sector."""
    return {sector: len(tickers) for sector, tickers in SECTORS.items()}
