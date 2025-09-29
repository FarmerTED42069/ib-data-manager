"""
Feature Library for Financial Analysis
Modular analysis features that can be selected and applied to CSV data
"""

from typing import Dict, List, Any, Optional, Callable
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum


class FeatureCategory(Enum):
    """Categories of analysis features"""
    TECHNICAL_INDICATORS = "Technical Indicators"
    STATISTICAL_ANALYSIS = "Statistical Analysis"
    RISK_METRICS = "Risk Metrics"
    REGIME_DETECTION = "Regime Detection"
    VOLATILITY_MODELS = "Volatility Models"
    MOMENTUM_ANALYSIS = "Momentum Analysis"
    CORRELATION_ANALYSIS = "Correlation Analysis"
    MACHINE_LEARNING = "Machine Learning"


@dataclass
class AnalysisFeature:
    """Represents a single analysis feature"""
    name: str
    category: FeatureCategory
    description: str
    code_template: str
    requirements: List[str]  # Required columns
    dependencies: List[str]  # Required libraries
    complexity: str  # "Basic", "Intermediate", "Advanced"
    
    
class FeatureLibrary:
    """Library of analysis features for financial data"""
    
    def __init__(self):
        self.features = {}
        self._initialize_features()
    
    def _initialize_features(self):
        """Initialize all available features"""
        
        # Technical Indicators
        self.add_feature(AnalysisFeature(
            name="Moving Averages",
            category=FeatureCategory.TECHNICAL_INDICATORS,
            description="Simple and Exponential Moving Averages (SMA, EMA)",
            requirements=["close"],
            dependencies=["pandas", "numpy"],
            complexity="Basic",
            code_template="""
# Moving Averages Analysis
def calculate_moving_averages(df):
    # Simple Moving Averages
    df['SMA_10'] = df['close'].rolling(window=10).mean()
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['SMA_50'] = df['close'].rolling(window=50).mean()
    df['SMA_200'] = df['close'].rolling(window=200).mean()
    
    # Exponential Moving Averages
    df['EMA_12'] = df['close'].ewm(span=12).mean()
    df['EMA_26'] = df['close'].ewm(span=26).mean()
    
    # Moving Average Crossover Signals
    df['MA_Signal'] = np.where(df['SMA_20'] > df['SMA_50'], 1, -1)
    
    return df

# Apply moving averages
df = calculate_moving_averages(df)

# Plot moving averages
plt.figure(figsize=(14, 8))
plt.plot(df.index, df['close'], label='Close Price', linewidth=1)
plt.plot(df.index, df['SMA_20'], label='SMA 20', alpha=0.7)
plt.plot(df.index, df['SMA_50'], label='SMA 50', alpha=0.7)
plt.title(f'{symbol} - Moving Averages')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

print("Moving Averages calculated and plotted!")
"""
        ))
        
        self.add_feature(AnalysisFeature(
            name="RSI Indicator",
            category=FeatureCategory.TECHNICAL_INDICATORS,
            description="Relative Strength Index with overbought/oversold levels",
            requirements=["close"],
            dependencies=["pandas", "numpy"],
            complexity="Basic",
            code_template="""
# RSI (Relative Strength Index) Analysis
def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Calculate RSI
df['RSI'] = calculate_rsi(df['close'])
df['RSI_Signal'] = np.where(df['RSI'] > 70, -1, np.where(df['RSI'] < 30, 1, 0))

# Plot RSI
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

# Price chart
ax1.plot(df.index, df['close'], label='Close Price')
ax1.set_title(f'{symbol} - Price and RSI Analysis')
ax1.legend()
ax1.grid(True, alpha=0.3)

# RSI chart
ax2.plot(df.index, df['RSI'], label='RSI', color='orange')
ax2.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='Overbought (70)')
ax2.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='Oversold (30)')
ax2.fill_between(df.index, 70, 100, alpha=0.2, color='red')
ax2.fill_between(df.index, 0, 30, alpha=0.2, color='green')
ax2.set_ylabel('RSI')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print(f"Current RSI: {df['RSI'].iloc[-1]:.2f}")
"""
        ))
        
        # Statistical Analysis
        self.add_feature(AnalysisFeature(
            name="Returns Analysis",
            category=FeatureCategory.STATISTICAL_ANALYSIS,
            description="Comprehensive returns analysis with distributions",
            requirements=["close"],
            dependencies=["pandas", "numpy", "scipy"],
            complexity="Intermediate",
            code_template="""
# Returns Analysis
from scipy import stats

def analyze_returns(df):
    # Calculate returns
    df['returns'] = df['close'].pct_change()
    df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
    df['cumulative_returns'] = (1 + df['returns']).cumprod() - 1
    
    returns = df['returns'].dropna()
    
    # Statistics
    stats_dict = {
        'Mean Return': returns.mean(),
        'Std Deviation': returns.std(),
        'Skewness': stats.skew(returns),
        'Kurtosis': stats.kurtosis(returns),
        'Sharpe Ratio': returns.mean() / returns.std() * np.sqrt(252),
        'Max Drawdown': (df['cumulative_returns'] - df['cumulative_returns'].cummax()).min()
    }
    
    return stats_dict

# Analyze returns
returns_stats = analyze_returns(df)

# Display statistics
print("=== Returns Analysis ===")
for key, value in returns_stats.items():
    print(f"{key}: {value:.4f}")

# Plot returns distribution
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Returns over time
axes[0, 0].plot(df.index, df['returns'])
axes[0, 0].set_title('Daily Returns')
axes[0, 0].grid(True, alpha=0.3)

# Cumulative returns
axes[0, 1].plot(df.index, df['cumulative_returns'] * 100)
axes[0, 1].set_title('Cumulative Returns (%)')
axes[0, 1].grid(True, alpha=0.3)

# Returns histogram
axes[1, 0].hist(df['returns'].dropna(), bins=50, alpha=0.7, density=True)
axes[1, 0].set_title('Returns Distribution')
axes[1, 0].grid(True, alpha=0.3)

# Q-Q plot
stats.probplot(df['returns'].dropna(), dist="norm", plot=axes[1, 1])
axes[1, 1].set_title('Q-Q Plot (Normal Distribution)')

plt.tight_layout()
plt.show()
"""
        ))
        
        # Risk Metrics
        self.add_feature(AnalysisFeature(
            name="Value at Risk (VaR)",
            category=FeatureCategory.RISK_METRICS,
            description="Historical and Parametric VaR calculations",
            requirements=["close"],
            dependencies=["pandas", "numpy", "scipy"],
            complexity="Advanced",
            code_template="""
# Value at Risk (VaR) Analysis
from scipy import stats

def calculate_var(returns, confidence_levels=[0.95, 0.99]):
    var_results = {}
    
    for confidence in confidence_levels:
        # Historical VaR
        var_hist = np.percentile(returns, (1 - confidence) * 100)
        
        # Parametric VaR (assuming normal distribution)
        mean_return = returns.mean()
        std_return = returns.std()
        var_param = stats.norm.ppf(1 - confidence, mean_return, std_return)
        
        var_results[f'Historical_VaR_{int(confidence*100)}'] = var_hist
        var_results[f'Parametric_VaR_{int(confidence*100)}'] = var_param
    
    return var_results

# Calculate VaR
returns = df['close'].pct_change().dropna()
var_metrics = calculate_var(returns)

print("=== Value at Risk Analysis ===")
for metric, value in var_metrics.items():
    print(f"{metric}: {value:.4f} ({value*100:.2f}%)")

# Expected Shortfall (Conditional VaR)
var_95 = var_metrics['Historical_VaR_95']
expected_shortfall = returns[returns <= var_95].mean()
print(f"Expected Shortfall (95%): {expected_shortfall:.4f} ({expected_shortfall*100:.2f}%)")

# Plot VaR visualization
plt.figure(figsize=(12, 6))
plt.hist(returns, bins=50, alpha=0.7, density=True, label='Returns Distribution')
plt.axvline(var_metrics['Historical_VaR_95'], color='red', linestyle='--', 
           label=f"VaR 95%: {var_metrics['Historical_VaR_95']:.4f}")
plt.axvline(var_metrics['Historical_VaR_99'], color='darkred', linestyle='--', 
           label=f"VaR 99%: {var_metrics['Historical_VaR_99']:.4f}")
plt.xlabel('Returns')
plt.ylabel('Density')
plt.title(f'{symbol} - Value at Risk Analysis')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
"""
        ))
        
        # Volatility Models
        self.add_feature(AnalysisFeature(
            name="GARCH Volatility Model",
            category=FeatureCategory.VOLATILITY_MODELS,
            description="GARCH(1,1) volatility modeling and forecasting",
            requirements=["close"],
            dependencies=["pandas", "numpy", "arch"],
            complexity="Advanced",
            code_template="""
# GARCH Volatility Modeling
try:
    from arch import arch_model
    
    # Prepare returns data
    returns = df['close'].pct_change().dropna() * 100  # Convert to percentage
    
    # Fit GARCH(1,1) model
    garch_model = arch_model(returns, vol='Garch', p=1, q=1)
    garch_fitted = garch_model.fit(disp='off')
    
    # Extract conditional volatility
    conditional_volatility = garch_fitted.conditional_volatility
    
    # Add to dataframe
    df.loc[conditional_volatility.index, 'GARCH_Volatility'] = conditional_volatility / 100
    
    # Print model summary
    print("=== GARCH Model Results ===")
    print(garch_fitted.summary())
    
    # Plot volatility
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    
    # Price chart
    ax1.plot(df.index, df['close'])
    ax1.set_title(f'{symbol} - Price and GARCH Volatility')
    ax1.set_ylabel('Price')
    ax1.grid(True, alpha=0.3)
    
    # Volatility chart
    ax2.plot(conditional_volatility.index, conditional_volatility)
    ax2.set_title('GARCH Conditional Volatility')
    ax2.set_ylabel('Volatility (%)')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Volatility forecasting
    forecasts = garch_fitted.forecast(horizon=5)
    print("\\n=== 5-Day Volatility Forecast ===")
    print(forecasts.variance.iloc[-1])
    
except ImportError:
    print("GARCH analysis requires 'arch' package. Install with: pip install arch")
except Exception as e:
    print(f"GARCH analysis failed: {e}")
"""
        ))
        
        # Machine Learning
        self.add_feature(AnalysisFeature(
            name="Price Prediction ML",
            category=FeatureCategory.MACHINE_LEARNING,
            description="Machine learning models for price prediction",
            requirements=["close", "volume"],
            dependencies=["pandas", "numpy", "sklearn"],
            complexity="Advanced",
            code_template="""
# Machine Learning Price Prediction
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

def create_features(df):
    # Technical features
    df['SMA_5'] = df['close'].rolling(5).mean()
    df['SMA_20'] = df['close'].rolling(20).mean()
    df['RSI'] = calculate_rsi(df['close'])  # Use RSI function from above
    df['Returns'] = df['close'].pct_change()
    df['Volatility'] = df['Returns'].rolling(20).std()
    
    # Lag features
    for lag in [1, 2, 3, 5]:
        df[f'Close_Lag_{lag}'] = df['close'].shift(lag)
        df[f'Volume_Lag_{lag}'] = df['volume'].shift(lag)
    
    # Target: next day's return
    df['Target'] = df['close'].shift(-1) / df['close'] - 1
    
    return df

# Create features
df_ml = create_features(df.copy())

# Select features for modeling
feature_columns = [col for col in df_ml.columns if 'Lag' in col or col in ['SMA_5', 'SMA_20', 'RSI', 'Volatility']]
df_ml = df_ml.dropna()

X = df_ml[feature_columns]
y = df_ml['Target']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Random Forest model
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train_scaled, y_train)

# Make predictions
y_pred = rf_model.predict(X_test_scaled)

# Evaluate model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("=== ML Model Performance ===")
print(f"Mean Squared Error: {mse:.6f}")
print(f"R² Score: {r2:.4f}")

# Feature importance
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\\n=== Feature Importance ===")
print(feature_importance.head(10))

# Plot predictions vs actual
plt.figure(figsize=(12, 6))
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel('Actual Returns')
plt.ylabel('Predicted Returns')
plt.title(f'{symbol} - ML Predictions vs Actual Returns')
plt.grid(True, alpha=0.3)
plt.show()
"""
        ))
    
    def add_feature(self, feature: AnalysisFeature):
        """Add a feature to the library"""
        self.features[feature.name] = feature
    
    def get_features_by_category(self, category: FeatureCategory) -> List[AnalysisFeature]:
        """Get all features in a specific category"""
        return [f for f in self.features.values() if f.category == category]
    
    def get_feature(self, name: str) -> Optional[AnalysisFeature]:
        """Get a specific feature by name"""
        return self.features.get(name)
    
    def list_all_features(self) -> Dict[str, List[str]]:
        """List all features grouped by category"""
        result = {}
        for category in FeatureCategory:
            features = self.get_features_by_category(category)
            result[category.value] = [f.name for f in features]
        return result
    
    def generate_selected_analysis(self, selected_features: List[str]) -> str:
        """Generate code for selected features"""
        code_blocks = []
        
        # Add imports based on selected features
        all_dependencies = set()
        for feature_name in selected_features:
            feature = self.get_feature(feature_name)
            if feature:
                all_dependencies.update(feature.dependencies)
        
        # Generate imports
        import_block = "# Required imports for selected features\\n"
        for dep in sorted(all_dependencies):
            if dep == "pandas":
                import_block += "import pandas as pd\\n"
            elif dep == "numpy":
                import_block += "import numpy as np\\n"
            elif dep == "matplotlib":
                import_block += "import matplotlib.pyplot as plt\\n"
            elif dep == "seaborn":
                import_block += "import seaborn as sns\\n"
            else:
                import_block += f"import {dep}\\n"
        
        code_blocks.append(import_block)
        
        # Add feature code blocks
        for feature_name in selected_features:
            feature = self.get_feature(feature_name)
            if feature:
                code_blocks.append(f"\\n# {feature.name} - {feature.description}")
                code_blocks.append(feature.code_template)
        
        return "\\n".join(code_blocks)


# Global feature library instance
FEATURE_LIBRARY = FeatureLibrary()
