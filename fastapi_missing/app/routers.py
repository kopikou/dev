from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
import pandas as pd
import numpy as np
import missingno as msno
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
from typing import Optional
from fastapi_missing.app.schemas import *
from fastapi import HTTPException
from fastapi_missing.app.dependencies import get_user_data
from fastapi_missing.app.schemas import (
    ImputationMethod,
    ImputationResponse,
    VisualizationFormat,
)
from fastapi_missing.app.utils import TempStorage
from fastapi_missing.app.validation import ValidateData
from fastapi_missing.app.exceptions import (
    MissingDataThresholdException,
    InvalidImputationMethodException,
)
from fastapi_missing.app.memory import LocalStorage
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from statsmodels.imputation.mice import MICEData
import scipy.stats

router = APIRouter(prefix="/missing", tags=["missing_data"])

# --- Вспомогательные функции для импутации ---
def little_mcar_test(df: pd.DataFrame) -> float:
    """Тест Литтла для проверки MCAR (упрощенная версия)."""
    missing_corr = df.isnull().corr().abs().mean().mean()
    return missing_corr

def check_missing_mechanism_numeric(df: pd.DataFrame) -> str:
    """Определяет механизм пропущенных данных для числовых столбцов (MCAR/MAR/MNAR)."""
    if little_mcar_test(df.select_dtypes(include=np.number)) < 0.1:
        return "MCAR"

    for col in df.select_dtypes(include=np.number).columns[df.select_dtypes(include=np.number).isnull().any()]:
        other_cols = [c for c in df.columns if c != col and df[c].dtype in [np.number, np.float64, np.int64]]
        if df[other_cols].corrwith(df[col].isnull().astype(int)).abs().max() > 0.3:
            return "MAR"

    return "MNAR"

def check_missing_mechanism_categorical(df: pd.DataFrame, target_col: str) -> str:
    """Определяет механизм пропусков для строкового столбца."""
    for col in df.columns:
        if col != target_col and df[col].dtype != 'object':
            contingency_table = pd.crosstab(df[target_col].isnull(), df[col])
            chi2, p, _, _ = scipy.stats.chi2_contingency(contingency_table)
            if p < 0.05:
                return "MAR"

    return "MCAR"

def check_missing_mechanism(df: pd.DataFrame) -> dict:
    """Определяет механизм пропусков для всех столбцов."""
    mechanisms = {}

    numeric_cols = df.select_dtypes(include=np.number).columns
    if not numeric_cols.empty:
        numeric_mechanism = check_missing_mechanism_numeric(df[numeric_cols])
        for col in numeric_cols:
            mechanisms[col] = numeric_mechanism

    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        mechanisms[col] = check_missing_mechanism_categorical(df, col)

    return mechanisms

# --- 2. Методы импутации ---
def mean_imputation(df: pd.DataFrame) -> pd.DataFrame:
    """Замена пропусков средним значением (только числовые столбцы)."""
    df_imputed = df.copy()
    numeric_cols = df.select_dtypes(include=np.number).columns
    if not numeric_cols.empty:
        imputer = SimpleImputer(strategy='mean')
        df_imputed[numeric_cols] = imputer.fit_transform(df[numeric_cols])
    return df_imputed

def knn_imputation(df: pd.DataFrame, n_neighbors: int = 5) -> pd.DataFrame:
    """KNN-импутация с исправленной обработкой категориальных данных."""
    df_imputed = df.copy()

    # Сначала обрабатываем числовые данные
    numeric_cols = df.select_dtypes(include=np.number).columns
    if not numeric_cols.empty:
        imputer = KNNImputer(n_neighbors=n_neighbors)
        df_imputed[numeric_cols] = imputer.fit_transform(df[numeric_cols])

    # Затем категориальные данные (используем частый метод)
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if df[col].isnull().sum() > 0:
            df_imputed[col] = df[col].fillna(df[col].mode()[0])

    return df_imputed


