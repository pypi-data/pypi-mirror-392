
from typing import Dict, Any, List
from decimal import Decimal

class LowStockChecker:
    THRESHOLDS = {
        'kg': Decimal('10.0'),
        'g': Decimal('500.0'),
        'liter': Decimal('20.0'),
        'ml': Decimal('1000.0'),
        'unit': Decimal('5.0'),
        'box': Decimal('3.0'),
        'pack': Decimal('10.0'),
    }

    @classmethod
    def is_low(cls, item: Dict[str, Any]) -> bool:
        qty = Decimal(str(item.get('Quantity', 0)))
        unit = item.get('Unit', '').strip().lower()
        threshold = cls.THRESHOLDS.get(unit, Decimal('5.0'))
        return qty < threshold
