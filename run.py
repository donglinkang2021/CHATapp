import streamlit as st
from ollama import Client
import json

# 设置页面配置
st.set_page_config(
    page_title="Ollama Chat",
    layout="wide"
)

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

if "ollama_host" not in st.session_state:
    st.session_state.ollama_host = "http://localhost:11434"

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

if "available_models" not in st.session_state:
    st.session_state.available_models = []

if "client" not in st.session_state:
    st.session_state.client = None

# 侧边栏配置
with st.sidebar:
    st.header("配置")
    
    # Ollama服务地址输入
    ollama_host = st.text_input("Ollama服务地址", st.session_state.ollama_host)
    
    # 获取可用模型按钮
    if st.button("获取可用模型"):
        try:
            st.session_state.client = Client(host=ollama_host)
            response = st.session_state.client.list()
            st.session_state.available_models = [model.model for model in response.models]
            st.success("成功获取模型列表！")
        except Exception as e:
            st.error(f"获取模型失败: {str(e)}")
    
    # 模型选择下拉框
    if st.session_state.available_models:
        selected_model = st.selectbox(
            "选择模型",
            st.session_state.available_models
        )
        if selected_model != st.session_state.selected_model:
            st.session_state.selected_model = selected_model
            st.session_state.messages = []

# 主界面
st.header("Ollama Chat")

# 创建一个容器来显示聊天历史
chat_container = st.container()

# 在底部创建一个容器来放置输入框
input_container = st.container()

# 在聊天容器中显示消息历史
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 在底部容器中放置输入框
with input_container:
    # 聊天输入
    if prompt := st.chat_input("输入您的问题"):
        if not st.session_state.selected_model:
            st.error("请先选择一个模型！")
        else:
            # 添加用户消息
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # 添加助手消息
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                try:
                    # 使用客户端进行对话
                    stream = st.session_state.client.chat(
                        model=st.session_state.selected_model,
                        messages=[{"role": m["role"], "content": m["content"]} 
                                for m in st.session_state.messages],
                        stream=True,
                    )
                    
                    for chunk in stream:
                        full_response += chunk['message']['content']
                        message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                    # 保存助手响应
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"发生错误: {str(e)}")
