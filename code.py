import pandas as pd

# First DataFrame
df1 = pd.DataFrame({
    "student_id": [1, 2, 3],
    "name": ["John", "Mary", "David"]
})

# Second DataFrame
df2 = pd.DataFrame({
    "student_id": [1, 2, 3],
    "grade": ["A", "B", "A"]
})

print("DataFrame 1:")
print(df1)

print("\nDataFrame 2:")
print(df2)