"""
Advanced RBridge Usage Examples
================================

Demonstrates using R packages, statistical modeling, and data processing
through the Python-R bridge.
"""

import numpy as np
import pandas as pd
from rtopy import RBridge, call_r


# ============================================================================
# Example 1: Support Vector Machine with e1071
# ============================================================================
print("=" * 70)
print("Example 1: SVM Classification with e1071")
print("=" * 70)

# Generate training data
np.random.seed(42)
n_samples = 100

# Class 0: centered at (-1, -1)
X0 = np.random.randn(n_samples // 2, 2) * 0.5 + np.array([-1, -1])
# Class 1: centered at (1, 1)
X1 = np.random.randn(n_samples // 2, 2) * 0.5 + np.array([1, 1])

X_train = np.vstack([X0, X1])
y_train = np.array([0] * (n_samples // 2) + [1] * (n_samples // 2))

# Create R code for SVM training and prediction
svm_code = '''
library(e1071)

train_svm <- function(X, y, kernel_type = "radial") {
    # Convert to data frame
    df <- data.frame(
        x1 = X[, 1],
        x2 = X[, 2],
        y = as.factor(y)
    )
    
    # Train SVM
    model <- svm(y ~ x1 + x2, data = df, kernel = kernel_type, cost = 1)
    
    # Make predictions on training data
    predictions <- predict(model, df)
    
    # Calculate accuracy
    accuracy <- mean(predictions == df$y)
    
    # Return results
    list(
        predictions = as.numeric(as.character(predictions)),
        accuracy = accuracy,
        n_support = model$tot.nSV
    )
}
'''

rb = RBridge(verbose=True)
result = rb.call(
    svm_code, 
    "train_svm",
    return_type="dict",
    X=X_train,
    y=y_train,
    kernel_type="radial"
)

print(f"Training Accuracy: {result['accuracy']:.2%}")
print(f"Number of Support Vectors: {result['n_support']}")
print(f"Sample Predictions: {result['predictions'][:10]}")


# ============================================================================
# Example 2: Time Series Analysis with forecast package
# ============================================================================
print("\n" + "=" * 70)
print("Example 2: Time Series Forecasting with forecast")
print("=" * 70)

# Generate time series data
time_series = np.sin(np.linspace(0, 4*np.pi, 50)) + np.random.randn(50) * 0.1

ts_code = '''
library(forecast)

forecast_ts <- function(x, h = 10) {
    # Convert to time series object
    ts_data <- ts(x, frequency = 12)
    
    # Fit ARIMA model
    fit <- auto.arima(ts_data, seasonal = FALSE)
    
    # Generate forecast
    fc <- forecast(fit, h = h)
    
    # Return results
    list(
        forecast_mean = as.numeric(fc$mean),
        forecast_lower = as.numeric(fc$lower[, 2]),  # 95% CI
        forecast_upper = as.numeric(fc$upper[, 2]),
        model_aic = fit$aic,
        model_order = paste0("ARIMA(", 
                            paste(arimaorder(fit), collapse = ","), 
                            ")")
    )
}
'''

result = rb.call(
    ts_code,
    "forecast_ts",
    return_type="dict",
    x=time_series.tolist(),
    h=10
)

print(f"Model: {result['model_order']}")
print(f"AIC: {result['model_aic']:.2f}")
print(f"10-step forecast: {np.array(result['forecast_mean'])[:5]}...")


# ============================================================================
# Example 3: Random Forest with randomForest package
# ============================================================================
print("\n" + "=" * 70)
print("Example 3: Random Forest Regression")
print("=" * 70)

# Generate regression data
np.random.seed(123)
X = np.random.rand(200, 3) * 10
y = 2*X[:, 0] + 3*X[:, 1] - X[:, 2] + np.random.randn(200) * 2

rf_code = '''
library(randomForest)

train_rf <- function(X, y, ntree = 500) {
    # Create data frame
    df <- data.frame(
        x1 = X[, 1],
        x2 = X[, 2],
        x3 = X[, 3],
        y = y
    )
    
    # Train random forest
    rf_model <- randomForest(y ~ ., data = df, ntree = ntree, importance = TRUE)
    
    # Get predictions
    predictions <- predict(rf_model, df)
    
    # Calculate R-squared
    r_squared <- 1 - sum((y - predictions)^2) / sum((y - mean(y))^2)
    
    # Get feature importance
    importance_scores <- importance(rf_model)[, 1]  # %IncMSE
    
    list(
        r_squared = r_squared,
        mse = rf_model$mse[ntree],
        predictions = predictions,
        importance = importance_scores
    )
}
'''

result = rb.call(
    rf_code,
    "train_rf",
    return_type="dict",
    X=X,
    y=y.tolist(),
    ntree=500
)

print(f"R-squared: {result['r_squared']:.3f}")
print(f"MSE: {result['mse']:.3f}")
print(f"Feature Importance: {result['importance']}")


# ============================================================================
# Example 4: Statistical Tests with stats package
# ============================================================================
print("\n" + "=" * 70)
print("Example 4: Statistical Hypothesis Testing")
print("=" * 70)

# Generate two samples
group1 = np.random.normal(5, 2, 50)
group2 = np.random.normal(6, 2, 50)

stats_code = '''
perform_tests <- function(group1, group2) {
    # T-test
    t_result <- t.test(group1, group2)
    
    # Wilcoxon test (non-parametric alternative)
    w_result <- wilcox.test(group1, group2)
    
    # Kolmogorov-Smirnov test
    ks_result <- ks.test(group1, group2)
    
    list(
        t_test = list(
            statistic = t_result$statistic,
            p_value = t_result$p.value,
            conf_int = t_result$conf.int
        ),
        wilcox_test = list(
            statistic = w_result$statistic,
            p_value = w_result$p.value
        ),
        ks_test = list(
            statistic = ks_result$statistic,
            p_value = ks_result$p.value
        ),
        summary_stats = list(
            group1_mean = mean(group1),
            group2_mean = mean(group2),
            group1_sd = sd(group1),
            group2_sd = sd(group2)
        )
    )
}
'''

result = rb.call(
    stats_code,
    "perform_tests",
    return_type="dict",
    group1=group1.tolist(),
    group2=group2.tolist()
)

print(f"Group 1 Mean: {result['summary_stats']['group1_mean']:.2f} ± {result['summary_stats']['group1_sd']:.2f}")
print(f"Group 2 Mean: {result['summary_stats']['group2_mean']:.2f} ± {result['summary_stats']['group2_sd']:.2f}")
print(f"\nT-test p-value: {result['t_test']['p_value']:.4f}")
print(f"Wilcoxon p-value: {result['wilcox_test']['p_value']:.4f}")


# ============================================================================
# Example 5: Data Transformation with dplyr
# ============================================================================
print("\n" + "=" * 70)
print("Example 5: Data Wrangling with dplyr")
print("=" * 70)

# Create sample dataset
data = pd.DataFrame({
    'id': range(1, 101),
    'group': np.random.choice(['A', 'B', 'C'], 100),
    'value': np.random.randn(100) * 10 + 50,
    'score': np.random.randint(1, 101, 100)
})

dplyr_code = '''
library(dplyr)

process_data <- function(df) {
    # Convert list columns to data frame
    data <- as.data.frame(df)
    
    # Perform dplyr operations
    result <- data %>%
        filter(score > 50) %>%
        group_by(group) %>%
        summarise(
            n = n(),
            mean_value = mean(value),
            median_score = median(score),
            sd_value = sd(value)
        ) %>%
        arrange(desc(mean_value))
    
    # Convert back to list format for JSON
    as.list(result)
}
'''

result = rb.call(
    dplyr_code,
    "process_data",
    return_type="pandas",
    df=data
)

print("\nGrouped Summary Statistics:")
print(result)


# ============================================================================
# Example 6: Clustering with cluster package
# ============================================================================
print("\n" + "=" * 70)
print("Example 6: K-means and Hierarchical Clustering")
print("=" * 70)

# Generate clustered data
np.random.seed(42)
cluster_data = np.vstack([
    np.random.randn(30, 2) * 0.5 + np.array([0, 0]),
    np.random.randn(30, 2) * 0.5 + np.array([3, 3]),
    np.random.randn(30, 2) * 0.5 + np.array([0, 3])
])

cluster_code = '''
library(cluster)

perform_clustering <- function(X, k = 3) {
    # Convert to matrix
    data_matrix <- as.matrix(X)
    
    # K-means clustering
    kmeans_result <- kmeans(data_matrix, centers = k, nstart = 25)
    
    # Hierarchical clustering
    dist_matrix <- dist(data_matrix)
    hc <- hclust(dist_matrix, method = "ward.D2")
    hc_clusters <- cutree(hc, k = k)
    
    # Silhouette analysis for k-means
    sil <- silhouette(kmeans_result$cluster, dist_matrix)
    avg_silhouette <- mean(sil[, 3])
    
    list(
        kmeans_clusters = kmeans_result$cluster,
        kmeans_centers = kmeans_result$centers,
        kmeans_withinss = kmeans_result$tot.withinss,
        hc_clusters = hc_clusters,
        silhouette_score = avg_silhouette
    )
}
'''

result = rb.call(
    cluster_code,
    "perform_clustering",
    return_type="dict",
    X=cluster_data,
    k=3
)

print(f"K-means Within-cluster SS: {result['kmeans_withinss']:.2f}")
print(f"Average Silhouette Score: {result['silhouette_score']:.3f}")
print(f"\nCluster Centers:\n{np.array(result['kmeans_centers'])}")
print(f"\nCluster sizes: {np.bincount(result['kmeans_clusters'])}")


print("\n" + "=" * 70)
print("All examples completed successfully!")
print("=" * 70)