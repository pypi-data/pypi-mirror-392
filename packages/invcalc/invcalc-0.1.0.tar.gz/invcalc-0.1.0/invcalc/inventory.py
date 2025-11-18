from decimal import Decimal


class InventoryCalculator:
    def __init__(self):
        self.reorder_points = {}
        self.lead_times = {}

    @staticmethod
    def calculate_eoq(demand, ordering_cost, holding_cost):
        """
        Calculate Economic Order Quantity (EOQ)
        EOQ = √(2DS/H)
        Where:
        D = Annual demand
        S = Ordering cost per order
        H = Holding cost per unit per year
        """
        if demand <= 0 or ordering_cost <= 0 or holding_cost <= 0:
            raise ValueError("All parameters must be positive")

        result = (Decimal(2) * demand * ordering_cost / holding_cost).sqrt()
        return result

    @staticmethod
    def calculate_reorder_point(demand, lead_time, safety_stock=0):
        """
        Calculate reorder point
        ROP = (Demand × Lead Time) + Safety Stock
        """
        if demand < 0 or lead_time < 0 or safety_stock < 0:
            raise ValueError("Parameters cannot be negative")

        return (demand * lead_time) + safety_stock

    @staticmethod
    def abc_analysis(items):
        """
        Perform ABC analysis on inventory items
        Returns categorized items (A, B, C) based on value
        """
        if not items:
            return {}

        # Calculate total value
        total_value = sum(item['value'] for item in items)

        # Sort items by value in descending order
        sorted_items = sorted(items, key=lambda x: x['value'], reverse=True)

        categorized = {'A': [], 'B': [], 'C': []}
        cumulative_value = 0

        for item in sorted_items:
            cumulative_value += item['value']
            percentage = (cumulative_value / total_value) * 100

            if percentage <= 80:
                category = 'A'
            elif percentage <= 95:
                category = 'B'
            else:
                category = 'C'

            categorized[category].append({'name': item['name'], 'value': item['value'], 'percentage': (item['value'] / total_value) * 100})

        return categorized

    @staticmethod
    def stock_turnover_ratio(cost_of_goods_sold, average_inventory):
        """
        Calculate inventory turnover ratio
        Turnover = Cost of Goods Sold / Average Inventory
        """
        if average_inventory == 0:
            return float('inf')
        return cost_of_goods_sold / average_inventory

    @staticmethod
    def days_in_inventory(turnover_ratio):
        """
        Calculate days in inventory
        Days = 365 / Turnover Ratio
        """
        if turnover_ratio == 0:
            return float('inf')
        return 365 / turnover_ratio
