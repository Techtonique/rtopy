from rtopy import callfunc

r_code = '''
calculate_stats <- function(data) {
    list(
        mean = mean(data),
        median = median(data),
        variance = var(data),
        standard_deviation = sd(data),
        quantiles = quantile(data, probs = c(0.25, 0.5, 0.75))
    )
}
'''

data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
result = callfunc(
    r_code=r_code,
    r_func="calculate_stats",
    type_return="dict",
    data=data
)
# Returns: {'mean': 55.0, 'median': 55.0, 'variance': 916.6667, ...}