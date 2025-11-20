import pandas
import pandas as pd
import pytest
from pyexpect import expect

from constellate.thirdparty.pandas.extra.sanitize.sanitize import fill_missing_from_schema
from constellate.thirdparty.pandas.validation.pandera import (
    PDASeries,
    PDAField,
    BaseConfig,
    PDAIndex,
)
import pandera as pa

from constellate.thirdparty.pandas.validation.validation import (
    pandas_data_coerce_and_validate,
    DataValidationError,
)


@pytest.mark.parametrize("asynced", [False, True])
@pytest.mark.asyncio
async def test_pandas_data_coerce_and_validate(asynced) -> None:
    class _PandaDataChecksDFSchema(pa.DataFrameModel):
        name: PDASeries[pandas.StringDtype] = PDAField()
        age: PDASeries[pandas.Int64Dtype] = PDAField()
        country: PDASeries[pandas.StringDtype] = PDAField()

        class Config(BaseConfig):
            pass

    # Validation success
    d = {"name": ["apple", "fruit"], "age": [1, 2], "country": ["italy", "usa"]}
    if asynced:

        @pandas_data_coerce_and_validate(schema=_PandaDataChecksDFSchema)
        async def _build_dataframe(data: dict = None):
            return pd.DataFrame(data=data)

        df = await _build_dataframe(data=d)
    else:

        @pandas_data_coerce_and_validate(schema=_PandaDataChecksDFSchema)
        def _build_dataframe(data: dict = None):
            return pd.DataFrame(data=data)

        df = _build_dataframe(data=d)

    expect(df.shape).to_equal((2, 3))

    # Validation failed
    for data in [
        # Name is not all str
        {"name": ["apple", "fruit"], "age": [1, object()], "country": ["italy", "usa"]},
        # Country column is missing
        {"name": ["apple", "fruit"], "age": [1, 2]},
        # Cost column is not in schema
        {"name": ["apple", "fruit"], "age": [1, 2], "country": ["italy", "usa"], "cost": [10, 12]},
    ]:
        with pytest.raises(DataValidationError):
            if asynced:

                @pandas_data_coerce_and_validate(schema=_PandaDataChecksDFSchema)
                async def _build_dataframe(data: dict = None):
                    return pd.DataFrame(data=data)

                await _build_dataframe(data=data)
            else:

                @pandas_data_coerce_and_validate(schema=_PandaDataChecksDFSchema)
                def _build_dataframe(data: dict = None):
                    return pd.DataFrame(data=data)

                _build_dataframe(data=data)


@pytest.mark.parametrize(
    "p",
    [
        ((1, 2), pd.DataFrame(data={"name": ["foo"], "surname": ["bar"]}), (1, 1)),
        ((2,), pd.Series(data={"name": ["foo"], "surname": ["bar"]}), (1,)),
    ],
)
def test_pandas_attribute_accessor(p) -> None:
    # Load DataFrameAttributeAccessor / SeriesAttributeAccessor

    shape_original = p[0]
    obj = p[1]
    shape_final = p[2]
    expect(obj.aa is not None).to_equal(True)

    # Read
    expect(obj.aa.name[0]).to_equal("foo")
    expect(obj.aa.surname[0]).to_equal("bar")

    # Write
    obj.aa.surname[0] = "baz"
    expect(obj.aa.surname[0]).to_equal("baz")

    # Delete
    expect(obj.shape).to_equal(shape_original)
    del obj.aa.surname
    expect(obj.shape).to_equal(shape_final)


