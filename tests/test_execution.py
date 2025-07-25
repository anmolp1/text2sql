import pytest
import pandas as pd
from src.execution.bigquery_client import run_query
from src.config import settings

# --- Dummy classes to simulate BigQuery behavior ---

class DummyResult:
    def __init__(self, df):
        self._df = df

    def to_dataframe(self):
        return self._df

class DummyQueryJob:
    def __init__(self, df):
        self._df = df

    def result(self):
        return DummyResult(self._df)

class DummyClient:
    def __init__(self, project):
        # Assert that the correct project is passed in
        assert project == settings.GCP_PROJECT

    def query(self, sql: str):
        # Simulate an error when SQL is exactly "RAISE"
        if sql == "RAISE":
            raise Exception("Simulated BigQuery failure")
        # Otherwise return a small dummy DataFrame
        df = pd.DataFrame({"col1": [10, 20], "col2": ["a", "b"]})
        return DummyQueryJob(df)

# --- Fixture to patch out the real BigQuery Client ---

@pytest.fixture(autouse=True)
def patch_bigquery_client(monkeypatch):
    """
    Monkey-patch google.cloud.bigquery.Client to return our DummyClient.
    """
    import google.cloud.bigquery as bq_mod
    monkeypatch.setattr(bq_mod, "Client", lambda project: DummyClient(project))

# --- Tests ---

def test_run_query_success():
    sql = "SELECT * FROM my_table"
    df = run_query(sql)
    # Should return a pandas DataFrame with our dummy data
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["col1", "col2"]
    assert df["col1"].tolist() == [10, 20]
    assert df["col2"].tolist() == ["a", "b"]

def test_run_query_failure():
    with pytest.raises(RuntimeError) as excinfo:
        run_query("RAISE")
    # The wrapper should catch the Exception and raise RuntimeError
    assert "Error executing query" in str(excinfo.value)