def mice_imputation(df: pd.DataFrame, n_iter: int = 10) -> pd.DataFrame:
    """MICE-импутация (Multiple Imputation by Chained Equations)."""
    numeric_cols = df.select_dtypes(include=np.number).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    df_imputed = df.copy()

    if not numeric_cols.empty:
        mice_data = MICEData(df[numeric_cols])
        mice_data.update_all(n_iter)
        df_imputed[numeric_cols] = mice_data.data

    for col in categorical_cols:
        if df[col].isnull().sum() > 0:
            df_imputed[col] = df[col].fillna(df[col].mode()[0])

    return df_imputed


def frequent_imputation(df: pd.DataFrame) -> pd.DataFrame:
    """Замена пропусков наиболее частым значением."""
    df_imputed = df.copy()
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            if df[col].dtype == 'object':
                df_imputed[col] = df[col].fillna(df[col].mode()[0])
            else:
                df_imputed[col] = df[col].fillna(df[col].mean())
    return df_imputed

def random_forest_imputation(df: pd.DataFrame, target_col: str) -> pd.Series:
    """Импутация одного столбца с помощью Random Forest."""
    temp_df = df.copy()
    numeric_cols = temp_df.select_dtypes(include=np.number).columns
    feature_cols = [c for c in numeric_cols if c != target_col]
    
    train = temp_df.dropna(subset=[target_col])
    test = temp_df[temp_df[target_col].isnull()]
    
    if len(train) == 0 or len(feature_cols) == 0:
        return df[target_col].fillna(df[target_col].median())
    
    imputer = SimpleImputer(strategy='mean')
    X_train = imputer.fit_transform(train[feature_cols])
    y_train = train[target_col]
    
    model = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    if not test.empty:
        X_test = imputer.transform(test[feature_cols])
        imputed_values = model.predict(X_test)
        result = df[target_col].copy()
        result[result.isnull()] = imputed_values
        return result
    
    return df[target_col]

def perform_imputation(
    df: pd.DataFrame,
    threshold: float = 0.3,
    custom_method: Optional[str] = None
) -> dict:
    """Основная функция для импутации данных."""
    warnings_list = []
    missing_percent = df.isnull().mean().max()
    if missing_percent > threshold:
        warning_msg = f"Обнаружено {missing_percent*100:.1f}% пропусков (порог {threshold*100}%). Результаты могут быть ненадежными!"
        warnings.warn(warning_msg)
        warnings_list.append(warning_msg)

    mechanisms = check_missing_mechanism(df)
    df_imputed = df.copy()
    applied_methods = {}
    
    method_mapping = {
        "mean": mean_imputation,
        "knn": knn_imputation,
        "mice": mice_imputation,
        "random_forest": random_forest_imputation,
        "frequent": frequent_imputation
    }
    
    if custom_method:
        if custom_method == "mice":
            try:
                df_imputed = pd.DataFrame(
                    method_mapping[custom_method](df.select_dtypes(include=np.number)),
                    columns=df.select_dtypes(include=np.number).columns
                )
                # Для категориальных данных используем частый метод
                for col in df.select_dtypes(include=['object']).columns:
                    df_imputed[col] = df[col].fillna(df[col].mode()[0])
            except:
                df_imputed = df.fillna(df.mean())
        else:
            for col in df.columns:
                if df[col].isnull().sum() > 0:
                    if df[col].dtype == 'object' and custom_method != "frequent":
                        df_imputed[col] = df[col].fillna(df[col].mode()[0])
                    else:
                        if custom_method == "random_forest" and df[col].dtype in [np.number, np.float64, np.int64]:
                            df_imputed[col] = random_forest_imputation(df, col)
                        else:
                            imputer = SimpleImputer(
                                strategy='mean' if custom_method == "mean" else 'most_frequent'
                            )
                            df_imputed[[col]] = imputer.fit_transform(df[[col]])
        applied_methods = {col: custom_method for col in df.columns}
        method_used = custom_method
    else:
        method_used = "columnwise"
        for col, mechanism in mechanisms.items():
            if df[col].isnull().sum() == 0:
                applied_methods[col] = "no_imputation_needed"
                continue
                
            method = "knn" if mechanism == "MCAR" else "mice" if mechanism == "MAR" else "random_forest"
            applied_methods[col] = method
            
            if df[col].dtype == 'object':
                df_imputed[col] = df[col].fillna(df[col].mode()[0])
                continue
                
            if method == "random_forest":
                df_imputed[col] = random_forest_imputation(df, col)
            else:
                try:
                    if method == "mice":
                        mice_data = MICEData(df[[col]])
                        mice_data.update_all(5)
                        df_imputed[[col]] = mice_data.data
                    else:
                        imputer = KNNImputer(n_neighbors=5) if method == "knn" else SimpleImputer(strategy='mean')
                        df_imputed[[col]] = imputer.fit_transform(df[[col]])
                except:
                    df_imputed[col] = df[col].fillna(df[col].median())

    return {
        "mechanisms": mechanisms,
        "applied_methods": applied_methods,
        "method": method_used,
        "imputed_data": df_imputed,
        "original_data": df.copy(), 
        "stats_before": {
            col: {
                "missing": int(df[col].isnull().sum()),
                "missing_percent": float(df[col].isnull().mean()),
                "dtype": str(df[col].dtype)
            } for col in df.columns
        },
        "stats_after": {
            col: {
                "missing": int(df_imputed[col].isnull().sum()),
                "missing_percent": float(df_imputed[col].isnull().mean()),
                "dtype": str(df_imputed[col].dtype)
            } for col in df_imputed.columns
        },
        "warnings": warnings_list
    }

