"""
Market Data Infrastructure for real-time price streaming and historical data
"""

from mcp.server.fastmcp import Context, FastMCP
from typing import Optional, List, Dict, Any
import pandas as pd

from ezib_mcp.licensing import require_quota


def register_market_data_tools(mcp: FastMCP):
    """Register market data tools with the MCP server."""

    @mcp.tool()
    @require_quota("market_data")
    async def subscribe_market_data(ctx: Context, contract_string: str,
                                   data_type: str = "realtime") -> dict:
        """
        Subscribe to real-time market data for a contract.
        
        Enables Agents to receive live market data for:
        - Real-time price updates (bid, ask, last)
        - Volume and trade information
        - Market status and trading hours
        - Price change and percentage calculations
        
        Args:
            ctx: The context containing the ezib connection
            contract_string: Contract identifier (from contract creation)
            data_type: Type of data subscription ("realtime", "delayed", "frozen")
            
        Returns:
            dict: Subscription result with market data stream info
            
        Example:
            subscribe_market_data(contract_string="AAPL_STK")
            # Subscribes to real-time AAPL market data
            
            subscribe_market_data(contract_string="ES_FUT", data_type="delayed")
            # Subscribes to delayed E-mini S&P 500 futures data
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
            
            if ticker_id == 0:
                return {
                    "success": False,
                    "error": f"Invalid contract string: {contract_string}",
                    "contract_string": contract_string
                }
            
            # Get contract object from ticker ID
            contract = ezib.contracts.get(ticker_id)
            if not contract:
                return {
                    "success": False,
                    "error": f"Contract not found for {contract_string}",
                    "contract_string": contract_string
                }
            
            # Map data_type to marketDataType
            market_data_type_map = {
                "realtime": 1,
                "frozen": 2,
                "delayed": 3,
                "delayed_frozen": 4
            }
            market_data_type = market_data_type_map.get(data_type.lower(), 1)
            
            # Set market data type globally first
            ezib.ib.reqMarketDataType(market_data_type)
            
            # Subscribe to market data using requestMarketData
            await ezib.requestMarketData([contract])
            success = True
            
            if success:
                # Get initial market data snapshot based on contract type
                is_option = hasattr(contract, 'secType') and contract.secType in ("OPT", "FOP")
                data_source = ezib.optionsData if is_option else ezib.marketData
                market_data = data_source.get(ticker_id, {})
                
                return {
                    "success": True,
                    "message": f"Successfully subscribed to market data for {contract_string}",
                    "subscription": {
                        "contract_string": contract_string,
                        "ticker_id": ticker_id,
                        "data_type": data_type,
                        "status": "active",
                        "initial_data": market_data
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to subscribe to market data for {contract_string}",
                    "contract_string": contract_string
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error subscribing to market data: {str(e)}",
                "contract_string": contract_string
            }

    @mcp.tool()
    @require_quota("market_data")
    async def get_market_data(ctx: Context, contract_string: str) -> dict:
        """
        Get current market data for a subscribed contract.
        
        Retrieves latest market data including:
        - Current bid/ask prices and sizes
        - Last trade price and volume
        - Daily high/low and opening price
        - Market status and timestamp
        - Price changes and percentages
        
        Args:
            ctx: The context containing the ezib connection
            contract_string: Contract identifier (must be subscribed)
            
        Returns:
            dict: Current market data with all available fields
            
        Example:
            get_market_data(contract_string="AAPL_STK")
            # Returns current AAPL market data snapshot
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
            
            if ticker_id == 0:
                return {
                    "success": False,
                    "error": f"Invalid contract string: {contract_string}",
                    "contract_string": contract_string
                }
            
            # Get contract object to determine data source
            contract = ezib.contracts.get(ticker_id)
            is_option = contract and hasattr(contract, 'secType') and contract.secType in ("OPT", "FOP")
            
            # Get market data from appropriate source
            data_source = ezib.optionsData if is_option else ezib.marketData
            market_data = data_source.get(ticker_id)
            
            # Check if DataFrame exists and has data
            if market_data is None or (hasattr(market_data, 'empty') and market_data.empty) or len(market_data) == 0:
                return {
                    "success": False,
                    "error": f"No market data available for {contract_string}. Subscribe first.",
                    "contract_string": contract_string,
                    "suggestion": "Use subscribe_market_data() to start receiving data"
                }
            
            # Extract latest data from DataFrame (market_data is always a DataFrame)
            latest_data = market_data.iloc[-1]
            if hasattr(latest_data, 'to_dict'):
                latest_data = latest_data.to_dict()
            
            # Format data with consistent structure based on actual DataFrame fields
            formatted_data = {
                "contract_string": contract_string,
                "ticker_id": ticker_id,
                "timestamp": latest_data.get("timestamp", ""),
                "prices": {
                    "bid": latest_data.get("bid", 0.0),
                    "ask": latest_data.get("ask", 0.0), 
                    "last": latest_data.get("last", 0.0)
                },
                "sizes": {
                    "bid_size": latest_data.get("bidsize", 0),
                    "ask_size": latest_data.get("asksize", 0),
                    "last_size": latest_data.get("lastsize", 0)
                },
                "volume": latest_data.get("volume", 0),  # trading volume for the day
                "implied_volatility": latest_data.get("iv", 0.0),
                "open_interest": latest_data.get("oi", 0)
            }
            
            # Add options-specific data for options contracts
            if is_option:
                formatted_data.update({
                    "underlying": latest_data.get("underlying", 0.0),
                    "option_price": latest_data.get("price", 0.0),
                    "dividend": latest_data.get("dividend", 0.0),
                    "greeks": {
                        # Generic/Mid Greeks
                        "imp_vol": latest_data.get("imp_vol", 0.0),
                        "delta": latest_data.get("delta", 0.0),
                        "gamma": latest_data.get("gamma", 0.0),
                        "vega": latest_data.get("vega", 0.0),
                        "theta": latest_data.get("theta", 0.0),
                        # Last price based Greeks
                        "last_imp_vol": latest_data.get("last_imp_vol", 0.0),
                        "last_delta": latest_data.get("last_delta", 0.0),
                        "last_gamma": latest_data.get("last_gamma", 0.0),
                        "last_vega": latest_data.get("last_vega", 0.0),
                        "last_theta": latest_data.get("last_theta", 0.0),
                        "last_price": latest_data.get("last_price", 0.0),
                        "last_dividend": latest_data.get("last_dividend", 0.0),
                        # Bid price based Greeks
                        "bid_imp_vol": latest_data.get("bid_imp_vol", 0.0),
                        "bid_delta": latest_data.get("bid_delta", 0.0),
                        "bid_gamma": latest_data.get("bid_gamma", 0.0),
                        "bid_vega": latest_data.get("bid_vega", 0.0),
                        "bid_theta": latest_data.get("bid_theta", 0.0),
                        "bid_price": latest_data.get("bid_price", 0.0),
                        "bid_dividend": latest_data.get("bid_dividend", 0.0),
                        # Ask price based Greeks
                        "ask_imp_vol": latest_data.get("ask_imp_vol", 0.0),
                        "ask_delta": latest_data.get("ask_delta", 0.0),
                        "ask_gamma": latest_data.get("ask_gamma", 0.0),
                        "ask_vega": latest_data.get("ask_vega", 0.0),
                        "ask_theta": latest_data.get("ask_theta", 0.0),
                        "ask_price": latest_data.get("ask_price", 0.0),
                        "ask_dividend": latest_data.get("ask_dividend", 0.0)
                    }
                })
            
            return {
                "success": True,
                "data": formatted_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting market data: {str(e)}",
                "contract_string": contract_string
            }

    @mcp.tool()
    async def unsubscribe_market_data(ctx: Context, contract_string: str) -> dict:
        """
        Unsubscribe from market data for a contract.
        
        Stops receiving real-time updates for the specified contract to:
        - Reduce data feed costs
        - Free up subscription slots
        - Stop unnecessary data streaming
        - Clean up resources
        
        Args:
            ctx: The context containing the ezib connection
            contract_string: Contract identifier to unsubscribe
            
        Returns:
            dict: Unsubscribe operation result
            
        Example:
            unsubscribe_market_data(contract_string="AAPL_STK")
            # Stops AAPL market data subscription
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
            
            if ticker_id == 0:
                return {
                    "success": False,
                    "error": f"Invalid contract string: {contract_string}",
                    "contract_string": contract_string
                }
            
            # Get contract object from ticker ID
            contract = ezib.contracts.get(ticker_id)
            if not contract:
                return {
                    "success": False,
                    "error": f"Contract not found for {contract_string}",
                    "contract_string": contract_string
                }
            
            # Unsubscribe from market data using cancelMarketData (synchronous)
            ezib.cancelMarketData([contract])
            success = True
            
            if success:
                return {
                    "success": True,
                    "message": f"Successfully unsubscribed from market data for {contract_string}",
                    "contract_string": contract_string,
                    "ticker_id": ticker_id
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to unsubscribe from market data for {contract_string}",
                    "contract_string": contract_string
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error unsubscribing from market data: {str(e)}",
                "contract_string": contract_string
            }

    @mcp.tool()
    async def get_historical_data(ctx: Context, contract_string: str, duration: str = "1 D",
                                 bar_size: str = "1 min", data_type: str = "TRADES") -> dict:
        """
        Get historical market data for analysis and backtesting.
        
        Retrieves historical bars for:
        - Price action analysis
        - Technical indicator calculations
        - Backtesting strategies
        - Chart pattern recognition
        - Volume analysis
        
        Args:
            ctx: The context containing the ezib connection
            contract_string: Contract identifier
            duration: Time period (e.g., "1 D", "1 W", "1 M", "1 Y")
            bar_size: Bar interval ("1 sec", "5 secs", "15 secs", "30 secs", "1 min", "2 mins", "3 mins", "5 mins", "15 mins", "30 mins", "1 hour", "1 day")
            data_type: Data type ("TRADES", "MIDPOINT", "BID", "ASK")
            
        Returns:
            dict: Historical data with OHLCV bars
            
        Example:
            get_historical_data(contract_string="AAPL_STK", duration="5 D", bar_size="1 hour")
            # Gets 5 days of hourly AAPL data
            
            get_historical_data(contract_string="ES_FUT", duration="1 D", bar_size="5 mins", data_type="TRADES")
            # Gets 1 day of 5-minute ES futures trade data
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
            
            if ticker_id == 0:
                return {
                    "success": False,
                    "error": f"Invalid contract string: {contract_string}",
                    "contract_string": contract_string
                }
            
            # Request historical data
            historical_data = await ezib.getHistoricalData(
                ticker_id=ticker_id,
                duration=duration,
                barSize=bar_size,
                whatToShow=data_type
            )
            
            if historical_data:
                return {
                    "success": True,
                    "data": {
                        "contract_string": contract_string,
                        "ticker_id": ticker_id,
                        "parameters": {
                            "duration": duration,
                            "bar_size": bar_size,
                            "data_type": data_type
                        },
                        "bars": historical_data,
                        "bar_count": len(historical_data)
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"No historical data available for {contract_string}",
                    "contract_string": contract_string
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting historical data: {str(e)}",
                "contract_string": contract_string,
                "parameters": {
                    "duration": duration,
                    "bar_size": bar_size,
                    "data_type": data_type
                }
            }

    @mcp.tool()
    async def list_active_subscriptions(ctx: Context) -> dict:
        """
        List all active market data subscriptions.
        
        Provides overview of:
        - Currently subscribed contracts
        - Subscription status and data types
        - Last update timestamps
        - Data feed costs tracking
        - Available subscription slots
        
        Args:
            ctx: The context containing the ezib connection
            
        Returns:
            dict: List of active subscriptions with details
            
        Example:
            list_active_subscriptions()
            # Returns all active market data subscriptions
        """
        connection_manager = ctx.request_context.lifespan_context.connection_manager
        
        if not connection_manager.is_connected:
            return {
                "success": False,
                "error": "Not connected to Interactive Brokers"
            }
        
        try:
            ezib = connection_manager.ezib
            
            # Get all market data subscriptions (both regular and options)
            all_market_data = {}
            all_market_data.update(ezib.marketData)  # Regular market data
            all_market_data.update(ezib.optionsData)  # Options market data
            
            subscriptions = []
            for ticker_id, data in all_market_data.items():
                # Get contract string from ticker ID
                contract_string = None
                for contract_str, tid in ezib.tickerIds.items():
                    if tid == ticker_id:
                        contract_string = contract_str
                        break
                
                # Extract latest data from DataFrame (data is a DataFrame, not a dict)
                if data is not None and len(data) > 0:
                    latest_data = data.iloc[-1]
                    if hasattr(latest_data, 'to_dict'):
                        latest_data = latest_data.to_dict()
                    
                    # Ensure we get scalar values, not Series
                    last_price = latest_data.get("last", 0)
                    if hasattr(last_price, 'item'):
                        last_price = last_price.item() if not pd.isna(last_price) else 0
                    
                    bid_price = latest_data.get("bid", 0)
                    if hasattr(bid_price, 'item'):
                        bid_price = bid_price.item() if not pd.isna(bid_price) else 0
                    
                    ask_price = latest_data.get("ask", 0)
                    if hasattr(ask_price, 'item'):
                        ask_price = ask_price.item() if not pd.isna(ask_price) else 0
                    
                    timestamp = latest_data.get("timestamp", "")
                    if hasattr(timestamp, 'item'):
                        timestamp = timestamp.item() if not pd.isna(timestamp) else ""
                    
                    # Convert to float/int for safe comparison
                    last_price = float(last_price) if last_price else 0.0
                    bid_price = float(bid_price) if bid_price else 0.0
                    ask_price = float(ask_price) if ask_price else 0.0
                    
                    has_data = bool(last_price or bid_price or ask_price)
                    status = "active" if (last_price or bid_price) else "subscribed"
                else:
                    # No data available yet
                    timestamp = ""
                    has_data = False
                    status = "subscribed"
                
                # 获取实际的 marketDataType
                data_type_num = 1  # 默认 Live
                if contract_string:
                    # 使用 ticker_id 获取合约对象（ezib.contracts 使用 ticker_id 作为 key）
                    contract = ezib.contracts.get(ticker_id)
                    if contract:
                        # 获取对应的 ticker 对象
                        ticker = ezib.ib.ticker(contract)
                        if ticker:
                            data_type_num = ticker.marketDataType
                
                # 映射为可读字符串
                data_type_map = {
                    1: "realtime",
                    2: "frozen", 
                    3: "delayed",
                    4: "delayed_frozen"
                }
                actual_data_type = data_type_map.get(data_type_num, "realtime")
                
                subscription_info = {
                    "ticker_id": ticker_id,
                    "contract_string": contract_string or f"ticker_{ticker_id}",
                    "last_update": timestamp,
                    "data_type": actual_data_type,  # 使用实际的 marketDataType
                    "has_data": has_data,
                    "status": status
                }
                subscriptions.append(subscription_info)
            
            return {
                "success": True,
                "subscriptions": subscriptions,
                "total_subscriptions": len(subscriptions),
                "active_data_feeds": len([s for s in subscriptions if s["has_data"]]),
                "message": f"Found {len(subscriptions)} active market data subscriptions"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error listing subscriptions: {str(e)}"
            }
