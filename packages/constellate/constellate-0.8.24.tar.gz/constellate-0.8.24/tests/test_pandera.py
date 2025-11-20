import pandas
import pandera as pa
from pyexpect import expect

from constellate.thirdparty.pandas.validation.pandera import PDASeries, PDAField, PDAIndex
from constellate.thirdparty.pandera.inspector import dataframe_from_schema, series_from_schema


def test_dataframe_from_schema() -> None:
    class _CompanyDFSchema(pa.DataFrameModel):
        idx: PDAIndex[str] = PDAField()
        name: PDASeries[str] = PDAField()
        age: PDASeries[int] = PDAField()

    df = dataframe_from_schema(schema=_CompanyDFSchema)
    expect(type(df)).to_equal(pandas.DataFrame)
    expect(len(df.columns)).to_equal(3)
    expect(df.empty).to_equal(True)


def test_series_from_schema() -> None:
    class _PersonSRSchema(pa.DataFrameModel):
        idx: PDAIndex[str] = PDAField()
        name: PDASeries[str] = PDAField()

    sr = series_from_schema(schema=_PersonSRSchema)
    expect(type(sr)).to_equal(pandas.Series)
    expect(sr.empty).to_equal(True)