# --- API Endpoints ---
@router.post("/impute", response_model=ImputationResponse)
async def impute_data(
    threshold: float = Query(0.3, description="Порог допустимого процента пропусков (0-1)"),
    method: Optional[ImputationMethod] = Query(None, description="Метод импутации (если не указан, будет выбран автоматически)"),
    user_data: dict = Depends(get_user_data),
) -> ImputationResponse:
    """Эндпоинт для импутации пропущенных данных."""
    # if threshold > 0.3:
    #     raise MissingDataThresholdException(threshold)

    df = user_data["data"]
    ValidateData.check_dataframe(df)
    
    result = perform_imputation(
        df,
        threshold=threshold,
        custom_method=method.value if method else None
    )
    
    # Сохраняем оба набора данных в Redis
    await LocalStorage.set_dataframe(
        user_id=user_data["user_id"],
        df=result["imputed_data"],
        key_suffix="_imputed"
    )
    await LocalStorage.set_dataframe(
        user_id=user_data["user_id"],
        df=result["original_data"],
        key_suffix="_original"
    )
    
    return ImputationResponse(
        mechanisms=result["mechanisms"],
        applied_methods=result["applied_methods"],
        method_used=result["method"],
        stats_before=result["stats_before"],
        stats_after=result["stats_after"],
        warnings=result.get("warnings", [])
    )




