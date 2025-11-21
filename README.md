# **Boolean Holant Gadget Construction Calculator**

**(布尔 Holant 问题 Gadget 构造计算器)**

这是一个基于 Web 的可视化工具，旨在辅助理论计算机科学家研究 **Boolean Holant 问题**。它允许用户通过图形化界面构建 Gadget（小部件），定义顶点函数（Signatures），并计算在特定 **全息基 (Holographic Basis)** 变换下的最终收缩结果。

\!(https://www.google.com/search?q=https://via.placeholder.com/800x400%3Ftext%3DHolant%2BGadget%2BBuilder%2BInterface)

## **🛠️ 功能特性**

* **可视化构建**: 通过拖拽添加顶点，点击端口进行连线，直观构建 Gadget 拓扑。  
* **符号计算核心**: 后端基于 SymPy，完美支持**复数域** ($\\mathbb{C}$) 和**符号变量** ($x, y$) 的运算，无精度丢失。  
* **全息变换 (Holographic Transformation)**: 支持对所有顶点应用全局基变换 $M$（如 $Z$-变换, Hadamard 变换），自动计算 $M^{\\otimes k} F$。  
* **张量收缩 (Tensor Contraction)**: 自动识别内部边并进行求和收缩，输出关于悬挂边（外部变量）的最终 Signature。  
* **自由端口连接**: 支持任意端口对任意端口 (Port-to-Port) 的连接方式。

## **🚀 环境搭建与安装**

本项目依赖 **Python 3**。

### **方法一：自动脚本安装 (推荐)**

我们提供了一个自动化脚本，可以一键完成虚拟环境创建和依赖安装。

1. 在终端中赋予脚本执行权限：  
   chmod \+x setup.sh

2. 运行安装脚本：  
   ./setup.sh

   *脚本会自动创建 venv 文件夹，安装 flask 和 sympy，并检查目录结构。*

### **方法二：手动安装**

1. **创建虚拟环境**:  
   python3 \-m venv venv

2. **激活环境**:  
   * macOS/Linux: source venv/bin/activate  
   * Windows: venv\\Scripts\\activate  
3. **安装依赖**:  
   pip install flask sympy

4. 创建目录结构:  
   确保项目根目录下有一个名为 templates 的文件夹，并将 index.html 放入其中。

## **▶️ 启动服务**

1. 确保虚拟环境已激活。  
2. 运行 Flask 后端：  
   python app.py

3. 打开浏览器访问：  
   \[http://127.0.0.1:5001\](http://127.0.0.1:5001)

   *(注：默认端口设为 5001 以避免与 macOS AirPlay 服务冲突)*

## **📖 使用指南**

### **1\. 构建 Gadget**

* **添加节点**: 在左侧栏输入名称和度数 (Arity)，点击 Drop Node。  
* **连线**: 鼠标移至节点的**红色端口 (Port)**，按下并拖拽至另一个节点的端口。  
* **删除连线**: 双击已连接的端口。

### **2\. 定义函数 (Signatures)**

* 点击任意节点选中它。  
* 在左侧 Signature 框中输入 Python 列表格式的真值表。  
* **长度要求**: 必须严格等于 $2^{\\text{Arity}}$。  
* **支持格式**:  
  * 整数: \[1, 0, 0, 1\] (Equality Gate)  
  * 复数: \[1, 'I', '-I', 1\] (支持 'i' 或 'I')  
  * 变量: \[1, 'x', 'x', 'y'\]

### **3\. 应用全息变换 (Holographic Basis)**

在 Computation 面板输入 $2 \\times 2$ 变换矩阵。

* **Z-Basis (Standard)**:  
  \[\[1, 1\], \["I", "-I"\]\]

* **Hadamard**:  
  \[\[1, 1\], \[1, \-1\]\]

* **留空**: 默认为恒等变换 (Identity)。

### **4\. 计算结果**

点击 Compute Contraction。结果将显示：

* **Signature**: 收缩后的向量结果。  
* **Variables**: 结果向量对应的外部变量顺序 (例如 v\_0\_1 代表节点0的第1个端口)。

## **🧠 服务实现原理 (Technical Details)**

### **后端架构 (Flask \+ SymPy)**

服务核心由 contract\_network 函数驱动：

1. 全息预处理 (Basis Change):  
   对每个节点的原始 Signature $F$，使用 Kronecker Product 计算变换后的张量：  
   $$ \\hat{F} \= M^{\\otimes k} F $$  
   这里我们手动实现了 kronecker\_product 以确保 SymPy 返回二维矩阵对象，避免高维张量类型错误。  
2. **符号索引分配 (Index Labeling)**:  
   * **内部边**: 为每一条连接两个节点的边分配一个求和变量 $e\_{i}$。  
   * **悬挂边**: 为每一个未连接的端口分配一个自由变量 $v\_{j}$。  
3. 暴力收缩 (Brute-force Contraction):  
   由于 Boolean Holant 问题的域大小为 2 ($q=2$)，且 Gadget 规模通常较小，我们采用遍历求和法：  
   $$ \\text{Result}(v\_{ext}) \= \\sum\_{e\_{int} \\in {0,1}} \\prod\_{node \\in V} \\hat{F}\_{node}(\\dots) $$  
   这种方法虽然复杂度为指数级，但在处理符号计算和小规模图验证时最为稳健。

### **前端架构 (HTML5 Canvas)**

* 无第三方图形库依赖，使用原生 Canvas API 实现高性能绘图。  
* 实现了基于极坐标的端口自动布局算法。  
* 通过 AJAX (Fetch API) 与 Python 后端进行 JSON 数据交换。

## **📂 项目结构**

.  
├── app.py              \# Flask 后端主程序 (核心算法)  
├── setup.sh            \# 环境配置脚本  
├── README.md           \# 说明文档  
└── templates/          \# Flask 模板目录  
    └── index.html      \# 前端界面 (Canvas 交互)  
