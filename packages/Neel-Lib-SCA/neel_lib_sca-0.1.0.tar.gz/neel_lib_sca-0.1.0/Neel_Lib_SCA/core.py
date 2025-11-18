"""
Simple Core Functions for Supply Chain Analytics
Easy-to-understand calculations for student projects
"""

import math
from typing import List, Dict, Any

def calculate_eoq(annual_demand: float, ordering_cost: float, holding_cost: float) -> float:
    """
    Calculate Economic Order Quantity (EOQ)
    
    Formula: EOQ = √(2 × Annual Demand × Order Cost ÷ Holding Cost)
    
    Args:
        annual_demand: Total units needed per year
        ordering_cost: Cost to place one order ($)
        holding_cost: Cost to store one unit for one year ($)
    
    Returns:
        Optimal order quantity (units)
    
    Example:
        >>> calculate_eoq(1000, 50, 2)
        224
    """
    if holding_cost <= 0:
        return 100  # Safe default
    
    eoq = math.sqrt((2 * annual_demand * ordering_cost) / holding_cost)
    return round(eoq)

def calculate_reorder_point(daily_demand: float, lead_time_days: int, 
                          safety_stock: float = 0) -> float:
    """
    Calculate when to reorder inventory
    
    Formula: Reorder Point = (Daily Demand × Lead Time) + Safety Stock
    
    Args:
        daily_demand: Average units sold per day
        lead_time_days: Days for supplier to deliver
        safety_stock: Extra buffer stock (units)
    
    Returns:
        Reorder point (units)
    
    Example:
        >>> calculate_reorder_point(10, 7, 15)
        85
    """
    reorder_point = (daily_demand * lead_time_days) + safety_stock
    return max(0, round(reorder_point))

def abc_analysis(products: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Categorize products into A, B, C classes based on value
    
    A = Top 80% of total value
    B = Next 15% of total value  
    C = Bottom 5% of total value
    
    Args:
        products: List of products with 'name' and 'value' keys
    
    Returns:
        Dictionary with A, B, C categories
    
    Example:
        >>> products = [{'name': 'Laptop', 'value': 1000}, {'name': 'Mouse', 'value': 20}]
        >>> abc_analysis(products)
        {'A': [{'name': 'Laptop', 'value': 1000}], 'B': [], 'C': [{'name': 'Mouse', 'value': 20}]}
    """
    if not products:
        return {'A': [], 'B': [], 'C': []}
    
    # Sort products by value (highest first)
    sorted_products = sorted(products, key=lambda x: x['value'], reverse=True)
    
    # Calculate total value
    total_value = sum(item['value'] for item in sorted_products)
    
    # Categorize products
    categories = {'A': [], 'B': [], 'C': []}
    running_total = 0
    
    for product in sorted_products:
        running_total += product['value']
        percentage = (running_total / total_value) * 100
        
        if percentage <= 80:
            categories['A'].append(product)
        elif percentage <= 95:
            categories['B'].append(product)
        else:
            categories['C'].append(product)
    
    return categories

def moving_average_forecast(data: List[float], periods: int = 3) -> List[float]:
    """
    Simple demand forecasting using moving average
    
    Formula: Forecast = Average of last N periods
    
    Args:
        data: Historical demand data
        periods: Number of periods to average
    
    Returns:
        Forecasted values
    
    Example:
        >>> moving_average_forecast([100, 110, 120], 2)
        [105, 115]
    """
    if len(data) < periods:
        return []
    
    forecasts = []
    for i in range(len(data) - periods + 1):
        average = sum(data[i:i + periods]) / periods
        forecasts.append(round(average, 1))
    
    return forecasts

def calculate_turnover(cogs: float, avg_inventory: float) -> float:
    """
    Calculate inventory turnover ratio
    
    Formula: Turnover = Cost of Goods Sold ÷ Average Inventory
    
    Args:
        cogs: Cost of goods sold ($)
        avg_inventory: Average inventory value ($)
    
    Returns:
        Turnover ratio (how many times inventory sells per year)
    
    Example:
        >>> calculate_turnover(50000, 10000)
        5.0
    """
    if avg_inventory <= 0:
        return 0
    
    return round(cogs / avg_inventory, 2)
