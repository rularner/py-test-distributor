'''
This class creates a Python server that accepts tests being posted
'''
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI()


class TestRunExternal(BaseModel):
    ' Information we accept from clients about test runs '
    name: str
    tests: list[str]


class TestResult(BaseModel):
    ' Information about test run results '
    duration: int
    success: bool


class TestRunInternal(BaseModel):
    ' Internal information about test runs '
    name: str
    initial_tests: list[str]
    test_queue: list[str]
    test_results: dict[str, TestResult]


class Test(BaseModel):
    ' What we keep about individual tests '
    name: str


run_dict = {}
running_dict = {}
previous_test_runs = {}

'''
@app.post("/set_previous_run_data")
def set_previous_run_data(previous_runs: list[TestDurations]):
    previous_test_runs.append(previous_runs)


@app.get("/previous_run_data")
def previous_run_data():
    run_data = {}
    for test_run in run_dict:
        for test in test_run:
            run_data[test.name].append(run_data[test.duration])

    return {'name':key, 'duration':mean([value for key,value in run_data.items])}
'''


@app.post("/runs")
async def create_run(test_run: TestRunExternal):
    " Set up a new test run "
    if test_run.name in run_dict:
        if run_dict[test_run.name].tests != test_run.tests:
            return JSONResponse(
                status_code=400,
                content={
                    "Error": "Test list do not match previous post"
                },
            )
    else:
        run_dict[test_run.name] = TestRunInternal(
            name=test_run.name,
            initial_tests=test_run.tests,
            test_queue=test_run.tests,
            test_results={}
        )


@app.get("/runs/{run_id}/tests")
async def next_test(run_id: str):
    " Return the next test to run "
    next_test_id = run_dict[run_id].test_queue.pop()
    return next_test_id


@app.post("/runs/{run_id}/tests/{test_id}")
async def test_response(run_id: str, test_id: str, test_result: TestResult):
    " Notify about the current test result "
    run_dict[run_id].test_results[test_id] = test_result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)