import subprocess
import json
import sys
import os
import threading
from typing import Callable, Optional, Dict, Any, List
from pathlib import Path


class Subscription:
    """
    Subscribe to Politics and War real-time events.
    
    Example:
        >>> from pnw_subscriptions import Subscription
        >>> 
        >>> def handle_event(event):
        ...     print(f"Color changed: {event}")
        >>> 
        >>> sub = Subscription(api_key="your_api_key", subscription_type="nation_colors")
        >>> sub.start(callback=handle_event)
    """
    
    SUBSCRIPTION_TYPES = {
        "nations": "nation_listener.js",
        "trades": "trade_listener.js",
        "wars": "war_listener.js",
        "alliances": "alliance_listener.js",
        "cities": "city_listener.js",
        "banks": "bank_listener.js",
        "treaties": "treaty_listener.js",
        "bounties": "bounty_listener.js",
        "baseball_games": "baseball_listener.js",
        "treasure_trades": "treasure_listener.js",
        "embargoes": "embargo_listener.js",
        "attacks": "attack_listener.js",
    }
    
    def __init__(self, api_key: str, subscription_type: str, pusher_key: str = "a22734a47847a64386c8"):
        """
        Initialize a subscription.
        
        Args:
            api_key: Your Politics and War API key
            subscription_type: Type of subscription ("nation_colors" or "trades")
            pusher_key: Pusher key (default provided)
        
        Raises:
            ValueError: If subscription_type is not valid
        """
        if subscription_type not in self.SUBSCRIPTION_TYPES:
            raise ValueError(
                f"Invalid subscription_type. Must be one of: {list(self.SUBSCRIPTION_TYPES.keys())}"
            )
        
        self.api_key = api_key
        self.pusher_key = pusher_key
        self.subscription_type = subscription_type
        self._process: Optional[subprocess.Popen] = None
        self._script_path = Path(__file__).parent / "scripts" / self.SUBSCRIPTION_TYPES[subscription_type]
    
    def start(self, callback: Callable[[Dict[str, Any]], None], blocking: bool = True):
        """
        Start the subscription and process events with the callback.
        
        Args:
            callback: Function to call for each event. Receives a dict with event data.
            blocking: If True, blocks until stopped. If False, runs in background thread.
        
        Example:
            >>> def my_handler(event):
            ...     if event["type"] == "COLOR_CHANGE":
            ...         print(f"{event['nation_name']} changed from {event['old_color']} to {event['new_color']}")
            >>> 
            >>> sub.start(callback=my_handler)
        """
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("Node.js is not installed or not in PATH")
        
        if not self._script_path.exists():
            raise FileNotFoundError(f"Script not found: {self._script_path}")
        
        env = os.environ.copy()
        env["PNW_API_KEY"] = self.api_key
        env["PNW_PUSHER_KEY"] = self.pusher_key
        
        self._process = subprocess.Popen(
            ["node", str(self._script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1,
        )
        
        print(f"[Python] Started {self.subscription_type} subscription", file=sys.stderr)
        
        if blocking:
            self._process_events(callback)
        else:
            thread = threading.Thread(target=self._process_events, args=(callback,), daemon=True)
            thread.start()
    
    def _process_events(self, callback: Callable[[Dict[str, Any]], None]):
        """Internal method to process events from the Node.js process."""
        try:
            for line in self._process.stdout:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    event = json.loads(line)
                    callback(event)
                except json.JSONDecodeError:
                    print(f"[Python] Warning: Could not parse JSON: {line}", file=sys.stderr)
        except KeyboardInterrupt:
            print("\n[Python] Shutting down...", file=sys.stderr)
            self.stop()
        except Exception as e:
            print(f"[Python] Error: {e}", file=sys.stderr)
            self.stop()
            raise
    
    def stop(self):
        """Stop the subscription."""
        if self._process:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None
            print("[Python] Subscription stopped", file=sys.stderr)
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.stop()
        return False


class MultiSubscription:
    """
    Manage multiple subscriptions simultaneously.
    
    Example:
        >>> from pnw_subscriptions import MultiSubscription
        >>> 
        >>> def handle_colors(event):
        ...     print(f"Color: {event}")
        >>> 
        >>> def handle_trades(event):
        ...     print(f"Trade: {event}")
        >>> 
        >>> multi = MultiSubscription(api_key="your_api_key")
        >>> multi.add_subscription("nation_colors", handle_colors)
        >>> multi.add_subscription("trades", handle_trades)
        >>> multi.start_all()
    """
    
    def __init__(self, api_key: str, pusher_key: str = "a22734a47847a64386c8"):
        """
        Initialize a multi-subscription manager.
        
        Args:
            api_key: Your Politics and War API key
            pusher_key: Pusher key (default provided)
        """
        self.api_key = api_key
        self.pusher_key = pusher_key
        self.subscriptions: List[Subscription] = []
        self._threads: List[threading.Thread] = []
    
    def add_subscription(
        self, 
        subscription_type: str, 
        callback: Callable[[Dict[str, Any]], None]
    ) -> Subscription:
        """
        Add a subscription to the manager.
        
        Args:
            subscription_type: Type of subscription ("nation_colors" or "trades")
            callback: Function to call for each event
        
        Returns:
            The created Subscription instance
        """
        sub = Subscription(
            api_key=self.api_key,
            subscription_type=subscription_type,
            pusher_key=self.pusher_key
        )
        self.subscriptions.append((sub, callback))
        return sub
    
    def start_all(self):
        """
        Start all subscriptions. Blocks until interrupted.
        """
        if not self.subscriptions:
            raise ValueError("No subscriptions added. Use add_subscription() first.")
        
        print(f"[Python] Starting {len(self.subscriptions)} subscription(s)...", file=sys.stderr)
        
        for sub, callback in self.subscriptions[:-1]:
            sub.start(callback=callback, blocking=False)
        
        try:
            last_sub, last_callback = self.subscriptions[-1]
            last_sub.start(callback=last_callback, blocking=True)
        except KeyboardInterrupt:
            print("\n[Python] Shutting down all subscriptions...", file=sys.stderr)
            self.stop_all()
    
    def stop_all(self):
        """Stop all subscriptions."""
        for sub, _ in self.subscriptions:
            sub.stop()
        print("[Python] All subscriptions stopped", file=sys.stderr)
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.stop_all()
        return False