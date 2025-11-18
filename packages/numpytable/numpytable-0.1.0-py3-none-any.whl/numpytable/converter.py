import numpy as np
import warnings


def from_table(text: str) -> np.ndarray:
    '''
        将表格形式的文本（如Excel复制的内容）转换为NumPy数组。
        
        文本格式要求：
        - 每行代表数组的一行，行之间用换行符分隔
        - 元素之间用制表符（Tab）分隔（Excel默认复制格式）
        - 支持整数、浮点数（自动识别类型）
        
        参数:
            text: 包含表格数据的字符串（建议用三引号包裹多行文本）
        
        返回:
            np.ndarray: 转换后的NumPy数组
        
        示例:
            >>> from numpytable import from_table
            >>> import numpy as np
            >>> data = np.array(from_table("""
            ... 1	2	3
            ... 4	5	6.7
            ... 8	9	10
            ... """))
            >>> print(data)
            [[ 1.   2.   3. ]
            [ 4.   5.   6.7]
            [ 8.   9.  10. ]]
    '''
    # 1. 分割文本为行，过滤空行
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        raise ValueError("输入文本为空或仅包含空行，请检查内容")
    
    # 2. 解析每行元素，转换为数值类型
    matrix = []
    for line_idx, line in enumerate(lines, start=1):
        # 按制表符分割元素，过滤空元素（处理可能的多余制表符）
        elements = [elem.strip() for elem in line.split('\t') if elem.strip()]
        if not elements:
            warnings.warn(f"第{line_idx}行为空，已跳过")
            continue
        
        # 转换为数值（优先int，含小数点则转为float）
        try:
            numeric_elements = []
            for elem in elements:
                if '.' in elem:
                    numeric_elements.append(float(elem))
                else:
                    numeric_elements.append(int(elem))
        except ValueError as e:
            raise ValueError(f"第{line_idx}行存在非数值元素：{e}（请确保元素为数字）")
        
        matrix.append(numeric_elements)
    
    # 3. 检查每行元素数量是否一致
    row_lengths = [len(row) for row in matrix]
    if len(set(row_lengths)) > 1:
        warnings.warn(
            f"检测到每行元素数量不一致：{row_lengths}\n"
            "生成的数组可能为不规则维度（object类型），请检查输入格式"
        )
    
    # 4. 转换为NumPy数组并返回
    return np.array(matrix)