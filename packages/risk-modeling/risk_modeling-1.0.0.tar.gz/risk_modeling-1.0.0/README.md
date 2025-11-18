# About The Project

While GitHub hosts many excellent risk modeling libraries, most emphasize traditional logistic regression approaches. This project addresses modern needs by:
1.  Focusing on **tree-based methodologies** (XGBoost, LightGBM)
2.  Providing **essential modeling tools** (PSI, IV, Bivar, etc.)
3.  Supporting **documentation of all modeling steps**

---

## Library Functionality

### 📈 Modeling Procedure
- **Hyperparameter Tuning**:  
  `random_search_xgboost()`, `random_search_lightgbm()`
- **Model Training**:  
  `train_single_model_xgboost()`, `train_single_model_lightgbm()`
- **Feature Analysis**:  
  `feature_importance()` (gain-based),  
  `variable_reduction()` (feature-importance-driven selection)
- **Performance Metrics**:  
  `model_performance()` (AUC, KS, Top Capture Rate, Top Bad Rate)

### 🛠️ Modeling Tools
- **Stability Analysis**:  
  `calculate_numeric_psi()`, `calculate_categorical_psi()`
- **Predictive Strength**:  
  `calculate_numeric_iv()`, `calculate_categorical_iv()`
- **Feature Evaluation**:  
  `compute_numeric_bivar()`, `compute_categorical_bivar()`,  
  `proc_means()` (quality checks)
- **UAT Support**:  
  `proc_compare()` (feature-by-feature value validation)
