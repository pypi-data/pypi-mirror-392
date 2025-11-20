"""
Core contract creation tools for Agent automation
"""

from mcp.server.fastmcp import Context, FastMCP

def register_contract_tools(mcp: FastMCP):
    """Register feature management tools with the MCP server."""

    @mcp.tool()
    async def create_stock_contract(ctx: Context, symbol: str, currency: str = "USD", exchange: str = "SMART") -> dict:
        """
        Create a stock contract for market data subscriptions and trading.
        
        This tool enables Agents to dynamically create stock contracts without pre-configuration,
        allowing for real-time response to market events, news, and trading opportunities.
        
        Args:
            ctx: The context containing the ezib connection
            symbol: Stock symbol (e.g., "AAPL", "MSFT", "TSLA")
            currency: Currency code (default: "USD")
            exchange: Exchange code (default: "SMART" for best execution)
            
        Returns:
            dict: Contract creation result with contract details and status
            
        Example:
            create_stock_contract(symbol="NVDA")
            # Creates NVDA stock contract for immediate market data subscription
            
            create_stock_contract(symbol="ASML", currency="EUR", exchange="AEB")  
            # Creates European stock contract with specific exchange
        """
        connection_manager = ctx.request_context.lifespan_context.connection_manager
        
        if not connection_manager.is_connected:
            return {
                "success": False,
                "error": "Not connected to Interactive Brokers",
                "symbol": symbol
            }
        
        try:
            ezib = connection_manager.ezib
            
            # Create stock contract using ezIBAsync
            contract = await ezib.createStockContract(
                symbol=symbol,
                currency=currency, 
                exchange=exchange
            )
            
            if contract:
                # Get contract details
                contract_string = ezib.contractString(contract)
                ticker_id = ezib.tickerId(contract_string)
                contract_details = ezib.contractDetails(contract)
                
                return {
                    "success": True,
                    "message": f"Stock contract created successfully for {symbol}",
                    "contract": {
                        "symbol": symbol,
                        "contract_string": contract_string,
                        "ticker_id": ticker_id,
                        "currency": currency,
                        "exchange": exchange,
                        "conId": getattr(contract, 'conId', 0),
                        "secType": "STK",
                        "min_tick": contract_details.get("minTick", 0.01),
                        "trading_hours": contract_details.get("tradingHours", ""),
                        "long_name": contract_details.get("longName", "")
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create contract for symbol {symbol}",
                    "symbol": symbol
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error creating stock contract: {str(e)}",
                "symbol": symbol
            }

    @mcp.tool()
    async def create_options_contract(ctx: Context, symbol: str, expiry: str, strike: float, 
                                    option_type: str = "C", currency: str = "USD", 
                                    exchange: str = "SMART") -> dict:
        """
        Create an options contract for market data subscriptions and trading.
        
        Enables Agents to dynamically create options contracts for strategies like:
        - Earnings plays (straddles, strangles)
        - Volatility trading
        - Delta hedging
        - Income generation (covered calls, cash-secured puts)
        
        Args:
            ctx: The context containing the ezib connection
            symbol: Underlying stock symbol (e.g., "AAPL", "SPY")
            expiry: Expiry date in YYYYMMDD format (e.g., "20241220")
            strike: Strike price (e.g., 150.0, 200.0)
            option_type: "C" for Call, "P" for Put (default: "C")
            currency: Currency code (default: "USD")
            exchange: Exchange code (default: "SMART")
            
        Returns:
            dict: Contract creation result with options details and Greeks availability
            
        Example:
            create_options_contract(symbol="AAPL", expiry="20241220", strike=200.0, option_type="C")
            # Creates AAPL Dec 20 2024 200 Call
            
            create_options_contract(symbol="SPY", expiry="20241115", strike=450.0, option_type="P")
            # Creates SPY Nov 15 2024 450 Put for portfolio hedging
        """
        connection_manager = ctx.request_context.lifespan_context.connection_manager
        
        if not connection_manager.is_connected:
            return {
                "success": False,
                "error": "Not connected to Interactive Brokers",
                "symbol": symbol
            }
        
        # Validate option type
        if option_type.upper() not in ["C", "P", "CALL", "PUT"]:
            return {
                "success": False,
                "error": f"Invalid option_type '{option_type}'. Use 'C'/'Call' or 'P'/'Put'",
                "symbol": symbol
            }
        
        # Normalize option type
        option_right = "C" if option_type.upper() in ["C", "CALL"] else "P"
        
        try:
            ezib = connection_manager.ezib
            
            # Create options contract using ezIBAsync
            contract = await ezib.createOptionContract(
                symbol=symbol,
                expiry=expiry,
                strike=strike,
                otype=option_right,
                currency=currency,
                exchange=exchange
            )
            
            if contract:
                # Get contract details
                contract_string = ezib.contractString(contract)
                ticker_id = ezib.tickerId(contract_string)
                contract_details = ezib.contractDetails(contract)
                
                return {
                    "success": True,
                    "message": f"Options contract created successfully for {symbol} {expiry} {strike} {option_right}",
                    "contract": {
                        "symbol": symbol,
                        "contract_string": contract_string,
                        "ticker_id": ticker_id,
                        "underlying": symbol,
                        "expiry": expiry,
                        "strike": strike,
                        "right": option_right,
                        "currency": currency,
                        "exchange": exchange,
                        "conId": getattr(contract, 'conId', 0),
                        "secType": "OPT",
                        "min_tick": contract_details.get("minTick", 0.01),
                        "trading_hours": contract_details.get("tradingHours", ""),
                        "multiplier": getattr(contract, 'multiplier', '100')
                    },
                    "greeks_available": True  # Options support Greeks calculation
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create options contract for {symbol} {expiry} {strike} {option_right}",
                    "symbol": symbol
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error creating options contract: {str(e)}",
                "symbol": symbol,
                "expiry": expiry,
                "strike": strike,
                "option_type": option_right
            }

    @mcp.tool()
    async def create_futures_contract(ctx: Context, symbol: str, expiry: str = None, 
                                    currency: str = "USD", exchange: str = "CME", 
                                    multiplier: str = "") -> dict:
        """
        Create a futures contract for market data subscriptions and trading.
        
        Enables Agents to access futures markets for:
        - Commodity exposure (crude oil, gold, wheat)
        - Index futures (ES, NQ, YM)
        - Currency futures
        - Interest rate futures
        - Continuous contracts for long-term analysis
        
        Args:
            ctx: The context containing the ezib connection
            symbol: Futures symbol (e.g., "ES", "CL", "GC", "NQ")
            expiry: Expiry date in YYYYMMDD format (None for continuous contract)
            currency: Currency code (default: "USD")
            exchange: Exchange code (default: "CME")
            multiplier: Contract multiplier (auto-detected if empty)
            
        Returns:
            dict: Contract creation result with futures specifications
            
        Example:
            create_futures_contract(symbol="ES", expiry="20241220")
            # Creates E-mini S&P 500 Dec 2024 futures contract
            
            create_futures_contract(symbol="CL", exchange="NYMEX")
            # Creates continuous crude oil futures contract
            
            create_futures_contract(symbol="GC", expiry="20250228", exchange="COMEX")
            # Creates gold futures Feb 2025 contract
        """
        connection_manager = ctx.request_context.lifespan_context.connection_manager
        
        if not connection_manager.is_connected:
            return {
                "success": False,
                "error": "Not connected to Interactive Brokers",
                "symbol": symbol
            }
        
        try:
            ezib = connection_manager.ezib
            
            # Handle continuous futures (no expiry specified)
            if expiry is None:
                # Create continuous futures contract
                contract = await ezib.createContinuousFuturesContract(
                    symbol=symbol,
                    exchange=exchange
                )
            else:
                # Create specific expiry futures contract
                contract = await ezib.createFuturesContract(
                    symbol=symbol,
                    currency=currency,
                    expiry=expiry,
                    exchange=exchange,
                    multiplier=multiplier
                )
            
            if contract:
                # Get contract details
                contract_string = ezib.contractString(contract)
                ticker_id = ezib.tickerId(contract_string)
                contract_details = ezib.contractDetails(contract)
                
                return {
                    "success": True,
                    "message": f"Futures contract created successfully for {symbol}" + (f" {expiry}" if expiry else " (continuous)"),
                    "contract": {
                        "symbol": symbol,
                        "contract_string": contract_string,
                        "ticker_id": ticker_id,
                        "expiry": expiry or "continuous",
                        "currency": currency,
                        "exchange": exchange,
                        "multiplier": getattr(contract, 'multiplier', multiplier),
                        "conId": getattr(contract, 'conId', 0),
                        "secType": "FUT" if expiry else "CONTFUT",
                        "min_tick": contract_details.get("minTick", 0.01),
                        "trading_hours": contract_details.get("tradingHours", ""),
                        "long_name": contract_details.get("longName", ""),
                        "contract_month": contract_details.get("contractMonth", "")
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create futures contract for {symbol}" + (f" {expiry}" if expiry else " (continuous)"),
                    "symbol": symbol
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error creating futures contract: {str(e)}",
                "symbol": symbol,
                "expiry": expiry
            }

    @mcp.tool()
    async def get_contract_details(ctx: Context, contract_string: str) -> dict:
        """
        Get comprehensive details about a contract.
        
        Provides Agents with detailed contract information for:
        - Trading hours validation
        - Minimum tick size for order pricing
        - Contract specifications
        - Exchange information
        - Multiplier and margin requirements
        
        Args:
            ctx: The context containing the ezib connection
            contract_string: Contract identifier string (from contract creation)
            
        Returns:
            dict: Comprehensive contract details and specifications
            
        Example:
            get_contract_details(contract_string="AAPL_STK")
            # Returns detailed AAPL stock contract information
            
            get_contract_details(contract_string="AAPL20241220C00200000_OPT")
            # Returns AAPL option contract specifications
        """
        connection_manager = ctx.request_context.lifespan_context.connection_manager
        
        if not connection_manager.is_connected:
            return {
                "success": False,
                "error": "Not connected to Interactive Brokers",
                "contract_string": contract_string
            }
        
        try:
            ezib = connection_manager.ezib
            
            # Get ticker ID from contract string
            ticker_id = ezib.tickerId(contract_string)
            
            # Get contract details
            contract_details = ezib.contractDetails(ticker_id)
            
            if not contract_details or contract_details.get("tickerId", 0) == 0:
                return {
                    "success": False,
                    "error": f"Contract not found: {contract_string}",
                    "contract_string": contract_string
                }
            
            # Get the actual contract object if available
            contract = ezib.contracts.get(ticker_id)
            
            result = {
                "success": True,
                "contract_string": contract_string,
                "ticker_id": ticker_id,
                "details": {
                    "con_id": contract_details.get("conId", 0),
                    "symbol": contract_details.get("summary", {}).get("symbol", ""),
                    "sec_type": contract_details.get("summary", {}).get("secType", ""),
                    "exchange": contract_details.get("summary", {}).get("exchange", ""),
                    "currency": contract_details.get("summary", {}).get("currency", ""),
                    "min_tick": contract_details.get("minTick", 0.01),
                    "price_magnifier": contract_details.get("priceMagnifier", 1),
                    "multiplier": contract_details.get("summary", {}).get("multiplier", ""),
                    "trading_hours": contract_details.get("tradingHours", ""),
                    "liquid_hours": contract_details.get("liquidHours", ""),
                    "time_zone": contract_details.get("timeZoneId", ""),
                    "long_name": contract_details.get("longName", ""),
                    "market_name": contract_details.get("marketName", ""),
                    "industry": contract_details.get("industry", ""),
                    "category": contract_details.get("category", ""),
                    "subcategory": contract_details.get("subcategory", ""),
                    "valid_exchanges": contract_details.get("validExchanges", ""),
                    "order_types": contract_details.get("orderTypes", "")
                }
            }
            
            # Add options-specific details
            if contract and hasattr(contract, 'secType') and contract.secType == "OPT":
                result["details"].update({
                    "underlying_con_id": contract_details.get("underConId", 0),
                    "expiry": contract_details.get("summary", {}).get("lastTradeDateOrContractMonth", ""),
                    "strike": contract_details.get("summary", {}).get("strike", 0.0),
                    "right": contract_details.get("summary", {}).get("right", "")
                })
            
            # Add futures-specific details  
            elif contract and hasattr(contract, 'secType') and contract.secType == "FUT":
                result["details"].update({
                    "contract_month": contract_details.get("contractMonth", ""),
                    "expiry": contract_details.get("summary", {}).get("lastTradeDateOrContractMonth", "")
                })
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting contract details: {str(e)}",
                "contract_string": contract_string
            }