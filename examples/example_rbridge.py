import pandas as pd
from rtopy import RBridge, call_r


# One-off calls
result = call_r("add <- function(x,y) x+y", "add", x=5, y=3)
print(result)

# Reusable bridge
rb = RBridge()
r_code = '''make_df <- function(n) {
    data.frame(
        x = 1:n,
        y = rnorm(n),
        group = sample(c("A", "B"), n, replace=TRUE)
    )
}'''
r_func = "make_df"
n = 100
# Use "auto" to automatically choose the best return type
# (will use pandas if available, otherwise dict)
df = rb.call(r_code, r_func, return_type="pandas", n=n)
print(df)
print(pd.DataFrame(df))

rb = RBridge()

# Simple calculation
code = "add <- function(x, y) x + y"
rb.call(code, "add", x=5, y=3)
8.0

# Statistical summary
code = '''
summarize <- function(x) {
    list(mean=mean(x), sd=sd(x), n=length(x))
}
'''

rb.call(code, "summarize", return_type="pandas", x=[1,2,3,4,5])