from typing import Optional
from pydantic import BaseModel, validator, AnyUrl, parse_obj_as, root_validator, constr

from ..api_tests import PerformanceApiTest
from ..api_reports import APIReport


class ThresholdPD(BaseModel):
    project_id: int
    test: str
    environment: str
    scope: str
    target: str
    aggregation: str
    comparison: str
    value: float

    @validator('test')
    def validate_test_exists(cls, value: str, values: dict):
        assert PerformanceApiTest.query.filter(
            PerformanceApiTest.project_id == values['project_id'],
            PerformanceApiTest.name == value
        ).first(), f'Test with name {value} does not exist'
        return value

    @validator('environment')
    def validate_env_exists(cls, value: str, values: dict):
        assert APIReport.query.filter(
            APIReport.environment == value,
            APIReport.project_id == values['project_id']
        ).first(), 'Result with this environment does not exist'
        return value

    @validator('scope')
    def validate_scope_exists(cls, value: str, values: dict):
        if value in ['all', 'every']:
            return value

        assert APIReport.query.filter(
            APIReport.project_id == values['project_id'],
            APIReport.requests.contains(value)
        ).first(), 'Such scope does not exist'
        return value

    @validator('target')
    def validate_target(cls, value: str):
        assert value in {'throughput', 'error_rate', 'response_time'}, f'Target {value} is not supported'
        return value

    @validator('aggregation')
    def validate_aggregation(cls, value: str):
        assert value in {'max', 'min', 'avg', 'pct95', 'pct50'}, f'Aggregation {value} is not supported'
        return value

    @validator('comparison')
    def validate_comparison(cls, value: str):
        assert value in {'gte', 'lte', 'lt', 'gt', 'eq'}, f'Comparison {value} is not supported'
        return value
