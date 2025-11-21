import json
from flask import Flask, render_template, request, jsonify
from sympy import symbols, Matrix, sympify, tensorproduct, I, simplify, expand, zeros # <--- 添加 zeros
from sympy.parsing.sympy_parser import parse_expr

app = Flask(__name__)

def kronecker_product(A, B):
    """
    手动实现矩阵的 Kronecker 积，确保返回 Matrix 对象而不是 NDimArray
    A: m x n Matrix
    B: p x q Matrix
    Result: mp x nq Matrix
    """
    rows_A, cols_A = A.shape
    rows_B, cols_B = B.shape
    
    # 创建全零大矩阵
    res = zeros(rows_A * rows_B, cols_A * cols_B)
    
    for i in range(rows_A):
        for j in range(cols_A):
            # 将 B 乘以 A[i,j] 放入对应的块位置
            # 这里的切片赋值是 SymPy Matrix 的特性
            scalar = A[i, j]
            # 注意：SymPy 切片是 [start:end]，不包含 end
            r_start = i * rows_B
            r_end = (i + 1) * rows_B
            c_start = j * cols_B
            c_end = (j + 1) * cols_B
            
            res[r_start:r_end, c_start:c_end] = scalar * B
            
    return res

def apply_transform(signature_list, arity, transform_matrix_str, node_name="Unknown"):
    """
    应用全息变换 (修复了 Tensor 类型错误)
    """
    if not transform_matrix_str or not transform_matrix_str.strip():
        return signature_list

    try:
        print(f"--- 开始变换节点: {node_name} (Arity: {arity}) ---")
        
        # 1. 解析 JSON
        clean_str = transform_matrix_str.replace("'", '"').replace('i', 'I').replace('j', 'I')
        M_list = json.loads(clean_str)
        
        # 2. 转为 SymPy 矩阵
        M_list = [[sympify(cell) for cell in row] for row in M_list]
        M = Matrix(M_list)

        if M.shape != (2, 2):
            raise ValueError("变换矩阵必须是 2x2。")

        # 3. 计算 M 的 Arity 次张量积 (使用 Kronecker Product)
        # M_final = M (x) M (x) ... (x) M
        print(f"[Debug] 计算 M 的 {arity} 次 Kronecker 积...")
        
        M_final = M
        for _ in range(arity - 1):
            # 使用我们要手写的 kronecker_product 替代 tensorproduct
            M_final = kronecker_product(M_final, M)
            
        # 4. 准备 Signature 向量
        sig_vec = Matrix(signature_list)
        
        expected_len = 2**arity
        if len(sig_vec) != expected_len:
            raise ValueError(f"Signature 长度应为 {expected_len}")

        # 5. 矩阵乘法 (现在 M_final 是标准的 Matrix，不会报错了)
        result_vec = M_final * sig_vec
        result_list = [simplify(x) for x in result_vec]
        
        print(f"[Success] 变换完成。结果前项: {result_list[:2]}...")
        return result_list

    except Exception as e:
        print(f"[Error] 节点 {node_name} 变换失败: {e}")
        raise e

def contract_network(nodes, edges, transform_matrix=None):
    # 1. 建立端口映射
    # port_mapping[(node_id, pin_index)] = symbol_name
    port_mapping = {}
    internal_symbols = set()
    
    # 为每条边生成一个唯一的符号
    for edge in edges:
        s_node, s_pin = edge['source'], edge['sourceHandle']
        t_node, t_pin = edge['target'], edge['targetHandle']
        
        # 定义边变量 e_{smaller_id}_{larger_id} 以保证一致性
        sym_name = f"e_{min(s_node, t_node)}_{max(s_node, t_node)}_{s_pin}_{t_pin}"
        sym = symbols(sym_name)
        
        port_mapping[(s_node, s_pin)] = sym
        port_mapping[(t_node, t_pin)] = sym
        internal_symbols.add(sym)

    # 2. 准备节点 Tensor
    node_tensors = []
    dangling_indices = [] # 记录所有的自由变量（悬挂边）

    for node in nodes:
        nid = node['id']
        arity = node['arity']
        sig_raw = node['signature']
        
        # 解析 Signature
        sig_sympy = []
        for x in sig_raw:
            try:
                s = parse_expr(str(x).replace('i', 'I'), local_dict={'I': I})
                sig_sympy.append(s)
            except:
                sig_sympy.append(sympify(0))
        
        if transform_matrix:
            sig_sympy = apply_transform(sig_sympy, arity, transform_matrix)
            
        # 确定该节点的索引列表
        current_indices = []
        for i in range(arity):
            if (nid, i) in port_mapping:
                current_indices.append(port_mapping[(nid, i)])
            else:
                # 这是一个悬挂边，视为外部变量
                # 命名为 out_{nid}_{pin_index}
                free_sym = symbols(f'v_{nid}_{i}')
                current_indices.append(free_sym)
                dangling_indices.append(free_sym)
        
        node_tensors.append({
            'data': sig_sympy,
            'indices': current_indices
        })

    # 3. 数值收缩 (Sum over internal edges {0,1})
    # 结果是一个关于 dangling_indices 的真值表
    final_signature = []
    result_arity = len(dangling_indices)
    
    # 遍历外部变量的所有组合 (2^k)
    for i in range(2**result_arity):
        # 生成外部变量赋值，例如 [0, 1, 0]
        # 注意位序：高位对应 dangling_indices[0]
        ext_vals = [(i >> j) & 1 for j in range(result_arity - 1, -1, -1)]
        val_map = {sym: val for sym, val in zip(dangling_indices, ext_vals)}
        
        # 对内部变量求和
        current_entry_sum = 0
        symbols_list = list(internal_symbols)
        num_internal = len(symbols_list)
        
        for j in range(2**num_internal):
            int_vals = [(j >> k) & 1 for k in range(num_internal - 1, -1, -1)]
            int_map = {sym: val for sym, val in zip(symbols_list, int_vals)}
            
            full_map = {**val_map, **int_map}
            
            # 计算所有节点的乘积
            term_prod = 1
            for n_info in node_tensors:
                # 找出该节点当前的 index 值 (e.g. [0, 1, 1] -> 3)
                idx_val = 0
                for bit_sym in n_info['indices']:
                    bit = full_map[bit_sym]
                    idx_val = (idx_val << 1) | bit
                
                term_prod *= n_info['data'][idx_val]
            
            current_entry_sum += term_prod
            
        final_signature.append(str(simplify(current_entry_sum)))

    # 构造返回信息，包括变量顺序
    dangling_names = [str(s) for s in dangling_indices]
    
    return {
        'signature': final_signature,
        'variables': dangling_names
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        result = contract_network(data.get('nodes', []), data.get('edges', []), data.get('transform'))
        return jsonify({'status': 'success', 'result': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    # 使用 5001 防止冲突
    app.run(debug=True, port=5001)