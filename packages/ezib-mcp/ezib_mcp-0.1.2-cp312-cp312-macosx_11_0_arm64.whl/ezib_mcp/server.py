"""
MIT License

Copyright (c) 2025 Kelvin Gao

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import asyncio
# import sys
# import logging
# import traceback
from datetime import datetime
from typing import AsyncIterator, Optional, Any

from mcp.server.fastmcp import FastMCP, Context
from ezib_mcp.tools.contract_management import register_contract_tools
from ezib_mcp.tools.market_data import register_market_data_tools
from contextlib import asynccontextmanager
from dataclasses import dataclass
from ezib_async import ezIBAsync
from starlette.middleware.cors import CORSMiddleware

# Configure logging FIRST before any imports that might use it
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     handlers=[
#         logging.StreamHandler(sys.stdout),
#         logging.FileHandler("/tmp/mcp_server.log", mode="a")
#         if os.path.exists("/tmp")
#         else logging.NullHandler(),
#     ],
# )
# logger = logging.getLogger(__name__)

from dotenv import load_dotenv

load_dotenv()

class EzIBConnectionManager:
    """
    Intelligent connection manager for Interactive Brokers with portfolio polling and dynamic account switching.
    
    This singleton class provides:
    - Automated portfolio data collection for all accounts
    - Dynamic account switching for trading operations  
    - Intelligent polling that adapts to user preferences
    - Unified connection lifecycle management
    """
    _instance = None
    _ezib = None
    
    # State management
    _current_target_account: Optional[str] = None  # User dynamically set account
    _env_default_account: Optional[str] = None     # Environment default account
    _polling_interval: int = 5                     # Polling interval in minutes
    _is_polling: bool = False                      # Polling task status
    _last_poll_time: Optional[datetime] = None     # Last polling timestamp
    _polling_task: Optional[asyncio.Task] = None   # Background polling task
    _connection_count: int = 0                     # Total connection attempts counter
    _poll_cycle_count: int = 0                     # Total polling cycles completed
    
    # Periodic connection state tracking
    _connected_accounts_in_cycle: set = None        # Accounts connected in current cycle
    _cycle_start_time: Optional[datetime] = None    # Current cycle start time
    
    def __new__(cls):
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self):
        """
        Initialize configuration, create ezIB instance, establish initial connection and start polling.
        
        Creates the ezIB instance, connects to IB Gateway for account discovery, 
        and records the actual connected account for polling optimization.
        """
        if self._ezib is not None:
            return
            
        # Load configuration from environment
        self._env_default_account = os.getenv("IB_ACCOUNT")
        self._polling_interval = int(os.getenv("IB_POLLING_INTERVAL_MINUTES", "5"))
        
        print(f"🔧 Configuration loaded:")
        print(f"   Default account: {self._env_default_account or 'Auto-detect'}")
        print(f"   Polling interval: {self._polling_interval} minutes")
        
        # Create ezIB instance
        self._ezib = ezIBAsync(
            ibhost=os.getenv("IB_HOST", "127.0.0.1"),
            ibport=os.getenv("IB_PORT", "4001"),
            ibclient=os.getenv("IB_CLIENTID", "0")
        )
        print(f"🏗️ ezIB instance created")
        
        # Establish initial connection WITHOUT specifying account to discover all accounts
        print("🔌 Establishing initial connection to IB Gateway (discovering accounts)...")
        try:
            await self._ezib.connectAsync()  # No account specified - discovers all accounts
            self._connection_count += 1
            await asyncio.sleep(3)  # Allow time for account discovery
            
            # Verify accounts were discovered
            if not hasattr(self._ezib, 'accountCodes') or not self._ezib.accountCodes:
                raise Exception("Failed to discover accounts after initial connection")
            
            print(f"✅ Account discovery completed - Available accounts: {list(self._ezib.accountCodes)}")
            
            # Get the actual connected/active account ID
            # Try multiple ways to get the active account
            active_account_id = None
            if hasattr(self._ezib, 'account') and self._ezib.account:
                if isinstance(self._ezib.account, str):
                    active_account_id = self._ezib.account
                elif isinstance(self._ezib.account, dict) and 'account' in self._ezib.account:
                    active_account_id = self._ezib.account['account']
                elif len(self._ezib.accountCodes) == 1:
                    # If only one account, it must be the active one
                    active_account_id = list(self._ezib.accountCodes)[0]
            
            # Fallback: use the first account if we can't determine the active one
            if not active_account_id and self._ezib.accountCodes:
                active_account_id = list(self._ezib.accountCodes)[0]
                print(f"⚠️ Could not determine active account, using first available: {active_account_id}")
            
            if not active_account_id:
                raise Exception("Could not determine active account ID after connection")
            
            print(f"🎯 Active account after initial connection: {active_account_id}")
            
            # Initialize cycle tracking and record the active account
            self._connected_accounts_in_cycle = set()
            self._cycle_start_time = datetime.now()
            self._connected_accounts_in_cycle.add(active_account_id)
            
            print(f"📝 Active account {active_account_id} recorded in cycle tracking")
            print(f"🔄 Cycle tracking initialized at {self._cycle_start_time.strftime('%H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Failed to establish initial connection: {e}")
            raise e
        
        # Start polling task (now skips initial connection since we already connected)
        await self._start_polling_task()
        
        print(f"✅ EzIBContextManager initialized successfully with initial connection")
    
    
    async def _connect_to_account(self, account: str):
        """Connect to a specific account with cycle tracking."""
        if not self._ezib or not hasattr(self._ezib, 'accountCodes'):
            raise Exception("EzIB connection not established")
            
        if account not in self._ezib.accountCodes:
            raise ValueError(f"Account {account} not found in available accounts: {list(self._ezib.accountCodes)}")
        
        # Initialize cycle tracking if needed
        if self._connected_accounts_in_cycle is None:
            self._connected_accounts_in_cycle = set()
            self._cycle_start_time = datetime.now()
            print(f"🔄 Started new polling cycle at {self._cycle_start_time.strftime('%H:%M:%S')}")
        
        # Check if already connected in this cycle
        if account in self._connected_accounts_in_cycle:
            print(f"⏭️ Skipping {account} - already connected in current cycle")
            return
        
        try:
            # Increment connection counter
            self._connection_count += 1
            
            # Disconnect and reconnect to the target account
            self._ezib.disconnect()
            await asyncio.sleep(1)
            await self._ezib.connectAsync(account=account)
            await asyncio.sleep(2)  # Wait for account data to load
            
            # Record this account as connected in current cycle
            self._connected_accounts_in_cycle.add(account)
            
            print(f"🔄 Connected to account: {account} (Connection #{self._connection_count})")
            print(f"📊 Connected accounts in cycle: {sorted(list(self._connected_accounts_in_cycle))}")
            
        except Exception as e:
            print(f"❌ Failed to connect to account {account}: {e}")
            raise e

    def _reset_cycle_tracking(self):
        """Reset cycle connection tracking for new polling cycle."""
        if self._connected_accounts_in_cycle:
            cycle_duration = datetime.now() - self._cycle_start_time if self._cycle_start_time else None
            print(f"✅ Cycle completed - Connected to {len(self._connected_accounts_in_cycle)} accounts")
            if cycle_duration:
                print(f"⏱️ Cycle duration: {cycle_duration.total_seconds():.1f}s")
        
        self._connected_accounts_in_cycle = set()
        self._cycle_start_time = datetime.now()
        print(f"🔄 New polling cycle started at {self._cycle_start_time.strftime('%H:%M:%S')}")
    
    def _get_target_account(self) -> Optional[str]:
        """Get the target account - MUST be from ENV or MCP dynamic setting only."""
        if not self._ezib or not hasattr(self._ezib, 'accountCodes') or not self._ezib.accountCodes:
            return None
        
        # Priority 1: User dynamically set via MCP tools
        if self._current_target_account:
            if self._current_target_account in self._ezib.accountCodes:
                return self._current_target_account
            else:
                print(f"⚠️ MCP target account {self._current_target_account} not available")
                
        # Priority 2: Environment variable setting  
        if self._env_default_account:
            if self._env_default_account in self._ezib.accountCodes:
                return self._env_default_account
            else:
                print(f"⚠️ ENV target account {self._env_default_account} not available")
        
        # NO FALLBACK to first available account!
        # Target account MUST be explicitly set via ENV or MCP
        print("❌ No valid target account found!")
        print("   Please set IB_ACCOUNT environment variable or use MCP switch_active_account tool")
        print(f"   Available accounts: {list(self._ezib.accountCodes)}")
        return None
    
    async def _start_polling_task(self):
        """Start the background portfolio polling task."""
        if self._polling_task and not self._polling_task.done():
            return  # Task already running
            
        self._is_polling = True
        self._polling_task = asyncio.create_task(self._portfolio_refresh_loop())
        print(f"🔄 Started portfolio polling task (interval: {self._polling_interval} minutes)")
    
    async def _portfolio_refresh_loop(self):
        """Optimized background task for intelligent portfolio data polling."""
        print("🚀 Starting optimized portfolio polling loop...")
        print(f"📊 Initial connection already established with cycle tracking")
        
        while self._is_polling:
            try:
                # Get target account and all accounts (already discovered in initialize)
                target_account = self._get_target_account()
                all_accounts = list(self._ezib.accountCodes)
                
                if not all_accounts:
                    print("⚠️ No accounts discovered, retrying...")
                    await asyncio.sleep(60)
                    continue
                    
                if not target_account:
                    print("⚠️ No target account specified!")
                    print("   Target account must be set via:")
                    print("   1. IB_ACCOUNT environment variable, OR")  
                    print("   2. MCP switch_active_account tool")
                    print(f"   Available accounts: {all_accounts}")
                    print("   Waiting for target account configuration...")
                    await asyncio.sleep(60)
                    continue
                
                print(f"🔄 Polling cycle #{self._poll_cycle_count + 1}")
                print(f"📊 All accounts: {all_accounts}")
                print(f"🎯 Target account: {target_account}")
                print(f"✅ Already connected in cycle: {sorted(list(self._connected_accounts_in_cycle))}")
                
                # Connect to all accounts (cycle tracking will skip already connected ones)
                for account in all_accounts:
                    await self._connect_to_account(account)
                
                # Ensure we end on target account by checking the last account we connected to
                # Since _connect_to_account handles cycle tracking, we know the final connection state
                last_connected_accounts = list(self._connected_accounts_in_cycle)
                if target_account not in last_connected_accounts:
                    print(f"🎯 Ensuring final connection to target account: {target_account}")
                    await self._connect_to_account(target_account)
                else:
                    print(f"✅ Target account {target_account} already handled in this cycle")
                
                # Update polling statistics
                self._last_poll_time = datetime.now()
                self._poll_cycle_count += 1
                
                print(f"✅ Portfolio refresh completed at {self._last_poll_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"📊 Cycle #{self._poll_cycle_count} | Total connections: {self._connection_count} | Avg per cycle: {round(self._connection_count / self._poll_cycle_count, 1)}")
                
                # Reset cycle tracking for next cycle
                self._reset_cycle_tracking()
                
                # Wait for next polling cycle
                print(f"⏱️ Next refresh in {self._polling_interval} minutes...")
                await asyncio.sleep(self._polling_interval * 60)
                
            except Exception as e:
                print(f"❌ Error in portfolio polling loop: {e}")
                print("🔄 Retrying in 60 seconds...")
                await asyncio.sleep(60)
    
    async def switch_to_account(self, account: str):
        """
        Dynamically switch to a specific account and update polling target.
        
        Args:
            account: Target account to switch to
            
        Returns:
            dict: Switch operation result
        """
        if not self._ezib or not hasattr(self._ezib, 'accountCodes'):
            raise Exception("EzIB connection not established")
            
        if account not in self._ezib.accountCodes:
            raise ValueError(f"Account {account} not found in available accounts: {list(self._ezib.accountCodes)}")
        
        previous_account = getattr(self._ezib, 'account', None)
        
        try:
            # Immediately switch to the target account
            await self._connect_to_account(account)
            
            # Update polling target so future polls will end at this account
            self._current_target_account = account
            
            print(f"🔄 Account switched: {previous_account} → {account}")
            print(f"🎯 Polling target updated to: {account}")
            
            return {
                "switched_to": account,
                "previous_account": previous_account,
                "success": True,
                "message": "Account switched successfully",
                "next_poll_target": account
            }
            
        except Exception as e:
            print(f"❌ Failed to switch to account {account}: {e}")
            return {
                "switched_to": None,
                "previous_account": previous_account,
                "success": False,
                "error": str(e),
                "stayed_on": getattr(self._ezib, 'account', None)
            }
    
    async def reset_to_default_account(self):
        """Reset to environment default account and clear dynamic target."""
        if not self._env_default_account:
            return {
                "success": False,
                "error": "No default account set in environment (IB_ACCOUNT)",
                "current_account": getattr(self._ezib, 'account', None)
            }
        
        try:
            previous_account = getattr(self._ezib, 'account', None)
            await self._connect_to_account(self._env_default_account)
            
            # Clear dynamic target so polling returns to env default
            self._current_target_account = None
            
            print(f"🏠 Reset to default account: {self._env_default_account}")
            
            return {
                "success": True,
                "reset_to": self._env_default_account,
                "previous_account": previous_account,
                "message": "Reset to default account successfully"
            }
            
        except Exception as e:
            print(f"❌ Failed to reset to default account: {e}")
            return {
                "success": False,
                "error": str(e),
                "current_account": getattr(self._ezib, 'account', None)
            }
    
    def get_current_account(self) -> Optional[str]:
        """Get the currently connected account."""
        if self._ezib and hasattr(self._ezib, 'account'):
            return self._ezib.account
        return None
    
    def get_account_status(self) -> dict:
        """Get comprehensive account and polling status."""
        current_account = self.get_current_account()
        
        status = {
            "connection": {
                "is_connected": self.is_connected,
                "current_account": current_account,
                "available_accounts": list(self._ezib.accountCodes) if self._ezib and hasattr(self._ezib, 'accountCodes') else [],
                "initialized": self._ezib is not None,
                "total_connections": self._connection_count
            },
            "polling": {
                "is_polling": self._is_polling,
                "interval_minutes": self._polling_interval,
                "last_poll_time": self._last_poll_time.isoformat() if self._last_poll_time else None,
                "target_account": self._get_target_account()
            },
            "configuration": {
                "env_default_account": self._env_default_account,
                "current_target_account": self._current_target_account,
                "polling_interval": self._polling_interval
            },
            "statistics": {
                "total_connection_attempts": self._connection_count,
                "total_poll_cycles": self._poll_cycle_count,
                "average_connections_per_cycle": round(self._connection_count / max(1, self._poll_cycle_count), 1) if self._poll_cycle_count > 0 else 0
            }
        }
        
        # Add account details if connected
        if current_account and self._ezib:
            try:
                account_data = self._ezib.account if hasattr(self._ezib, 'account') else {}
                if account_data:
                    status["account_details"] = account_data
            except Exception as e:
                status["account_details_error"] = str(e)
        
        return status
    
    async def force_portfolio_refresh(self):
        """Manually trigger a portfolio refresh cycle."""
        if not self._ezib or not hasattr(self._ezib, 'accountCodes'):
            return {
                "success": False,
                "error": "EzIB connection not established"
            }
        
        target_account = self._get_target_account()
        all_accounts = list(self._ezib.accountCodes)
        
        if not target_account:
            return {
                "success": False,
                "error": "No target account available"
            }
        
        try:
            print("🔄 Manual portfolio refresh initiated...")
            
            # Quick refresh of all accounts
            for account in all_accounts:
                await self._connect_to_account(account)
                await asyncio.sleep(1)
            
            # Return to target account
            await self._connect_to_account(target_account)
            
            self._last_poll_time = datetime.now()
            
            return {
                "success": True,
                "refreshed_accounts": all_accounts,
                "current_account": target_account,
                "refresh_time": self._last_poll_time.isoformat(),
                "message": "Portfolio data refreshed successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "current_account": self.get_current_account()
            }
    
    @property
    def ezib(self) -> Any:
        """Get the ezIBAsync instance."""
        return self._ezib
    
    @property
    def is_connected(self) -> bool:
        """Check if the IB Gateway connection is active."""
        return self._ezib is not None and hasattr(self._ezib, 'connected') and self._ezib.connected
    
    async def disconnect(self):
        """Disconnect from IB Gateway and cleanup resources."""
        # Stop polling task
        if self._polling_task and not self._polling_task.done():
            self._is_polling = False
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass
            self._polling_task = None
        
        # Disconnect from IB Gateway
        if self._ezib and self.is_connected:
            self._ezib.disconnect()
        
        # Reset state
        self._ezib = None
        self._current_target_account = None
        self._last_poll_time = None
        
        print("🔌 Disconnected from IB Gateway and cleaned up resources")    
@dataclass
class EzIBAppContext:
    """Application context containing the connection manager."""
    connection_manager: EzIBConnectionManager


@asynccontextmanager
async def ezib_lifespan(_server: FastMCP) -> AsyncIterator[EzIBAppContext]:
    """
    Manages the EzIBConnectionManager lifecycle with intelligent polling and account switching.
    
    This function ensures that the IB Gateway connection is established during server startup
    and begins intelligent portfolio polling.
    
    Args:
        server: The FastMCP server instance
        
    Yields:
        EzIBAppContext: The application context containing the connection manager
    """
    # Get the singleton connection manager
    connection_manager = EzIBConnectionManager()
    
    try:
        # Force initialization during server startup
        print("🚀 Initializing EzIB Connection Manager...")
        await connection_manager.initialize()
        print(f"✅ EzIB Connection Manager ready. Connection status: {connection_manager.is_connected}")
        
        # Yield the application context
        yield EzIBAppContext(connection_manager=connection_manager)
    finally:
        # Disconnect and cleanup when server shuts down
        print("🔄 Server shutting down...")
        await connection_manager.disconnect()

mcp = FastMCP(
    "ezib-mcp",
    lifespan=ezib_lifespan,
    description="MCP server built on `ezib_async` that exposes Interactive Brokers' trading and market data functionality.",
    host=os.getenv("HOST", "0.0.0.0"),
    port=os.getenv("PORT", "8050")
)

# =============================================
# Multi-account infomation
# ---------------------------------------
# multi-account account values
# ---------------------------------------
@mcp.tool()
async def get_accounts(ctx: Context) -> dict:
    """
    Get account values for all accounts.
    
    Args:
        ctx: The context containing the ezib connection
        
    Returns:
        dict: A dict of account values for all accounts
    """
    connection_manager = ctx.request_context.lifespan_context.connection_manager
    if connection_manager.is_connected:
        return connection_manager.ezib.accounts
    else:
        raise Exception("Not connected to Interactive Brokers")

# ---------------------------------------
# multi-account portfolios
# ---------------------------------------
@mcp.tool()
async def get_portfolios(ctx: Context) -> dict:
    """
    Get portfolios for all accounts.
    
    Args:
        ctx: The context containing the ezib connection
        
    Returns:
        dict: A dict of portfolio items for all accounts
    """
    connection_manager = ctx.request_context.lifespan_context.connection_manager
    if connection_manager.is_connected:
        return connection_manager.ezib.portfolios
    else:
        raise Exception("Not connected to Interactive Brokers")

# ---------------------------------------
# multi-account positions
# ---------------------------------------
@mcp.tool()
async def get_positions(ctx: Context) -> dict:
    """
    Get positions for all accounts.
    
    Args:
        ctx: The context containing the ezib connection
        
    Returns:
        dict: A dict of position items for all accounts
    """
    connection_manager = ctx.request_context.lifespan_context.connection_manager
    if connection_manager.is_connected:
        return connection_manager.ezib.positions
    else:
        raise Exception("Not connected to Interactive Brokers")


# =============================================
# Active account infomation
# ---------------------------------------
# active account account values
# ---------------------------------------
@mcp.tool()
async def get_account(ctx: Context, account: str = "") -> dict:
    """
    Get account values for the active account.
    
    Args:
        ctx (Context): The context containing the ezib connection
        account (str, optional): The account to get values for. Defaults to "".
        
    Returns:
        dict: A dict of account values for the active account
    """
    connection_manager = ctx.request_context.lifespan_context.connection_manager
    if connection_manager.is_connected:
        ezib = connection_manager.ezib
        if account == "":
            return ezib.account
        elif account not in ezib.accountCodes:
            raise ValueError(f"Account {account} not found")

        return ezib.accounts[account]
    else:
        raise Exception("Not connected to Interactive Brokers")

# ---------------------------------------
# active account portfolio
# ---------------------------------------
@mcp.tool()
async def get_portfolio(ctx: Context, account: str = "") -> dict:
    """
    Get portfolio for the active account.
    
    Args:
        ctx (Context): The context containing the ezib connection
        account (str, optional): The account to get portfolio for. Defaults to "".
        
    Returns:
        dict: A dict of portfolio items for the active account
    """
    connection_manager = ctx.request_context.lifespan_context.connection_manager
    if connection_manager.is_connected:
        ezib = connection_manager.ezib
        if account == "":
            return ezib.portfolio
        elif account not in ezib.accountCodes:
            raise ValueError(f"Account {account} not found")

        return ezib.portfolios[account]
    else:
        raise Exception("Not connected to Interactive Brokers")

# ---------------------------------------
# active account positions
# ---------------------------------------
@mcp.tool()
async def get_position(ctx: Context, account: str = "") -> dict:
    """
    Get positions for the active account.
    
    Args:
        ctx (Context): The context containing the ezib connection
        account (str, optional): The account to get positions for. Defaults to "".
        
    Returns:
        dict: A dict of position items for the active account
    """
    connection_manager = ctx.request_context.lifespan_context.connection_manager
    if connection_manager.is_connected:
        ezib = connection_manager.ezib
        if account == "":
            return ezib.position
        elif account not in ezib.accountCodes:
            raise ValueError(f"Account {account} not found")

        return ezib.positions[account]
    else:
        raise Exception("Not connected to Interactive Brokers")


# =============================================
# Connection Management Tools
# ---------------------------------------
# Dynamic account switching and status management
# ---------------------------------------

@mcp.tool()
async def switch_active_account(ctx: Context, target_account: str) -> dict:
    """
    Dynamically switch to a different account for trading operations.
    
    This function switches the active connection to the specified account and
    updates the polling target so future polling cycles will end at this account.
    
    Args:
        ctx: The context containing the connection manager
        target_account: The account code to switch to (e.g., "DU1234567")
        
    Returns:
        dict: Switch operation result with success status and account info
        
    Example:
        switch_active_account(target_account="DU7654321")
        # Switches to account DU7654321 and makes it the polling target
    """
    connection_manager = ctx.request_context.lifespan_context.connection_manager
    return await connection_manager.switch_to_account(target_account)


@mcp.tool()
async def get_account_status(ctx: Context) -> dict:
    """
    Get comprehensive status information about connections, accounts, and polling.
    
    Provides detailed information about:
    - Current connection status and active account
    - All available accounts discovered  
    - Polling system status and configuration
    - Last polling time and target account
    - Environment configuration
    
    Args:
        ctx: The context containing the connection manager
        
    Returns:
        dict: Comprehensive status information including connection, polling, and config details
        
    Example:
        get_account_status()
        # Returns detailed status with connection info, polling status, and configuration
    """
    connection_manager = ctx.request_context.lifespan_context.connection_manager
    return connection_manager.get_account_status()


@mcp.tool()
async def reset_to_default_account(ctx: Context) -> dict:
    """
    Reset to the environment default account and clear dynamic targeting.
    
    This function switches back to the account specified in the IB_ACCOUNT environment
    variable and clears any dynamic account targeting. Future polling cycles will
    return to the environment default account.
    
    Args:
        ctx: The context containing the connection manager
        
    Returns:
        dict: Reset operation result with success status and account info
        
    Example:
        reset_to_default_account()
        # Switches back to env default account and clears dynamic targeting
    """
    connection_manager = ctx.request_context.lifespan_context.connection_manager
    return await connection_manager.reset_to_default_account()


@mcp.tool()
async def get_current_account(ctx: Context) -> dict:
    """
    Get the currently connected account identifier.
    
    Returns the account code of the account that is currently connected
    and active for operations.
    
    Args:
        ctx: The context containing the connection manager
        
    Returns:
        dict: Current account information
        
    Example:
        get_current_account()
        # Returns: {"current_account": "DU1234567", "is_connected": true}
    """
    connection_manager = ctx.request_context.lifespan_context.connection_manager
    current_account = connection_manager.get_current_account()
    
    return {
        "current_account": current_account,
        "is_connected": connection_manager.is_connected,
        "available_accounts": list(connection_manager.ezib.accountCodes) if connection_manager.ezib and hasattr(connection_manager.ezib, 'accountCodes') else []
    }


@mcp.tool()
async def force_portfolio_refresh(ctx: Context) -> dict:
    """
    Manually trigger an immediate portfolio data refresh for all accounts.
    
    This function immediately performs a portfolio refresh cycle, connecting to
    all accounts to update their portfolio data, then returns to the target account.
    Useful when you need fresh data immediately without waiting for the next
    automatic polling cycle.
    
    Args:
        ctx: The context containing the connection manager
        
    Returns:
        dict: Refresh operation result with success status and timing info
        
    Example:
        force_portfolio_refresh()
        # Immediately refreshes all account portfolio data
    """
    connection_manager = ctx.request_context.lifespan_context.connection_manager
    return await connection_manager.force_portfolio_refresh()


# Register all modules when this file is imported
# try:
register_contract_tools(mcp)
register_market_data_tools(mcp)
# except Exception as e:
#     logger.error(f"💥 Critical error during module registration: {e}")
#     logger.error(traceback.format_exc())
#     raise

async def run_http_with_cors() -> None:
    """
    Run the FastMCP HTTP server with CORS enabled so that browsers can
    successfully perform OPTIONS /mcp/ preflight requests.
    """
    import uvicorn

    # Base Streamable HTTP app from FastMCP
    app = mcp.streamable_http_app()

    # Allow configuration via environment; default to wildcard for local use
    raw_origins = os.getenv("CORS_ALLOW_ORIGINS", "*")
    if raw_origins == "*":
        allow_origins = ["*"]
    else:
        allow_origins = [
            origin.strip()
            for origin in raw_origins.split(",")
            if origin.strip()
        ]

    # Attach CORS middleware. This will handle OPTIONS /mcp/ preflight
    # and add the appropriate CORS headers to responses.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )

    config = uvicorn.Config(
        app,
        host=mcp.settings.host,
        port=mcp.settings.port,
        log_level=mcp.settings.log_level.lower(),
    )
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    """Main entry point for the EzIB MCP Server."""
    # Initialize EzIB Connection Manager during server startup
    print("🚀 Pre-initializing EzIB Connection Manager...")
    connection_manager = EzIBConnectionManager()
    
    try:
        await connection_manager.initialize()
        print("✅ EzIB Connection Manager pre-initialization completed successfully")
    except Exception as e:
        print(f"❌ Failed to initialize EzIB Connection Manager: {e}")
        print("⚠️  Server will start but ezIB functions will not work until connection is established")
    
    transport = os.getenv("TRANSPORT", "stdio")
    try:
        if transport == 'http':
            # Run the MCP server with streamable HTTP transport
            await run_http_with_cors()
        elif transport == 'stdio':
            # Run the MCP server with stdio transport
            await mcp.run_stdio_async()
        else:
            raise ValueError(f"Unsupported transport: {transport}. Use 'http' or 'stdio'.")
    finally:
        # Cleanup: disconnect when server shuts down
        print("🔄 Server shutting down...")
        await connection_manager.disconnect()
    
def cli():
    """Console script entrypoint for uvx / pip-installed usage."""
    asyncio.run(main())


if __name__ == "__main__":
    cli()
