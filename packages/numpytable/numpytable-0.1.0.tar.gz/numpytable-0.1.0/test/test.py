import numpy as np
from numpytable import from_table

data1 = np.array(from_table("""
1	2	3
4	5	6.7
8	9	10
"""))

print(data1)
print(data1.dtype)  # 应为float64（因包含6.7）
data2 = np.array(from_table("""
1	2	3
4	5	6
8	9	10
"""))
print(data2)
print(data2.dtype)  # 应为int32

result = data1@data2
print(result)
print(result.dtype)  # 应为float64