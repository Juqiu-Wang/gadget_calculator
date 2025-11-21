#!/bin/bash

# 定义颜色输出，看起来更专业
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}=== 开始构建 Boolean Holant Gadget 计算器环境 ===${NC}"

# 1. 检查是否安装了 Python 3
if ! command -v python3 &> /dev/null
then
    echo -e "${RED}[错误] 未检测到 python3，请先安装 Python 3。${NC}"
    exit 1
fi

# 2. 创建虚拟环境 (名为 venv)
if [ -d "venv" ]; then
    echo -e "${GREEN}[信息] 虚拟环境 'venv' 已存在，跳过创建。${NC}"
else
    echo -e "${CYAN}[1/4] 正在创建 Python 虚拟环境...${NC}"
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[成功] 虚拟环境已建立。${NC}"
    else
        echo -e "${RED}[错误] 创建虚拟环境失败。${NC}"
        exit 1
    fi
fi

# 3. 激活环境并安装依赖
echo -e "${CYAN}[2/4] 正在激活环境并安装依赖 (Flask, SymPy)...${NC}"
source venv/bin/activate

# 升级 pip (可选，但推荐)
pip install --upgrade pip > /dev/null 2>&1

# 安装依赖
pip install flask sympy

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[成功] 依赖包 (Flask, SymPy) 安装完毕。${NC}"
else
    echo -e "${RED}[错误] 依赖包安装失败，请检查网络。${NC}"
    exit 1
fi

# 4. 建立目录结构
echo -e "${CYAN}[3/4] 检查并修复目录结构...${NC}"
if [ ! -d "templates" ]; then
    mkdir templates
    echo -e "${GREEN}[成功] 已创建 'templates' 文件夹 (这是 Flask 存放 HTML 的地方)。${NC}"
else
    echo -e "${GREEN}[信息] 'templates' 文件夹已存在。${NC}"
fi

# 5. 完成提示
echo -e "${CYAN}[4/4] 准备就绪！${NC}"
echo -e "----------------------------------------------------"
echo -e "环境已配置完成。你可以使用以下命令启动项目："
echo -e ""
echo -e "   ${GREEN}source venv/bin/activate${NC}  (激活环境)"
echo -e "   ${GREEN}python app.py${NC}             (启动程序)"
echo -e "----------------------------------------------------"