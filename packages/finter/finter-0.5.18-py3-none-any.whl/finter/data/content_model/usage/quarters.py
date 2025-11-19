"""
KRX Financial Loader - Quarters parameter usage documentation.
"""

QUARTERS_USAGE_TEXT = """
╔════════════════════════════════════════════════════════════════════════════╗
║                     Quarters Parameter Usage Guide                         ║
╚════════════════════════════════════════════════════════════════════════════╝

The 'quarters' parameter enables rolling quarterly calculations for financial data.

📖 Basic Usage:
   cf.get_df(item_name, quarters=(n_quarters, operation))

⚠️  Important: quarters must be a tuple with (quarters, operation)

📋 Supported Operations:

   1. Mean - Average of n quarters
      Example: quarters=(4, 'mean')
      → Returns: 4-quarter rolling average

   2. Sum - Sum of n quarters
      Example: quarters=(4, 'sum')
      → Returns: 4-quarter rolling sum (TTM for revenue, etc.)

   3. Diff - Difference between current and n quarters ago
      Example: quarters=(4, 'diff')
      → Returns: YoY change (current Q - same Q last year)

   4. Last - Value from n quarters ago
      Example: quarters=(4, 'last')
      → Returns: Same quarter value from 1 year ago
      Example: quarters=(0, 'last')
      → Returns: Current quarter value (same as original data)

💡 Examples:

   # 4-quarter rolling average
   df = cf.get_df('total_assets', quarters=(4, 'mean'))

   # 4-quarter sum (Trailing Twelve Months)
   df = cf.get_df('revenue', quarters=(4, 'sum'))

   # Year-over-Year change
   df = cf.get_df('net_income', quarters=(4, 'diff'))

   # Previous year same quarter
   df = cf.get_df('eps', quarters=(4, 'last'))

   # 1-quarter ago (previous quarter)
   df = cf.get_df('total_assets', quarters=(1, 'last'))

   # Current quarter (quarters=0 with 'last')
   df = cf.get_df('total_assets', quarters=(0, 'last'))

⚠️  Notes:
   - Data is automatically loaded from 2 years before start date for accuracy
   - Forward fill is applied with a limit of 500 days
   - Cannot be used together with 'preprocess_type' parameter

📌 Additional Parameters:
   - fill_nan (default: True)
     * True: Prevents lookahead bias by not showing last day data
     * False: Shows all data including last day
     Example: df = cf.get_df('revenue', quarters=(4, 'sum'), fill_nan=False)
"""
