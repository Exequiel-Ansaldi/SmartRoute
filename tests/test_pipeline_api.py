from inspect import signature

from main import run_pipeline, solve_routes_for_algorithm


def test_pipeline_api_does_not_expose_capacity_parameter():
    run_signature = signature(run_pipeline)
    solve_signature = signature(solve_routes_for_algorithm)

    assert "capacity" not in run_signature.parameters
    assert "capacity" not in solve_signature.parameters