@router.post("/visualize", response_class=FileResponse)
async def visualize_imputation(
    format: VisualizationFormat = VisualizationFormat.PNG,
    user_data: dict = Depends(get_user_data),
) -> FileResponse:
    """Генерация комплексной визуализации до/после импутации."""
    # Получаем оба набора данных из Redis
    df_before = await LocalStorage.get_dataframe(
        user_id=user_data["user_id"],
        key_suffix="_original"
    )
    df_after = await LocalStorage.get_dataframe(
        user_id=user_data["user_id"],
        key_suffix="_imputed"
    )
    
    if df_before is None or df_after is None:
        raise HTTPException(status_code=404, detail="Data not found")

    # Определяем механизмы пропусков для всех столбцов
    mechanisms = check_missing_mechanism(df_before)
    
    numeric_cols = df_before.select_dtypes(include=np.number).columns
    n_numeric = len(numeric_cols)
    
    # Рассчитываем структуру графиков
    n_kde_rows = (n_numeric + 1) // 2
    total_rows = 1 + n_kde_rows + 3  # +1 для статистики, +1 для таблицы механизмов, +1 для таблицы статистики
    
    # Создаем фигуру с динамической высотой
    fig = plt.figure(figsize=(18, 6 * total_rows), constrained_layout=True)
    gs = fig.add_gridspec(total_rows, 2, height_ratios=[1] + [1]*n_kde_rows + [0.5, 0.5, 1.5])
    
    # --- 1. Матрицы пропусков ---
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    
    msno.matrix(df_before, ax=ax1, sparkline=False)
    ax1.set_title("До импутации")
    msno.matrix(df_after, ax=ax2, sparkline=False)
    ax2.set_title("После импутации")
    
    # --- 2. KDE графики для числовых признаков ---
    if n_numeric > 0:
        for i, col in enumerate(numeric_cols):
            row = 1 + (i // 2)
            col_pos = i % 2
            ax = fig.add_subplot(gs[row, col_pos])
            
            sns.kdeplot(df_before[col].dropna(), label="До импутации", color="blue", alpha=0.7, fill=True)
            sns.kdeplot(df_after[col], label="После импутации", color="orange", alpha=0.7, fill=True)
            
            ax.set_title(f"Распределение '{col}'")
            ax.set_xlabel("Значение")
            ax.set_ylabel("Плотность")
            ax.legend()
    
    # --- 4. Полная описательная статистика для числовых колонок ---
    if n_numeric > 0:
        # Получаем полную статистику со всеми нужными квантилями
        stats_before = df_before[numeric_cols].describe(percentiles=[.25, .5, .75]).T
        stats_after = df_after[numeric_cols].describe(percentiles=[.25, .5, .75]).T
        
        # Создаем таблицу с полной статистикой
        ax_stats = fig.add_subplot(gs[total_rows-1, :])  # Занимает всю последнюю строку
        ax_stats.axis('off')
        
        # Подготовка данных для таблицы
        stats_data = []
        columns = ["Параметр", "count (до)", "mean (до)", "std (до)", 
                  "min (до)", "25% (до)", "50% (до)", "75% (до)", "max (до)",
                  "count (после)", "mean (после)", "std (после)", 
                  "min (после)", "25% (после)", "50% (после)", "75% (после)", "max (после)"]
        
        for col in numeric_cols:
            before = stats_before.loc[col]
            after = stats_after.loc[col]
            stats_data.append([
                col,
                f"{before['count']:.0f}",
                f"{before['mean']:.2f}",
                f"{before['std']:.2f}",
                f"{before['min']:.2f}",
                f"{before['25%']:.2f}",
                f"{before['50%']:.2f}",
                f"{before['75%']:.2f}",
                f"{before['max']:.2f}",
                f"{after['count']:.0f}",
                f"{after['mean']:.2f}",
                f"{after['std']:.2f}",
                f"{after['min']:.2f}",
                f"{after['25%']:.2f}",
                f"{after['50%']:.2f}",
                f"{after['75%']:.2f}",
                f"{after['max']:.2f}"
            ])
        
        # Создаем таблицу статистики
        stats_table = ax_stats.table(
            cellText=stats_data,
            colLabels=columns,
            loc='center',
            cellLoc='center'
        )
        
        # Настраиваем таблицу статистики
        stats_table.auto_set_font_size(False)
        stats_table.set_fontsize(8)
        stats_table.scale(1, 1.2)
        
        # Добавляем заголовок
        ax_stats.set_title("Описательная статистика", y=1.05, pad=20)
    
    # --- 5. Общая информация о пропусках ---
    ax_info = fig.add_subplot(gs[total_rows-2, :])  # Предпоследняя строка
    ax_info.axis('off')
    
    # Рассчитываем общую статистику пропусков
    total_missing_before = df_before.isnull().sum().sum()
    total_missing_after = df_after.isnull().sum().sum()
    percent_missing_before = (total_missing_before / (df_before.size)) * 100
    percent_missing_after = (total_missing_after / (df_after.size)) * 100
    
    info_text = (
        f"Общая статистика пропусков:\n"
        f"До импутации: {total_missing_before} пропущенных значений ({percent_missing_before:.2f}% данных)\n"
        f"После импутации: {total_missing_after} пропущенных значений ({percent_missing_after:.2f}% данных)\n"
        f"Всего колонок: {len(df_before.columns)} (числовых: {n_numeric}, категориальных: {len(df_before.columns) - n_numeric})"
    )
    
    ax_info.text(
        0, 0.5, 
        info_text,
        ha="left", va="center", fontsize=11,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.5)
    )
    
    plt.subplots_adjust(hspace=0.5, wspace=0.3)
    return TempStorage.return_file(save_format=format, fig=fig)

