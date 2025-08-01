from fastapi import APIRouter, Depends

from fastapi.responses import FileResponse
import matplotlib.pyplot as plt
import seaborn as sns

from fastapi_visualization.app.schemas import (
    CorrelationMethod,
    ParamsForScatterplot,
    ParamsForScatterplotFast,
    ParamsForVisualizationCorrelation,
    ParamsForVisualizationCorrelationFast,
    ImageFormat,
)
from fastapi_visualization.app.validation import CorrelationValidation, ValidateData
from fastapi_visualization.app.dependencies import *
from fastapi_visualization.app.utils import TempStorage
from fastapi_visualization.app.builders import CorrelationBuilder
from fastapi_visualization.app.memory import *


router = APIRouter(prefix="/visualization", tags=["visualization"])


@router.post("/heatmap")
async def get_heatmap(
    params: ParamsForVisualizationCorrelation,
    method: CorrelationMethod = CorrelationMethod.SPEARMAN,
    data: dict = Depends(get_user_data),
) -> dict[str, dict[str, float | None]]:
    df = CorrelationValidation.validate(df=data["data"], columns=params.columns)

    result = CorrelationBuilder.build(
        df=df, method=method, round_value=params.round_value, replace_nan=True
    )

    return result.to_dict()


@router.post("/heatmap/fast")
async def get_heatmap_fast(
    params: ParamsForVisualizationCorrelationFast,
    method: CorrelationMethod = CorrelationMethod.SPEARMAN,
    save_format: ImageFormat = ImageFormat.PNG,
    data: dict = Depends(get_user_data),
) -> FileResponse:
    df = CorrelationValidation.validate(df=data["data"], columns=params.columns)

    result = CorrelationBuilder.build(df=df, method=method)

    fig_width = result.shape[1]  # ширина зависит от количества столбцов
    fig_height = result.shape[0]  # высота зависит от количества строк

    plt.figure(figsize=(fig_width, fig_height))
    sns.heatmap(
        result,
        annot=True,
        cmap="YlGnBu",
        cbar=params.cbar,
        xticklabels=result.columns,
        yticklabels=result.index,
    )

    plt.xticks(rotation=params.x_lable_rotation)

    if params.title is not None:
        plt.title(params.title)

    return TempStorage.return_file(save_format=save_format)


@router.post("/scatterplot")
async def get_scatterplot(
    params: ParamsForScatterplot,
    data: dict = Depends(get_user_data),
) -> dict:
    columns = [params.x_column, params.y_column]
    if params.hue_column is not None:
        columns.append(params.hue_column)

    df = ValidateData.check_columns(df=data["data"], columns=columns)

    return df.to_dict()


@router.post("/scatterplot/fast")
async def get_scatterplot_fast(
    params: ParamsForScatterplotFast,
    save_format: ImageFormat = ImageFormat.PNG,
    data: dict = Depends(get_user_data),
) -> dict:
    columns = [params.x_column, params.y_column]
    if params.hue_column is not None:
        columns.append(params.hue_column)

    df = ValidateData.check_columns(df=data["data"], columns=columns)

    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df,
        x=params.x_column,
        y=params.y_column,
        hue=params.hue_column,
        palette="viridis",
        s=params.dot_size,
        legend="auto" if params.need_legend is True else False,
    )

    plt.xlabel(params.x_column)
    plt.ylabel(params.y_column)

    if params.title is not None:
        plt.title(params.title)

    return TempStorage.return_file(save_format=save_format)
