from typing import Any, List, Dict, Optional


def aggregate_sum(results: List[Any]) -> Any:
    """Sum aggregator"""
    return sum(results)


def aggregate_list(results: List[Any]) -> List[Any]:
    """List aggregator (flatten list)"""
    return [
        item
        for sublist in results
        for item in (sublist if isinstance(sublist, list) else [sublist])
    ]


def aggregate_dict(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Dictionary aggregator (merge dictionaries)"""
    aggregated: Dict[str, Any] = {}
    for result in results:
        if isinstance(result, dict):
            aggregated.update(result)
    return aggregated


def aggregate_first_non_none(results: List[Any]) -> Optional[Any]:
    """First non-None value aggregator"""
    for result in results:
        if result is not None:
            return result
    return None


def aggregate_all(results: List[Any]) -> List[Any]:
    """Aggregator that returns all results"""
    return results
