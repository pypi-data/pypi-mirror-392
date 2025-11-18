"""
Neel_Lib_SCA - Supply Chain Analytics Library
Simple and practical supply chain calculations for inventory management
"""

from .core import (
calculate_eoq,
calculate_reorder_point,
abc_analysis,
moving_average_forecast,
calculate_turnover
)

version = "1.0.0"
author = "Neel Sawant"
email = "neel.sawant09@gmail.com"

all = [
"calculate_eoq",
"calculate_reorder_point",
"abc_analysis",
"moving_average_forecast",
"calculate_turnover"
]