@pytest.mark.parametrize("typed", [pandas.DataFrame, pandas.Series])
def test_pandas_fill_missing_from_schema(typed) -> None:
    if typed == pandas.DataFrame:
        #
        # Fill column name
        #
        class _FillMissingColumnFromSchemaDFSchema(pa.DataFrameModel):
            time: PDAIndex[pandas.StringDtype] = PDAField()
            age: PDASeries[pandas.Int64Dtype] = PDAField()
            name: PDASeries[pandas.StringDtype] = PDAField()

        df = pandas.DataFrame()
        df = fill_missing_from_schema(schema=_FillMissingColumnFromSchemaDFSchema, data=df)
        expect(isinstance(df.index, pandas.Index)).to_equal(True)
        expect(type(df.index.dtype)).to_equal(pandas.StringDtype)
        expect(type(df.age.dtype)).to_equal(pandas.Int64Dtype)
        expect(type(df.name.dtype)).to_equal(pandas.StringDtype)

        class _FillMissingColumnFromSchemaDFSchemaMultiIndex(pa.DataFrameModel):
            time: PDAIndex[pandas.StringDtype] = PDAField()
            uid: PDAIndex[pandas.Int64Dtype] = PDAField()
            age: PDASeries[pandas.Int64Dtype] = PDAField()
            name: PDASeries[pandas.StringDtype] = PDAField()

        #
        # Fill column dtype
        #
        class _FillNanFromSchemaDFSchemaNoIndex(pa.DataFrameModel):
            age: PDASeries[pandas.Int64Dtype] = PDAField()
            name: PDASeries[pandas.StringDtype] = PDAField()

        df = pandas.DataFrame(data={"age": [None, None], "name": [None, None]})
        df = fill_missing_from_schema(schema=_FillNanFromSchemaDFSchemaNoIndex, data=df)
        expect(type(df.age.dtype)).to_equal(pandas.Int64Dtype)
        expect(type(df.name.dtype)).to_equal(pandas.StringDtype)
        expect(type(df["age"][0])).to_equal(type(pandas.NA))
        expect(type(df["name"][0])).to_equal(type(pandas.NA))

        class _FillNanFromSchemaDFSchemaMonoIndex(pa.DataFrameModel):
            time: PDAIndex[pandas.StringDtype] = PDAField()
            age: PDASeries[pandas.Int64Dtype] = PDAField()
            name: PDASeries[pandas.StringDtype] = PDAField()

        df = pandas.DataFrame(
            index=["20/10/2022", "21/10/2022"], data={"age": [None, None], "name": [None, None]}
        )
        df = fill_missing_from_schema(schema=_FillNanFromSchemaDFSchemaMonoIndex, data=df)
        expect(isinstance(df.index, pandas.Index)).to_equal(True)
        expect(type(df.index.dtype)).to_equal(pandas.StringDtype)
        expect(type(df.age.dtype)).to_equal(pandas.Int64Dtype)
        expect(type(df.name.dtype)).to_equal(pandas.StringDtype)
        expect(df.index[0]).to_equal("20/10/2022")
        expect(type(df["age"][0])).to_equal(type(pandas.NA))
        expect(type(df["name"][0])).to_equal(type(pandas.NA))

        class _FillNanFromSchemaDFSchemaMultiIndex(pa.DataFrameModel):
            time: PDAIndex[pandas.StringDtype] = PDAField()
            uid: PDAIndex[pandas.Int64Dtype] = PDAField()
            age: PDASeries[pandas.Int64Dtype] = PDAField()
            name: PDASeries[pandas.StringDtype] = PDAField()

        multi_index = pandas.MultiIndex.from_tuples(
            [("20/10/2022", 0), ("21/10/2022", 1)], names=["time", "uid"]
        )
        df = pandas.DataFrame(index=multi_index, data={"age": [None, None], "name": [None, None]})
        df = fill_missing_from_schema(schema=_FillNanFromSchemaDFSchemaMultiIndex, data=df)
        expect(isinstance(df.index, pandas.MultiIndex)).to_equal(True)
        expect(type(df.age.dtype)).to_equal(pandas.Int64Dtype)
        expect(type(df.name.dtype)).to_equal(pandas.StringDtype)
        expect(df.index[0]).to_equal(("20/10/2022", 0))
        expect(type(df["age"][0])).to_equal(type(pandas.NA))
        expect(type(df["name"][0])).to_equal(type(pandas.NA))

    elif typed == pandas.Series:

        class _FillNanFromSchemaSRSchemaNoIndex(pa.DataFrameModel):
            age: PDASeries[pandas.Int64Dtype] = PDAField()

        sr = pandas.Series(data={0: None})
        sr = fill_missing_from_schema(schema=_FillNanFromSchemaSRSchemaNoIndex, data=sr)
        expect(type(sr[0])).to_equal(type(pandas.NA))

        class _FillNanFromSchemaSRSchemaMonoIndex(pa.DataFrameModel):
            time: PDAIndex[pandas.StringDtype] = PDAField()
            age: PDASeries[pandas.Int64Dtype] = PDAField()

        sr = pandas.Series(
            data={"20/10/2022": None, "21/10/2022": 20}, index=["20/10/2022", "21/10/2022"]
        )
        sr = fill_missing_from_schema(schema=_FillNanFromSchemaSRSchemaMonoIndex, data=sr)
        expect(isinstance(sr.index, pandas.Index)).to_equal(True)
        expect(type(sr.index.dtype)).to_equal(pandas.StringDtype)
        expect(type(sr["20/10/2022"])).to_equal(type(pandas.NA))

        class _FillNanFromSchemaSRSchemaMultiIndex(pa.DataFrameModel):
            time: PDAIndex[pandas.StringDtype] = PDAField()
            uid: PDAIndex[pandas.Int64Dtype] = PDAField()
            age: PDASeries[pandas.Int64Dtype] = PDAField()

        multi_index = pandas.MultiIndex.from_tuples(
            [("20/10/2022", 0), ("21/10/2022", 1)], names=["time", "uid"]
        )
        sr = pandas.Series(data={"20/10/2022": None, "21/10/2022": 20}, index=multi_index)
        sr = fill_missing_from_schema(schema=_FillNanFromSchemaSRSchemaMultiIndex, data=sr)
        expect(isinstance(sr.index, pandas.MultiIndex)).to_equal(True)
        expect(type(sr[("20/10/2022", 0)])).to_equal(type(pandas.NA))

    else:
        raise NotImplementedError()
