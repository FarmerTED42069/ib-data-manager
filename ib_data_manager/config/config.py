"""
Configuration settings for IB Data Manager
"""

import os
import json

class Config:
    """Configuration manager"""
    
    DEFAULT_CONFIG = {
        'ib_gateway': {
            'host': '127.0.0.1',
            'port': 4002,  # 4002 for paper trading
            'client_id': 1
        },
        'database': {
            'path': 'ib_data.db',
            'backup_enabled': True,
            'backup_interval_days': 7,
            # Performance settings
            'batch_size': 1000,  # Records per batch insert
            'connection_pool_size': 5,  # Number of pooled connections
            'connection_timeout': 30,  # Connection timeout in seconds
            'pragma_settings': {
                'journal_mode': 'WAL',  # Write-Ahead Logging for better concurrency
                'synchronous': 'NORMAL',  # Balance between safety and speed
                'cache_size': -64000,  # 64MB cache (negative = KB)
                'temp_store': 'MEMORY',  # Store temp tables in memory
                'mmap_size': 268435456  # 256MB memory-mapped I/O
            }
        },
        'logging': {
            'level': 'INFO',
            'file': 'ib_data_manager.log',
            'max_file_size_mb': 10,
            'backup_count': 5
        },
        'data_settings': {
            'default_duration': '1 D',
            'default_bar_size': '1 min',
            'default_exchange': 'SMART',
            'default_currency': 'USD',
            'max_concurrent_requests': 10,  # Increased from 3 for better throughput
            # Performance tuning
            'request_timeout': 30,  # API request timeout in seconds
            'retry_attempts': 3,  # Number of retry attempts for failed requests
            'retry_delay': 1.0,  # Delay between retries in seconds
            'rate_limit_delay': 0.1,  # Delay between API calls to avoid throttling
            # Memory management
            'max_memory_usage_mb': 512,  # Maximum memory usage before cleanup
            'data_retention_days': 365,  # Days to keep historical data
            'cleanup_interval_hours': 24,  # Hours between automatic cleanup
            # Real-time data settings
            'realtime_buffer_size': 1000,  # Buffer size for real-time data
            'market_depth_levels': 10,  # Number of market depth levels to track
            'quote_throttle_ms': 100  # Minimum milliseconds between quote updates
        },
        'gui_settings': {
            'window_size': '800x600',
            'theme': 'default',
            'auto_connect': False,
            'save_window_position': True
        },
        'performance': {
            # Monitoring settings
            'enable_metrics': True,  # Enable performance metrics collection
            'metrics_interval': 60,  # Seconds between metric snapshots
            'log_slow_queries': True,  # Log database queries slower than threshold
            'slow_query_threshold_ms': 1000,  # Milliseconds threshold for slow queries
            'memory_monitoring': True,  # Enable memory usage monitoring
            'memory_alert_threshold_mb': 1024,  # Alert when memory usage exceeds this
            # Threading settings
            'max_worker_threads': 4,  # Maximum number of worker threads
            'thread_pool_timeout': 30,  # Thread pool timeout in seconds
            'async_queue_size': 1000,  # Maximum size of async operation queue
            # Connection health
            'connection_health_check': True,  # Enable connection health monitoring
            'health_check_interval': 300,  # Seconds between health checks
            'reconnect_attempts': 5,  # Number of reconnection attempts
            'reconnect_delay': 5  # Seconds between reconnection attempts
        }
    }
    
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_configs(self.DEFAULT_CONFIG, config)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
            
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def _merge_configs(self, default, custom):
        """Merge custom config with defaults"""
        merged = default.copy()
        for key, value in custom.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged
        
    def get(self, section, key, default=None):
        """Get configuration value"""
        try:
            return self.config[section][key]
        except KeyError:
            return default
            
    def set(self, section, key, value):
        """Set configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()
        
    def get_all(self):
        """Get all configuration"""
        return self.config.copy()
        
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
        
    # Performance-specific helper methods
    def get_database_batch_size(self):
        """Get database batch size for bulk operations"""
        return self.get('database', 'batch_size', 1000)
        
    def get_connection_pool_size(self):
        """Get database connection pool size"""
        return self.get('database', 'connection_pool_size', 5)
        
    def get_max_concurrent_requests(self):
        """Get maximum concurrent API requests"""
        return self.get('data_settings', 'max_concurrent_requests', 10)
        
    def get_memory_limit_mb(self):
        """Get memory usage limit in MB"""
        return self.get('data_settings', 'max_memory_usage_mb', 512)
        
    def get_data_retention_days(self):
        """Get data retention period in days"""
        return self.get('data_settings', 'data_retention_days', 365)
        
    def get_pragma_settings(self):
        """Get SQLite PRAGMA settings for performance"""
        return self.get('database', 'pragma_settings', {})
        
    def is_performance_monitoring_enabled(self):
        """Check if performance monitoring is enabled"""
        return self.get('performance', 'enable_metrics', True)
        
    def get_slow_query_threshold_ms(self):
        """Get slow query threshold in milliseconds"""
        return self.get('performance', 'slow_query_threshold_ms', 1000)

# Create a global config instance
config = Config()

# Example usage
if __name__ == "__main__":
    # Load config
    cfg = Config()
    
    # Get values
    host = cfg.get('ib_gateway', 'host')
    port = cfg.get('ib_gateway', 'port')
    print(f"IB Gateway: {host}:{port}")
    
    # Set values
    cfg.set('ib_gateway', 'port', 4002)  # Switch to paper trading
    
    # Get all config
    all_config = cfg.get_all()
    print(json.dumps(all_config, indent=2))
    
    # Reset to defaults
    # cfg.reset_to_defaults()