@router.post("/download", response_class=FileResponse)
async def download_imputed_data(
    format: FileFormat = FileFormat.CSV,
    user_data: dict = Depends(get_user_data),
) -> FileResponse:
    """Скачивание импутированных данных."""
    df = await LocalStorage.get_dataframe(
        user_id=user_data["user_id"],
        key_suffix="_imputed"
    )
    return TempStorage.return_dataframe(df=df, save_format=format)


# Добавляем новые эндпоинты в router

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_data(
    user_data: dict = Depends(get_user_data),
) -> AnalysisResponse:
    """Анализ данных перед импутацией."""
    df = user_data["data"]
    ValidateData.check_dataframe(df)
    
    # Определяем механизмы пропусков
    mechanisms = check_missing_mechanism(df)
    
    # Формируем рекомендации по методам импутации
    recommended_methods = {}
    for col, mechanism in mechanisms.items():
        if df[col].isnull().sum() == 0:
            recommended_methods[col] = "no_imputation_needed"
        else:
            if mechanism == "MCAR":
                recommended_methods[col] = "knn или mean"
            elif mechanism == "MAR":
                recommended_methods[col] = "mice"
            else:
                recommended_methods[col] = "random_forest" if df[col].dtype in [np.number, np.float64, np.int64] else "frequent"
    
    # Сохраняем оригинальные данные в Redis
    await LocalStorage.set_dataframe(
        user_id=user_data["user_id"],
        df=df,
        key_suffix="_original"
    )
    
    # Формируем статистику
    stats = {
        col: {
            "missing": int(df[col].isnull().sum()),
            "missing_percent": float(df[col].isnull().mean()),
            "dtype": str(df[col].dtype),
            "mechanism": mechanisms.get(col, "unknown"),
            "recommended_method": recommended_methods.get(col, "unknown")
        } for col in df.columns
    }
    
    return AnalysisResponse(stats=stats)

@router.post("/visualize-matrix", response_class=FileResponse)
async def visualize_missing_matrix(
    format: VisualizationFormat = VisualizationFormat.PNG,
    user_data: dict = Depends(get_user_data),
) -> FileResponse:
    """Визуализация матрицы пропусков."""
    df = user_data["data"]
    
    plt.figure(figsize=(12, 6))
    msno.matrix(df)
    plt.title("Матрица пропусков в данных")
    
    return TempStorage.return_file(save_format=format, fig=plt.gcf())

