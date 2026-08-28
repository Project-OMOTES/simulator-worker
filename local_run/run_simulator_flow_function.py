from pathlib import Path

from simulator_worker.prefect_flow import SimulatorFlowResult, simulator_flow

input_esdl_file = Path(__file__).parents[1] / "tests" / "data" / "esdl" / "simulator_tutorial.esdl"
workflow_type_name = "simulator"

with open(input_esdl_file) as open_file:
    input_esdl = open_file.read()

simulator_flow_result = simulator_flow.fn(
    input_esdl=input_esdl,
    workflow_config={
        "timestep": 3600,
        "start_time": "2019-01-01T00:00:00.000Z",
        "end_time": "2019-01-31T00:00:00.000Z",
    },
    workflow_type_name=workflow_type_name,
)
if not isinstance(simulator_flow_result, SimulatorFlowResult):
    raise RuntimeError(f"Simulator flow did not return a result: {simulator_flow_result}")
if simulator_flow_result.output_esdl is None:
    raise RuntimeError("Simulator flow did not produce output ESDL")

print("--------------Result")
print(f"Job is done (type: {workflow_type_name}). Output esdl length: {len(simulator_flow_result.output_esdl)}, ")

# print("Output ESDL:", simulator_flow_result.output_esdl)
