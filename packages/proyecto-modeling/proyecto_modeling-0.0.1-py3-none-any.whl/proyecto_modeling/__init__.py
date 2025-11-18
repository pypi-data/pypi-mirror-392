# -*- coding: utf-8 -*-
"""
Modeling - standalone implementation.
"""

import os
from datetime import datetime
from typing import Dict, List, Tuple
import json
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import f1_score, accuracy_score
import joblib

from proyecto_core import ensure_dirs, logger, MODELS_DIR, EXP_LOG


def make_classification_pipeline(min_df: int = 2, C: float = 1.0) -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=min_df)),
        ("clf", LinearSVC(C=C, random_state=42, max_iter=2000)),
    ])


def train_model(texts: List[str], labels: List[str], min_df: int = 2, C: float = 1.0, seed: int = 42) -> Tuple[Pipeline, Dict]:
    logger.info("[MODELING] Iniciando entrenamiento...")
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=seed, stratify=labels)
    pipe = make_classification_pipeline(min_df=min_df, C=C)
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "f1_macro": float(f1_score(y_test, y_pred, average="macro")),
        "test_size": len(X_test),
        "train_size": len(X_train),
    }
    logger.info(f"[MODELING] Métricas: {metrics}")
    return pipe, metrics


def cross_validate_model(texts: List[str], labels: List[str], cv_folds: int = 5, min_df: int = 2, C: float = 1.0, seed: int = 42) -> Dict:
    logger.info(f"[MODELING] Iniciando cross-validation ({cv_folds} folds)...")
    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=seed)
    X = np.array(texts, dtype=object)
    y = np.array(labels, dtype=object)
    scores = {"accuracy": [], "f1_macro": []}
    for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        X_train, X_test = X[train_idx].tolist(), X[test_idx].tolist()
        y_train, y_test = y[train_idx].tolist(), y[test_idx].tolist()
        pipe = make_classification_pipeline(min_df=min_df, C=C)
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        scores["accuracy"].append(float(accuracy_score(y_test, y_pred)))
        scores["f1_macro"].append(float(f1_score(y_test, y_pred, average="macro")))
        logger.info(f"  Fold {fold+1}/{cv_folds}: Acc={scores['accuracy'][-1]:.4f}, F1={scores['f1_macro'][-1]:.4f}")
    result = {
        "cv_folds": cv_folds,
        "accuracy_mean": float(np.mean(scores["accuracy"])),
        "accuracy_std": float(np.std(scores["accuracy"])),
        "f1_macro_mean": float(np.mean(scores["f1_macro"])),
        "f1_macro_std": float(np.std(scores["f1_macro"])),
        "fold_scores": scores,
    }
    logger.info(f"[MODELING] CV Result: Acc={result['accuracy_mean']:.4f}±{result['accuracy_std']:.4f}")
    return result


def save_model(pipe: Pipeline, path: str = None) -> str:
    ensure_dirs(MODELS_DIR)
    if path is None:
        existing = [f for f in os.listdir(MODELS_DIR) if f.endswith('.joblib')]
        version = len(existing) + 1
        path = os.path.join(MODELS_DIR, f"svm_tfidf_v{version}.joblib")
    joblib.dump(pipe, path)
    logger.info(f"[MODELING] Modelo guardado: {path}")
    return path


def load_model(path: str) -> Pipeline:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Modelo no encontrado: {path}")
    return joblib.load(path)


def log_experiment(run_info: Dict):
    ensure_dirs(os.path.dirname(EXP_LOG))
    run_info["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(EXP_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(run_info, ensure_ascii=False) + "\n")
    logger.info(f"[MODELING] Experimento registrado: {EXP_LOG}")


def hyperparameter_sweep(texts: List[str], labels: List[str], param_grid: List[Dict], cv_folds: int = 3, seed: int = 42) -> List[Dict]:
    logger.info(f"[MODELING] Iniciando hyperparameter sweep ({len(param_grid)} configs)...")
    results = []
    for i, params in enumerate(param_grid):
        logger.info(f"  [{i+1}/{len(param_grid)}] Params: {params}")
        cv_result = cross_validate_model(texts, labels, cv_folds=cv_folds, min_df=params.get("min_df", 2), C=params.get("C", 1.0), seed=seed)
        result = {**params, "cv_results": cv_result}
        results.append(result)
        log_experiment({"type": "hyperparameter_sweep", "params": params, "metrics": cv_result})
    results.sort(key=lambda r: -r["cv_results"]["f1_macro_mean"])
    logger.info(f"[MODELING] Mejor config: {results[0]}")
    return results


__all__ = [
    "make_classification_pipeline",
    "train_model",
    "cross_validate_model",
    "save_model",
    "load_model",
    "log_experiment",
    "hyperparameter_sweep",
]