@router.post("/visualize-graphs", response_class=FileResponse)
async def visualize_imputation_graphs(
    format: VisualizationFormat = VisualizationFormat.PNG,
    user_data: dict = Depends(get_user_data),
) -> FileResponse:
    """Генерация графиков (матрицы пропусков и распределения)."""
    df_before = await LocalStorage.get_dataframe(
        user_id=user_data["user_id"],
        key_suffix="_original"
    )
    df_after = await LocalStorage.get_dataframe(
        user_id=user_data["user_id"],
        key_suffix="_imputed"
    )
    
    if df_before is None or df_after is None:
        raise HTTPException(status_code=404, detail="Data not found")

    numeric_cols = df_before.select_dtypes(include=np.number).columns
    n_numeric = len(numeric_cols)
    
    # Создаем фигуру только с графиками
    fig = plt.figure(figsize=(18, 6 * (1 + (n_numeric + 1) // 2)), constrained_layout=True)
    gs = fig.add_gridspec(1 + (n_numeric + 1) // 2, 2)
    
    # 1. Матрицы пропусков
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    
    msno.matrix(df_before, ax=ax1, sparkline=False)
    ax1.set_title("До импутации")
    msno.matrix(df_after, ax=ax2, sparkline=False)
    ax2.set_title("После импутации")
    
    # 2. KDE графики для числовых признаков
    if n_numeric > 0:
        for i, col in enumerate(numeric_cols):
            row = 1 + (i // 2)
            col_pos = i % 2
            ax = fig.add_subplot(gs[row, col_pos])
            
            sns.kdeplot(df_before[col].dropna(), label="До импутации", color="blue", alpha=0.7, fill=True)
            sns.kdeplot(df_after[col], label="После импутации", color="orange", alpha=0.7, fill=True)
            
            ax.set_title(f"Распределение '{col}'")
            ax.set_xlabel("Значение")
            ax.set_ylabel("Плотность")
            ax.legend()
    
    plt.tight_layout()
    return TempStorage.return_file(save_format=format, fig=fig)

@router.post("/visualize-tables", response_class=FileResponse)
async def visualize_imputation_tables(
    format: VisualizationFormat = VisualizationFormat.PNG,
    user_data: dict = Depends(get_user_data),
) -> FileResponse:
    """Генерация таблиц (статистика пропусков и описательная статистика)."""
    df_before = await LocalStorage.get_dataframe(
        user_id=user_data["user_id"],
        key_suffix="_original"
    )
    df_after = await LocalStorage.get_dataframe(
        user_id=user_data["user_id"],
        key_suffix="_imputed"
    )
    
    if df_before is None or df_after is None:
        raise HTTPException(status_code=404, detail="Data not found")

    numeric_cols = df_before.select_dtypes(include=np.number).columns
    
    # Создаем фигуру только с таблицами
    fig = plt.figure(figsize=(18, 10), constrained_layout=True)
    gs = fig.add_gridspec(2, 1, height_ratios=[0.5, 1.5])
    
    # 1. Общая информация о пропусках
    ax_info = fig.add_subplot(gs[0, 0])
    ax_info.axis('off')
    
    total_missing_before = df_before.isnull().sum().sum()
    total_missing_after = df_after.isnull().sum().sum()
    percent_missing_before = (total_missing_before / (df_before.size)) * 100
    percent_missing_after = (total_missing_after / (df_after.size)) * 100
    
    info_text = (
        f"Общая статистика пропусков:\n"
        f"До импутации: {total_missing_before} пропущенных значений ({percent_missing_before:.2f}% данных)\n"
        f"После импутации: {total_missing_after} пропущенных значений ({percent_missing_after:.2f}% данных)\n"
        f"Всего колонок: {len(df_before.columns)} (числовых: {len(numeric_cols)}, категориальных: {len(df_before.columns) - len(numeric_cols)})"
    )
    
    ax_info.text(
        0, 0.5, 
        info_text,
        ha="left", va="center", fontsize=11,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.5)
    )
    
    # 2. Описательная статистика для числовых колонок
    if len(numeric_cols) > 0:
        stats_before = df_before[numeric_cols].describe(percentiles=[.25, .5, .75]).T
        stats_after = df_after[numeric_cols].describe(percentiles=[.25, .5, .75]).T
        
        ax_stats = fig.add_subplot(gs[1, 0])
        ax_stats.axis('off')
        
        stats_data = []
        columns = ["Параметр", "count (до)", "mean (до)", "std (до)", 
                  "min (до)", "25% (до)", "50% (до)", "75% (до)", "max (до)",
                  "count (после)", "mean (после)", "std (после)", 
                  "min (после)", "25% (после)", "50% (после)", "75% (после)", "max (после)"]
        
        for col in numeric_cols:
            before = stats_before.loc[col]
            after = stats_after.loc[col]
            stats_data.append([
                col,
                f"{before['count']:.0f}",
                f"{before['mean']:.2f}",
                f"{before['std']:.2f}",
                f"{before['min']:.2f}",
                f"{before['25%']:.2f}",
                f"{before['50%']:.2f}",
                f"{before['75%']:.2f}",
                f"{before['max']:.2f}",
                f"{after['count']:.0f}",
                f"{after['mean']:.2f}",
                f"{after['std']:.2f}",
                f"{after['min']:.2f}",
                f"{after['25%']:.2f}",
                f"{after['50%']:.2f}",
                f"{after['75%']:.2f}",
                f"{after['max']:.2f}"
            ])
        
        stats_table = ax_stats.table(
            cellText=stats_data,
            colLabels=columns,
            loc='center',
            cellLoc='center'
        )
        stats_table.auto_set_font_size(False)
        stats_table.set_fontsize(8)
        stats_table.scale(1, 1.2)
        ax_stats.set_title("Описательная статистика", y=1.05, pad=20)
    
    plt.tight_layout()
    return TempStorage.return_file(save_format=format, fig=fig)