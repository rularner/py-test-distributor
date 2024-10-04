'''
This class creates a Python server that accepts tests being posted
'''
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI()


class TestRunExternal(BaseModel):
    name: str
    tests: list[str]


class TestResult(BaseModel):
    duration: int
    success: bool


class TestRunInternal(BaseModel):
    name: str
    initial_tests: list[str]
    test_queue: list[str]
    test_results: dict[str, TestResult]


class Test(BaseModel):
    name: str


class TestFinalState(BaseModel):
    name: str
    duration: str
    state: str
    reason: str


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
    if test_run.name in run_dict:
        if run_dict[test_run.name].tests != test_run.tests:
            return JSONResponse(
                status_code=400,
                content={
                    "Error": "Test list do not match previous post"
                },
            )
        else:
            return
    else:
        run_dict[test_run.name] = TestRunInternal(
            name=test_run.name,
            initial_tests=test_run.tests,
            test_queue=test_run.tests,
            test_results={}
        )


@app.get("/runs/{run_id}/tests")
async def next_test(run_id: str):
    next_test = run_dict[run_id].test_queue.pop()
    return next_test


@app.post("/runs/{run_id}/tests/{test_id}")
async def test_response(run_id: str, test_id: str, testResult: TestResult):
    run_dict[run_id].test_results[test_id] = testResult

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
