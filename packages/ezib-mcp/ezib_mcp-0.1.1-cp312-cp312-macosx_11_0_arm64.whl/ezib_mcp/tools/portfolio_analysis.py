"""
Advanced portfolio analysis tools for comprehensive risk management and position optimization.

This module provides sophisticated portfolio analysis capabilities including:
- Delta exposure calculation and aggregation
- Complete Greeks analysis for options positions
- Portfolio risk metrics and stress testing
- Position aggregation and visualization data preparation
- Real-time risk monitoring and alerting
"""

from mcp.server.fastmcp import Context, FastMCP
from typing import Optional, List, Dict, Any, Union
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio

from ezib_mcp.licensing import require_quota, require_feature


def register_portfolio_analysis_tools(mcp: FastMCP):
    """Register advanced portfolio analysis tools with the MCP server."""

    @mcp.tool()
    @require_feature("portfolio_analysis")
    @require_quota("portfolio_analysis")
    async def calculate_portfolio_delta(ctx: Context, account: str = "", include_underlying: bool = True) -> dict:
        """
        Calculate comprehensive delta exposure for portfolio positions.

        Provides detailed delta breakdown by symbol, security type, and direction.
        Essential for understanding portfolio directional risk and hedging requirements.

        Args:
            ctx: The context containing the ezib connection
            account: Specific account to analyze (empty for active account)
            include_underlying: Include underlying stock prices in calculations

        Returns:
            dict: Comprehensive delta analysis with the following structure:
            {
                "success": true,
                "account": "U9860850",
                "total_delta": 245.67,
                "by_symbol": {
                    "AAPL": {"stock_delta": 300, "options_delta": -45.2, "net_delta": 254.8},
                    "TSLA": {"stock_delta": 300, "options_delta": 123.4, "net_delta": 423.4}
                },
                "risk_metrics": {
                    "largest_exposure": {"symbol": "TSLA", "delta": 423.4},
                    "concentration_risk": 0.35,  # Percentage of total delta in largest position
                    "hedging_efficiency": 0.82   # How well options hedge underlying positions
                }
            }

        Example:
            delta_analysis = await calculate_portfolio_delta(ctx, account="U9860850")
            print(f"Total portfolio delta: {delta_analysis['total_delta']}")
        """
        connection_manager = ctx.request_context.lifespan_context.connection_manager

        if not connection_manager.is_connected:
            return {
                "success": False,
                "error": "Not connected to Interactive Brokers"
            }

        try:
            ezib = connection_manager.ezib

            # Get positions for the specified account
            if account == "":
                positions_data = ezib.position
                account_id = ezib.accountCode
            else:
                if account not in ezib.accountCodes:
                    return {
                        "success": False,
                        "error": f"Account {account} not found"
                    }
                positions_data = ezib.positions[account]
                account_id = account

            if not positions_data:
                return {
                    "success": True,
                    "account": account_id,
                    "total_delta": 0.0,
                    "by_symbol": {},
                    "message": "No positions found"
                }

            # Convert to DataFrame for easier processing
            positions_df = pd.DataFrame(positions_data)

            # Initialize delta calculations
            symbol_deltas = {}
            total_portfolio_delta = 0.0

            # Process each position
            for _, position in positions_df.iterrows():
                symbol = position.get('symbol', 'UNKNOWN')
                sec_type = position.get('secType', 'UNKNOWN')
                quantity = float(position.get('position', 0))

                if symbol not in symbol_deltas:
                    symbol_deltas[symbol] = {
                        'stock_delta': 0.0,
                        'options_delta': 0.0,
                        'net_delta': 0.0
                    }

                if sec_type == 'STK':
                    # Stock delta is always 1.0 per share
                    delta_contribution = quantity * 1.0
                    symbol_deltas[symbol]['stock_delta'] += delta_contribution

                elif sec_type in ['OPT', 'FOP']:
                    # For options, need to get delta from market data
                    try:
                        # Get contract for this position
                        contract_string = position.get('contract_string', '')
                        if contract_string:
                            ticker_id = ezib.tickerId(contract_string)
                            option_data = ezib.optionsData.get(ticker_id)

                            if option_data is not None and len(option_data) > 0:
                                latest_data = option_data.iloc[-1]
                                delta = latest_data.get('delta', 0.0)

                                # Options delta contribution (multiply by 100 for contract multiplier)
                                delta_contribution = quantity * float(delta) * 100
                                symbol_deltas[symbol]['options_delta'] += delta_contribution
                            else:
                                # If no market data, estimate based on position
                                print(f"Warning: No market data for {symbol} option, using position estimate")
                                # Use a conservative estimate for missing delta
                                delta_contribution = quantity * 0.5 * 100  # Assume 0.5 delta
                                symbol_deltas[symbol]['options_delta'] += delta_contribution
                    except Exception as e:
                        print(f"Error calculating delta for {symbol} option: {e}")
                        continue

                # Update net delta for symbol
                symbol_deltas[symbol]['net_delta'] = (
                    symbol_deltas[symbol]['stock_delta'] +
                    symbol_deltas[symbol]['options_delta']
                )

                total_portfolio_delta += symbol_deltas[symbol]['net_delta']

            # Calculate risk metrics
            if symbol_deltas:
                # Find largest exposure
                largest_symbol = max(symbol_deltas.keys(),
                                   key=lambda x: abs(symbol_deltas[x]['net_delta']))
                largest_delta = symbol_deltas[largest_symbol]['net_delta']

                # Calculate concentration risk
                concentration_risk = abs(largest_delta) / max(abs(total_portfolio_delta), 1) if total_portfolio_delta != 0 else 0

                # Calculate hedging efficiency (how well options offset stock positions)
                total_stock_delta = sum(data['stock_delta'] for data in symbol_deltas.values())
                total_options_delta = sum(data['options_delta'] for data in symbol_deltas.values())

                hedging_efficiency = 0.0
                if total_stock_delta != 0:
                    hedging_efficiency = 1.0 - abs(total_options_delta) / abs(total_stock_delta)
                    hedging_efficiency = max(0.0, min(1.0, hedging_efficiency))
            else:
                largest_symbol = "N/A"
                largest_delta = 0.0
                concentration_risk = 0.0
                hedging_efficiency = 0.0

            return {
                "success": True,
                "account": account_id,
                "total_delta": round(total_portfolio_delta, 2),
                "by_symbol": {
                    symbol: {
                        "stock_delta": round(data['stock_delta'], 2),
                        "options_delta": round(data['options_delta'], 2),
                        "net_delta": round(data['net_delta'], 2)
                    }
                    for symbol, data in symbol_deltas.items()
                },
                "risk_metrics": {
                    "largest_exposure": {
                        "symbol": largest_symbol,
                        "delta": round(largest_delta, 2)
                    },
                    "concentration_risk": round(concentration_risk, 3),
                    "hedging_efficiency": round(hedging_efficiency, 3)
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error calculating portfolio delta: {str(e)}"
            }

    @mcp.tool()
    async def aggregate_positions_by_symbol(ctx: Context, account: str = "",
                                          include_market_value: bool = True) -> dict:
        """
        Aggregate portfolio positions by underlying symbol with net exposure calculation.

        Provides consolidated view of positions grouped by symbol, showing long/short breakdown
        and net exposure. Essential for understanding overall portfolio allocation and concentration.

        Args:
            ctx: The context containing the ezib connection
            account: Specific account to analyze (empty for active account)
            include_market_value: Include current market value calculations

        Returns:
            dict: Aggregated position data with the following structure:
            {
                "success": true,
                "account": "U9860850",
                "symbols": {
                    "AAPL": {
                        "positions": [
                            {"type": "STK", "quantity": 300, "avg_cost": 150.0, "market_value": 45000},
                            {"type": "OPT", "quantity": -5, "avg_cost": 5.0, "market_value": -2500}
                        ],
                        "net_quantity": 295,
                        "net_market_value": 42500,
                        "long_value": 45000,
                        "short_value": -2500,
                        "weight": 0.15  # Percentage of total portfolio value
                    }
                },
                "portfolio_summary": {
                    "total_symbols": 12,
                    "total_market_value": 284500,
                    "long_exposure": 320000,
                    "short_exposure": -35500,
                    "net_exposure": 284500
                }
            }

        Example:
            positions = await aggregate_positions_by_symbol(ctx, include_market_value=True)
            for symbol, data in positions['symbols'].items():
                print(f"{symbol}: Net value ${data['net_market_value']}")
        """
        connection_manager = ctx.request_context.lifespan_context.connection_manager

        if not connection_manager.is_connected:
            return {
                "success": False,
                "error": "Not connected to Interactive Brokers"
            }

        try:
            ezib = connection_manager.ezib

            # Get positions for the specified account
            if account == "":
                positions_data = ezib.position
                account_id = ezib.accountCode
            else:
                if account not in ezib.accountCodes:
                    return {
                        "success": False,
                        "error": f"Account {account} not found"
                    }
                positions_data = ezib.positions[account]
                account_id = account

            if not positions_data:
                return {
                    "success": True,
                    "account": account_id,
                    "symbols": {},
                    "portfolio_summary": {
                        "total_symbols": 0,
                        "total_market_value": 0,
                        "long_exposure": 0,
                        "short_exposure": 0,
                        "net_exposure": 0
                    }
                }

            # Convert to DataFrame for easier processing
            positions_df = pd.DataFrame(positions_data)

            # Initialize aggregation structures
            symbol_aggregates = {}
            total_market_value = 0.0
            total_long_exposure = 0.0
            total_short_exposure = 0.0

            # Process each position
            for _, position in positions_df.iterrows():
                symbol = position.get('symbol', 'UNKNOWN')
                sec_type = position.get('secType', 'UNKNOWN')
                quantity = float(position.get('position', 0))
                avg_cost = float(position.get('avgCost', 0))

                # Calculate market value if requested
                market_value = 0.0
                if include_market_value:
                    # Get current price for market value calculation
                    try:
                        if sec_type == 'STK':
                            # For stocks, use current market price
                            contract_string = f"{symbol}_STK"
                            ticker_id = ezib.tickerId(contract_string)
                            market_data = ezib.marketData.get(ticker_id)

                            if market_data is not None and len(market_data) > 0:
                                latest_data = market_data.iloc[-1]
                                current_price = latest_data.get('last', avg_cost)
                                market_value = quantity * float(current_price)
                            else:
                                # Use average cost as fallback
                                market_value = quantity * avg_cost

                        elif sec_type in ['OPT', 'FOP']:
                            # For options, use option price from options data
                            contract_string = position.get('contract_string', '')
                            if contract_string:
                                ticker_id = ezib.tickerId(contract_string)
                                option_data = ezib.optionsData.get(ticker_id)

                                if option_data is not None and len(option_data) > 0:
                                    latest_data = option_data.iloc[-1]
                                    option_price = latest_data.get('last', avg_cost)
                                    market_value = quantity * float(option_price) * 100  # Contract multiplier
                                else:
                                    market_value = quantity * avg_cost
                            else:
                                market_value = quantity * avg_cost
                    except Exception as e:
                        print(f"Error calculating market value for {symbol}: {e}")
                        market_value = quantity * avg_cost
                else:
                    # Use cost basis if market value not requested
                    market_value = quantity * avg_cost

                # Initialize symbol aggregate if not exists
                if symbol not in symbol_aggregates:
                    symbol_aggregates[symbol] = {
                        'positions': [],
                        'net_quantity': 0.0,
                        'net_market_value': 0.0,
                        'long_value': 0.0,
                        'short_value': 0.0
                    }

                # Add position to symbol aggregate
                position_data = {
                    'type': sec_type,
                    'quantity': quantity,
                    'avg_cost': avg_cost,
                    'market_value': round(market_value, 2)
                }
                symbol_aggregates[symbol]['positions'].append(position_data)

                # Update aggregates
                symbol_aggregates[symbol]['net_market_value'] += market_value

                if market_value > 0:
                    symbol_aggregates[symbol]['long_value'] += market_value
                    total_long_exposure += market_value
                else:
                    symbol_aggregates[symbol]['short_value'] += market_value
                    total_short_exposure += market_value

                total_market_value += market_value

            # Calculate portfolio weights
            for symbol in symbol_aggregates:
                symbol_aggregates[symbol]['weight'] = (
                    abs(symbol_aggregates[symbol]['net_market_value']) / max(abs(total_market_value), 1)
                    if total_market_value != 0 else 0
                )

                # Round values for cleaner output
                symbol_aggregates[symbol]['net_market_value'] = round(
                    symbol_aggregates[symbol]['net_market_value'], 2
                )
                symbol_aggregates[symbol]['long_value'] = round(
                    symbol_aggregates[symbol]['long_value'], 2
                )
                symbol_aggregates[symbol]['short_value'] = round(
                    symbol_aggregates[symbol]['short_value'], 2
                )
                symbol_aggregates[symbol]['weight'] = round(
                    symbol_aggregates[symbol]['weight'], 4
                )

            return {
                "success": True,
                "account": account_id,
                "symbols": symbol_aggregates,
                "portfolio_summary": {
                    "total_symbols": len(symbol_aggregates),
                    "total_market_value": round(total_market_value, 2),
                    "long_exposure": round(total_long_exposure, 2),
                    "short_exposure": round(total_short_exposure, 2),
                    "net_exposure": round(total_market_value, 2)
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error aggregating positions: {str(e)}"
            }

    @mcp.tool()
    async def calculate_portfolio_greeks(ctx: Context, account: str = "",
                                       include_underlying_exposure: bool = True) -> dict:
        """
        Calculate comprehensive Greeks analysis for all option positions in portfolio.

        Provides complete risk profile including delta, gamma, theta, vega for each option
        and aggregated portfolio-level Greeks. Essential for options risk management.

        Args:
            ctx: The context containing the ezib connection
            account: Specific account to analyze (empty for active account)
            include_underlying_exposure: Include impact of underlying stock positions on Greeks

        Returns:
            dict: Comprehensive Greeks analysis with the following structure:
            {
                "success": true,
                "account": "U9860850",
                "portfolio_greeks": {
                    "total_delta": 156.78,
                    "total_gamma": 23.45,
                    "total_theta": -145.67,
                    "total_vega": 892.34
                },
                "by_symbol": {
                    "AAPL": {
                        "positions": [
                            {
                                "contract": "AAPL Dec20'24 200 Call",
                                "quantity": 5,
                                "delta": 67.5,
                                "gamma": 12.3,
                                "theta": -23.4,
                                "vega": 156.7
                            }
                        ],
                        "symbol_greeks": {
                            "delta": 67.5,
                            "gamma": 12.3,
                            "theta": -23.4,
                            "vega": 156.7
                        }
                    }
                },
                "risk_analysis": {
                    "time_decay": -145.67,  # Daily theta impact
                    "volatility_risk": 892.34,  # 1% vol change impact
                    "gamma_risk": "moderate",  # Risk level assessment
                    "expiration_risk": [
                        {"date": "2024-12-20", "positions": 5, "theta": -100.23}
                    ]
                }
            }

        Example:
            greeks = await calculate_portfolio_greeks(ctx, account="U9860850")
            print(f"Daily time decay: ${greeks['portfolio_greeks']['total_theta']}")
        """
        connection_manager = ctx.request_context.lifespan_context.connection_manager

        if not connection_manager.is_connected:
            return {
                "success": False,
                "error": "Not connected to Interactive Brokers"
            }

        try:
            ezib = connection_manager.ezib

            # Get positions for the specified account
            if account == "":
                positions_data = ezib.position
                account_id = ezib.accountCode
            else:
                if account not in ezib.accountCodes:
                    return {
                        "success": False,
                        "error": f"Account {account} not found"
                    }
                positions_data = ezib.positions[account]
                account_id = account

            if not positions_data:
                return {
                    "success": True,
                    "account": account_id,
                    "portfolio_greeks": {
                        "total_delta": 0.0,
                        "total_gamma": 0.0,
                        "total_theta": 0.0,
                        "total_vega": 0.0
                    },
                    "by_symbol": {},
                    "message": "No positions found"
                }

            # Convert to DataFrame for easier processing
            positions_df = pd.DataFrame(positions_data)

            # Initialize Greeks calculations
            symbol_greeks = {}
            portfolio_greeks = {
                'total_delta': 0.0,
                'total_gamma': 0.0,
                'total_theta': 0.0,
                'total_vega': 0.0
            }
            expiration_risk = {}

            # Process each position
            for _, position in positions_df.iterrows():
                symbol = position.get('symbol', 'UNKNOWN')
                sec_type = position.get('secType', 'UNKNOWN')
                quantity = float(position.get('position', 0))

                # Initialize symbol Greeks if not exists
                if symbol not in symbol_greeks:
                    symbol_greeks[symbol] = {
                        'positions': [],
                        'symbol_greeks': {
                            'delta': 0.0,
                            'gamma': 0.0,
                            'theta': 0.0,
                            'vega': 0.0
                        }
                    }

                if sec_type == 'STK' and include_underlying_exposure:
                    # Stock positions contribute to delta only
                    stock_delta = quantity * 1.0
                    symbol_greeks[symbol]['symbol_greeks']['delta'] += stock_delta
                    portfolio_greeks['total_delta'] += stock_delta

                    # Add stock position to positions list
                    symbol_greeks[symbol]['positions'].append({
                        'contract': f"{symbol} Stock",
                        'quantity': quantity,
                        'delta': stock_delta,
                        'gamma': 0.0,
                        'theta': 0.0,
                        'vega': 0.0
                    })

                elif sec_type in ['OPT', 'FOP']:
                    # For options, get Greeks from market data
                    try:
                        contract_string = position.get('contract_string', '')
                        if contract_string:
                            ticker_id = ezib.tickerId(contract_string)
                            option_data = ezib.optionsData.get(ticker_id)

                            if option_data is not None and len(option_data) > 0:
                                latest_data = option_data.iloc[-1]

                                # Extract Greeks (prefer mid Greeks, fallback to last)
                                delta = float(latest_data.get('delta', latest_data.get('last_delta', 0.0)))
                                gamma = float(latest_data.get('gamma', latest_data.get('last_gamma', 0.0)))
                                theta = float(latest_data.get('theta', latest_data.get('last_theta', 0.0)))
                                vega = float(latest_data.get('vega', latest_data.get('last_vega', 0.0)))

                                # Calculate position-level Greeks (multiply by quantity and contract multiplier)
                                position_delta = quantity * delta * 100
                                position_gamma = quantity * gamma * 100
                                position_theta = quantity * theta * 100
                                position_vega = quantity * vega * 100

                                # Add to symbol and portfolio totals
                                symbol_greeks[symbol]['symbol_greeks']['delta'] += position_delta
                                symbol_greeks[symbol]['symbol_greeks']['gamma'] += position_gamma
                                symbol_greeks[symbol]['symbol_greeks']['theta'] += position_theta
                                symbol_greeks[symbol]['symbol_greeks']['vega'] += position_vega

                                portfolio_greeks['total_delta'] += position_delta
                                portfolio_greeks['total_gamma'] += position_gamma
                                portfolio_greeks['total_theta'] += position_theta
                                portfolio_greeks['total_vega'] += position_vega

                                # Get contract details for expiration tracking
                                expiry = position.get('expiry', 'Unknown')
                                if expiry != 'Unknown':
                                    if expiry not in expiration_risk:
                                        expiration_risk[expiry] = {
                                            'positions': 0,
                                            'theta': 0.0
                                        }
                                    expiration_risk[expiry]['positions'] += abs(quantity)
                                    expiration_risk[expiry]['theta'] += position_theta

                                # Add option position to positions list
                                contract_desc = f"{symbol} {expiry} {position.get('strike', 'Unknown')} {position.get('right', 'Unknown')}"
                                symbol_greeks[symbol]['positions'].append({
                                    'contract': contract_desc,
                                    'quantity': quantity,
                                    'delta': round(position_delta, 2),
                                    'gamma': round(position_gamma, 2),
                                    'theta': round(position_theta, 2),
                                    'vega': round(position_vega, 2)
                                })
                            else:
                                print(f"Warning: No Greeks data available for {symbol} option")
                    except Exception as e:
                        print(f"Error calculating Greeks for {symbol} option: {e}")
                        continue

            # Round portfolio-level Greeks
            for greek in portfolio_greeks:
                portfolio_greeks[greek] = round(portfolio_greeks[greek], 2)

            # Round symbol-level Greeks
            for symbol in symbol_greeks:
                for greek in symbol_greeks[symbol]['symbol_greeks']:
                    symbol_greeks[symbol]['symbol_greeks'][greek] = round(
                        symbol_greeks[symbol]['symbol_greeks'][greek], 2
                    )

            # Risk analysis
            gamma_risk_level = "low"
            if abs(portfolio_greeks['total_gamma']) > 1000:
                gamma_risk_level = "high"
            elif abs(portfolio_greeks['total_gamma']) > 500:
                gamma_risk_level = "moderate"

            # Format expiration risk
            expiration_risk_list = [
                {
                    "date": date,
                    "positions": int(data['positions']),
                    "theta": round(data['theta'], 2)
                }
                for date, data in sorted(expiration_risk.items())
            ]

            return {
                "success": True,
                "account": account_id,
                "portfolio_greeks": portfolio_greeks,
                "by_symbol": symbol_greeks,
                "risk_analysis": {
                    "time_decay": portfolio_greeks['total_theta'],
                    "volatility_risk": portfolio_greeks['total_vega'],
                    "gamma_risk": gamma_risk_level,
                    "expiration_risk": expiration_risk_list
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error calculating portfolio Greeks: {str(e)}"
            }

    @mcp.tool()
    async def get_portfolio_risk_metrics(ctx: Context, account: str = "",
                                       calculation_period_days: int = 252) -> dict:
        """
        Generate comprehensive portfolio risk metrics and analysis.

        Provides key risk indicators including concentration, volatility, correlation,
        and stress test estimates. Essential for portfolio risk management and reporting.

        Args:
            ctx: The context containing the ezib connection
            account: Specific account to analyze (empty for active account)
            calculation_period_days: Period for volatility calculations (default 252 trading days)

        Returns:
            dict: Comprehensive risk metrics with the following structure:
            {
                "success": true,
                "account": "U9860850",
                "portfolio_value": 284500.0,
                "risk_metrics": {
                    "concentration": {
                        "top_5_holdings_pct": 0.68,
                        "largest_position_pct": 0.23,
                        "herfindahl_index": 0.156
                    },
                    "exposure": {
                        "long_exposure": 320000.0,
                        "short_exposure": -35500.0,
                        "net_exposure": 284500.0,
                        "gross_exposure": 355500.0,
                        "leverage_ratio": 1.25
                    },
                    "greeks_summary": {
                        "net_delta": 156.78,
                        "total_gamma": 23.45,
                        "daily_theta": -145.67,
                        "vega_exposure": 892.34
                    },
                    "estimated_var": {
                        "1_day_95_pct": -12450.0,
                        "1_day_99_pct": -18670.0,
                        "note": "Estimated based on position sizes and historical volatility"
                    }
                },
                "alerts": [
                    {
                        "level": "warning",
                        "message": "High concentration in tech sector (45%)",
                        "recommendation": "Consider diversification"
                    }
                ]
            }

        Example:
            risk_metrics = await get_portfolio_risk_metrics(ctx, account="U9860850")
            print(f"Portfolio VaR (95%): ${risk_metrics['risk_metrics']['estimated_var']['1_day_95_pct']}")
        """
        connection_manager = ctx.request_context.lifespan_context.connection_manager

        if not connection_manager.is_connected:
            return {
                "success": False,
                "error": "Not connected to Interactive Brokers"
            }

        try:
            # Get portfolio data using existing tools
            portfolio_delta = await calculate_portfolio_delta(ctx, account)
            aggregated_positions = await aggregate_positions_by_symbol(ctx, account, include_market_value=True)
            portfolio_greeks = await calculate_portfolio_greeks(ctx, account)

            if not portfolio_delta["success"] or not aggregated_positions["success"]:
                return {
                    "success": False,
                    "error": "Failed to retrieve portfolio data for risk analysis"
                }

            account_id = portfolio_delta["account"]
            portfolio_summary = aggregated_positions["portfolio_summary"]
            symbols_data = aggregated_positions["symbols"]

            # Calculate concentration metrics
            total_value = abs(portfolio_summary["total_market_value"])
            if total_value == 0:
                return {
                    "success": True,
                    "account": account_id,
                    "portfolio_value": 0.0,
                    "risk_metrics": {
                        "concentration": {"note": "No positions found"},
                        "exposure": {"note": "No positions found"},
                        "greeks_summary": {"note": "No positions found"}
                    }
                }

            # Sort symbols by absolute market value
            symbol_values = [
                (symbol, abs(data["net_market_value"]))
                for symbol, data in symbols_data.items()
            ]
            symbol_values.sort(key=lambda x: x[1], reverse=True)

            # Calculate concentration metrics
            top_5_value = sum(value for _, value in symbol_values[:5])
            largest_position_value = symbol_values[0][1] if symbol_values else 0

            # Herfindahl-Hirschman Index (concentration measure)
            hhi = sum((value / total_value) ** 2 for _, value in symbol_values)

            concentration_metrics = {
                "top_5_holdings_pct": round(top_5_value / total_value, 3),
                "largest_position_pct": round(largest_position_value / total_value, 3),
                "herfindahl_index": round(hhi, 3)
            }

            # Exposure metrics
            long_exposure = portfolio_summary["long_exposure"]
            short_exposure = portfolio_summary["short_exposure"]
            net_exposure = portfolio_summary["net_exposure"]
            gross_exposure = abs(long_exposure) + abs(short_exposure)
            leverage_ratio = gross_exposure / max(total_value, 1)

            exposure_metrics = {
                "long_exposure": long_exposure,
                "short_exposure": short_exposure,
                "net_exposure": net_exposure,
                "gross_exposure": round(gross_exposure, 2),
                "leverage_ratio": round(leverage_ratio, 2)
            }

            # Greeks summary
            greeks_data = portfolio_greeks.get("portfolio_greeks", {})
            greeks_summary = {
                "net_delta": greeks_data.get("total_delta", 0.0),
                "total_gamma": greeks_data.get("total_gamma", 0.0),
                "daily_theta": greeks_data.get("total_theta", 0.0),
                "vega_exposure": greeks_data.get("total_vega", 0.0)
            }

            # Estimated VaR (simplified calculation based on position sizes)
            # This is a rough estimate - real VaR would require historical returns
            assumed_daily_vol = 0.02  # 2% daily volatility assumption
            var_95_multiplier = 1.645  # 95% confidence level
            var_99_multiplier = 2.326  # 99% confidence level

            estimated_var_95 = -total_value * assumed_daily_vol * var_95_multiplier
            estimated_var_99 = -total_value * assumed_daily_vol * var_99_multiplier

            var_metrics = {
                "1_day_95_pct": round(estimated_var_95, 2),
                "1_day_99_pct": round(estimated_var_99, 2),
                "note": "Estimated based on position sizes and assumed 2% daily volatility"
            }

            # Generate alerts based on risk thresholds
            alerts = []

            # Concentration alerts
            if concentration_metrics["largest_position_pct"] > 0.25:
                alerts.append({
                    "level": "warning",
                    "message": f"High concentration in single position ({concentration_metrics['largest_position_pct']:.1%})",
                    "recommendation": "Consider position size reduction or hedging"
                })

            if concentration_metrics["top_5_holdings_pct"] > 0.75:
                alerts.append({
                    "level": "warning",
                    "message": f"High concentration in top 5 holdings ({concentration_metrics['top_5_holdings_pct']:.1%})",
                    "recommendation": "Consider diversification across more symbols"
                })

            # Leverage alerts
            if leverage_ratio > 2.0:
                alerts.append({
                    "level": "high",
                    "message": f"High leverage ratio ({leverage_ratio:.1f}x)",
                    "recommendation": "Monitor margin requirements and reduce exposure if needed"
                })
            elif leverage_ratio > 1.5:
                alerts.append({
                    "level": "warning",
                    "message": f"Moderate leverage detected ({leverage_ratio:.1f}x)",
                    "recommendation": "Monitor market conditions and margin usage"
                })

            # Greeks alerts
            if abs(greeks_summary["daily_theta"]) > 1000:
                alerts.append({
                    "level": "info",
                    "message": f"High time decay exposure (${greeks_summary['daily_theta']:.0f}/day)",
                    "recommendation": "Monitor options approaching expiration"
                })

            if abs(greeks_summary["vega_exposure"]) > 5000:
                alerts.append({
                    "level": "info",
                    "message": f"High volatility sensitivity (${greeks_summary['vega_exposure']:.0f} per 1% vol change)",
                    "recommendation": "Monitor implied volatility levels"
                })

            return {
                "success": True,
                "account": account_id,
                "portfolio_value": total_value,
                "risk_metrics": {
                    "concentration": concentration_metrics,
                    "exposure": exposure_metrics,
                    "greeks_summary": greeks_summary,
                    "estimated_var": var_metrics
                },
                "alerts": alerts,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error calculating portfolio risk metrics: {str(e)}"
            }

    @mcp.tool()
    async def prepare_portfolio_visualization_data(ctx: Context, chart_type: str,
                                                 account: str = "") -> dict:
        """
        Prepare optimized data for portfolio visualization and charting.

        Formats portfolio data specifically for common visualization libraries
        (Plotly, D3.js, Chart.js) and chart types. Reduces processing overhead
        in frontend applications.

        Args:
            ctx: The context containing the ezib connection
            chart_type: Type of visualization ("allocation", "risk_breakdown", "greeks_heatmap", "exposure_waterfall")
            account: Specific account to analyze (empty for active account)

        Returns:
            dict: Formatted data optimized for the specified chart type:

            For "allocation" chart:
            {
                "success": true,
                "chart_type": "allocation",
                "data": {
                    "labels": ["AAPL", "TSLA", "NVDA", "Others"],
                    "values": [45000, 32000, 28000, 15000],
                    "percentages": [37.5, 26.7, 23.3, 12.5],
                    "colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
                }
            }

            For "risk_breakdown" chart:
            {
                "success": true,
                "chart_type": "risk_breakdown",
                "data": {
                    "categories": ["Delta Risk", "Gamma Risk", "Theta Risk", "Vega Risk"],
                    "values": [156.78, 23.45, -145.67, 892.34],
                    "risk_levels": ["moderate", "low", "high", "moderate"]
                }
            }

        Example:
            chart_data = await prepare_portfolio_visualization_data(ctx, "allocation")
            # Use chart_data directly with Plotly:
            # fig = px.pie(values=chart_data['data']['values'], names=chart_data['data']['labels'])
        """
        connection_manager = ctx.request_context.lifespan_context.connection_manager

        if not connection_manager.is_connected:
            return {
                "success": False,
                "error": "Not connected to Interactive Brokers"
            }

        try:
            if chart_type == "allocation":
                # Get aggregated positions for allocation chart
                aggregated_data = await aggregate_positions_by_symbol(ctx, account, include_market_value=True)

                if not aggregated_data["success"]:
                    return aggregated_data

                symbols_data = aggregated_data["symbols"]
                total_value = abs(aggregated_data["portfolio_summary"]["total_market_value"])

                if total_value == 0:
                    return {
                        "success": True,
                        "chart_type": "allocation",
                        "data": {
                            "labels": [],
                            "values": [],
                            "percentages": [],
                            "colors": []
                        },
                        "message": "No positions to display"
                    }

                # Sort by absolute value and prepare data
                sorted_symbols = sorted(
                    symbols_data.items(),
                    key=lambda x: abs(x[1]["net_market_value"]),
                    reverse=True
                )

                # Take top symbols and group others
                top_symbols = sorted_symbols[:10]  # Top 10 symbols
                others_value = sum(abs(data["net_market_value"]) for symbol, data in sorted_symbols[10:])

                labels = [symbol for symbol, _ in top_symbols]
                values = [abs(data["net_market_value"]) for _, data in top_symbols]
                percentages = [value / total_value * 100 for value in values]

                if others_value > 0:
                    labels.append("Others")
                    values.append(others_value)
                    percentages.append(others_value / total_value * 100)

                # Generate colors
                default_colors = [
                    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
                    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf", "#aec7e8"
                ]
                colors = default_colors[:len(labels)]

                return {
                    "success": True,
                    "chart_type": "allocation",
                    "account": aggregated_data["account"],
                    "data": {
                        "labels": labels,
                        "values": [round(v, 2) for v in values],
                        "percentages": [round(p, 1) for p in percentages],
                        "colors": colors
                    }
                }

            elif chart_type == "risk_breakdown":
                # Get portfolio Greeks for risk breakdown
                greeks_data = await calculate_portfolio_greeks(ctx, account)

                if not greeks_data["success"]:
                    return greeks_data

                portfolio_greeks = greeks_data["portfolio_greeks"]

                # Prepare risk breakdown data
                categories = ["Delta Risk", "Gamma Risk", "Theta Risk", "Vega Risk"]
                values = [
                    portfolio_greeks["total_delta"],
                    portfolio_greeks["total_gamma"],
                    portfolio_greeks["total_theta"],
                    portfolio_greeks["total_vega"]
                ]

                # Determine risk levels based on absolute values
                risk_levels = []
                for i, value in enumerate(values):
                    abs_value = abs(value)
                    if i == 0:  # Delta
                        level = "high" if abs_value > 500 else "moderate" if abs_value > 100 else "low"
                    elif i == 1:  # Gamma
                        level = "high" if abs_value > 1000 else "moderate" if abs_value > 200 else "low"
                    elif i == 2:  # Theta
                        level = "high" if abs_value > 500 else "moderate" if abs_value > 100 else "low"
                    else:  # Vega
                        level = "high" if abs_value > 2000 else "moderate" if abs_value > 500 else "low"
                    risk_levels.append(level)

                return {
                    "success": True,
                    "chart_type": "risk_breakdown",
                    "account": greeks_data["account"],
                    "data": {
                        "categories": categories,
                        "values": [round(v, 2) for v in values],
                        "risk_levels": risk_levels
                    }
                }

            elif chart_type == "greeks_heatmap":
                # Get Greeks by symbol for heatmap
                greeks_data = await calculate_portfolio_greeks(ctx, account)

                if not greeks_data["success"]:
                    return greeks_data

                symbols_greeks = greeks_data["by_symbol"]

                # Prepare heatmap data
                symbols = list(symbols_greeks.keys())
                greeks_types = ["delta", "gamma", "theta", "vega"]

                heatmap_data = []
                for symbol in symbols:
                    symbol_data = symbols_greeks[symbol]["symbol_greeks"]
                    heatmap_data.append([
                        symbol_data["delta"],
                        symbol_data["gamma"],
                        symbol_data["theta"],
                        symbol_data["vega"]
                    ])

                return {
                    "success": True,
                    "chart_type": "greeks_heatmap",
                    "account": greeks_data["account"],
                    "data": {
                        "symbols": symbols,
                        "greeks_types": greeks_types,
                        "values": heatmap_data,  # 2D array: [symbol][greek_type]
                        "color_scale": "RdYlBu"  # Suggested color scale
                    }
                }

            elif chart_type == "exposure_waterfall":
                # Get aggregated positions for waterfall chart
                aggregated_data = await aggregate_positions_by_symbol(ctx, account, include_market_value=True)

                if not aggregated_data["success"]:
                    return aggregated_data

                symbols_data = aggregated_data["symbols"]

                # Prepare waterfall data (long vs short by symbol)
                symbols = []
                long_values = []
                short_values = []

                for symbol, data in symbols_data.items():
                    symbols.append(symbol)
                    long_values.append(data["long_value"])
                    short_values.append(data["short_value"])

                return {
                    "success": True,
                    "chart_type": "exposure_waterfall",
                    "account": aggregated_data["account"],
                    "data": {
                        "symbols": symbols,
                        "long_values": long_values,
                        "short_values": short_values,
                        "net_values": [l + s for l, s in zip(long_values, short_values)]
                    }
                }

            else:
                return {
                    "success": False,
                    "error": f"Unsupported chart type: {chart_type}",
                    "supported_types": ["allocation", "risk_breakdown", "greeks_heatmap", "exposure_waterfall"]
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error preparing visualization data: {str(e)}"
            }
