from .codermanager import CoderTemplateManager
from typing import List, Dict, Any,Optional
import re

coder = CoderTemplateManager()

# --- 工具函数实现 ---

def search_template_by_text(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    根据自然语言查询在模板库中进行语义搜索（使用 Qdrant 向量检索），返回最相关的 `top_k` 个模板的摘要信息。
    """
    print("search_template_by_text")
    print(f"input & {type(query)} & query: {query} top:k {top_k} ")
    search_result = coder.search(
        text=query,
        limit=top_k,
        # query_filter=None # 可以在这里添加额外的过滤条件，例如根据语言、框架过滤
    )

    templates_summary = []
    for hit in search_result:
        # 在实际 Qdrant 中，hit.id 是模板的ID，hit.payload 包含其他元数据
        # 假设你的 Qdrant payload 中存储了 template_name 和 description
        templates_summary.append({
            'template_id': hit.payload.get("template_id"),
            'description': hit.payload.get('description', 'No description provided.'),
            'match_score': hit.score
        })
    print(f"output & {type(templates_summary)} & {templates_summary} ")
    return templates_summary

def get_template_details(template_id: str) -> Optional[Dict[str, Any]]: # template_id 根据你的模型是 Integer
    """
    根据 `template_id` 从数据库中获取模板的完整详细信息，包括模板代码、推断出的命名约定和使用建议。
    """
    print("get_template_details")
    print(f"input & {type(template_id)} & query: {template_id} ")
    template = coder.get_template_obj(template_id = template_id)
    if template:
        return {
            'template_id': template.template_id,
            'description': template.description,
            'template_code': template.template_code,
            'version': template.version,
        }
    print(f"output & {type(template)} & {template} ")
    return None


def ask_user_for_clarification(question: str) -> str:
    """
    当你对用户需求有疑问，或需要用户做选择（例如在多个匹配模板中选择一个）时，使用此工具向用户提问。
    """
    print("ask_user_for_clarification")
    print(f"input & {type(question)} & query: {question} ")
    print("\n--- Agent 需要你的帮助 ---")
    print(f"Agent: {question}")
    user_input = input("你的回答: ")
    print("-------------------------\n")
    print(f"output & {type(user_input)} & query: {user_input} ")
    return user_input


def generate_request_file(template_code: str, user_request_details: Dict[str, Any], naming_conventions: Optional[Dict[str, Any]] = None) -> str:
    """
    根据选定的模板代码、解析后的用户需求（结构化形式）和模板的命名约定，生成符合 `REQUEST_START/END` 格式的指令文件。
    `user_request_details` 应该是一个字典，键是 BLOCK/PLACEHOLDER 的名称，值是包含 '指令' 和 '约束/示例' 的字典。
    """
    print("generate_request_file")
    print(f"input & {type(template_code)} & template_code: {template_code} user_request_details: {user_request_details} naming_conventions: {naming_conventions}")

    request_parts = []

    request_parts.append("--- REQUEST_START ---")
    request_parts.append("template.py # 目标文件通常是这个，可以根据实际情况调整") # 假设一个通用文件名

    # 添加整体目标描述
    overall_goal = user_request_details.get("overall_goal", "完善代码模板以满足以下需求。")
    request_parts.append(f"\n**目标：** {overall_goal}\n")

    # 添加命名约定 (如果提供了)
    if naming_conventions:
        request_parts.append("**命名约定:**")
        for key, value in naming_conventions.items():
            request_parts.append(f"*   **{key}:** {value}")
        request_parts.append("") # 空行

    request_parts.append("**具体修改点：**\n")

    # 遍历模板代码，找到所有的 BLOCK 和 PLACEHOLDER
    # 然后根据 user_request_details 填充指令
    # 这是一个简化版本，实际可能需要更复杂的解析器来处理嵌套块或动态生成的块
    # 对于 MVP，我们可以假设 user_request_details 中包含了所有需要填充的块/占位符
    block_pattern = r"(BLOCK_START|PLACEHOLDER):\s*(\w+)"
    for match in re.finditer(block_pattern, template_code):
        block_type = match.group(1)
        block_name = match.group(2)

        if block_name in user_request_details:
            details = user_request_details[block_name]
            instruction = details.get("指令", "")
            constraint_example = details.get("约束/示例", "")

            request_parts.append(f"*   **{block_type}: {block_name}**")
            request_parts.append(f"    *   **指令：** {instruction}")
            if constraint_example:
                # 确保多行约束/示例能正确缩进
                formatted_ce = "\n".join([f"    *   **约束/示例：** {line}" if i == 0 else f"    *   {line}" for i, line in enumerate(str(constraint_example).splitlines())])
                request_parts.append(formatted_ce)
            request_parts.append("") # 空行

    request_parts.append("--- REQUEST_END ---")
    print(f"output & {type(request_parts)} & request_parts: {request_parts} ")

    result = "\n".join(request_parts)
    return result



from modusched.core import BianXieAdapter
from pro_craft.utils import extract_

llm2 = """
你是一个专业的Python代码修改和生成AI。你的任务是根据用户提供的代码模板文件和详细的修改指令文件，精确地对模板进行补充、完善和修改。

**你的目标是：**
1.  **严格遵循指令文件中的所有要求，尤其是针对特定 `BLOCK` 和 `PLACEHOLDER` 的指令和约束/示例。**
2.  **尽可能应用指令文件中提供的命名约定。**
3.  **仅修改指令明确要求修改的部分，模板中未被指令覆盖的固定部分必须保持不变。**
4.  **最终输出完整且可运行的Python代码。**

**输入格式:**
用户将以以下两个部分向你提供信息：

--- TEMPLATE_CODE_START ---
[原始的代码模板内容，其中包含 BLOCK_START/END 和 PLACEHOLDER/END_PLACEHOLDER 标记]
--- TEMPLATE_CODE_END ---

--- REQUEST_FILE_START ---
[一个结构化的指令文件，格式为 REQUEST_START/END，包含目标、命名约定和具体修改点]
--- REQUEST_FILE_END ---

**你的工作流程和生成原则:**

1.  **解析指令文件：**
    *   首先解析 `REQUEST_FILE_START` 中的所有内容，理解其 `目标`、`命名约定` 和 `具体修改点`。
    *   将 `具体修改点` 中的每个 `BLOCK` 和 `PLACEHOLDER` 指令及其 `约束/示例` 映射到模板代码中的对应位置。
2.  **处理模板代码：**
    *   逐行读取 `TEMPLATE_CODE_START` 中的模板代码。
    *   当遇到 `BLOCK_START` 或 `PLACEHOLDER` 标记时：
        *   查找指令文件中对应 `块名称` 的修改指令。
        *   **如果存在指令：**
            *   删除 `BLOCK_START` 和 `BLOCK_END` (或 `PLACEHOLDER` 和 `END_PLACEHOLDER`) 及其内部的原始内容（包括 `AI:` 注释）。
            *   用指令中提供的代码**替换**该区域。
            *   在替换的代码块的开始和结束位置，添加特殊的标记 `// AI_MODIFIED_START` 和 `// AI_MODIFIED_END` (如果只是新增内容，可以使用 `// AI_ADDED_START` 和 `// AI_ADDED_END`)。
            *   如果指令是要求删除某些内容，请用 `// AI_DELETED_LINE: [原始行内容]` 标记被删除的行。
        *   **如果不存在指令：**
            *   保留该 `BLOCK` 或 `PLACEHOLDER` 及其内部的原始内容（包括 `AI:` 注释和标记本身），不做任何改动。这允许模板中的可选部分在没有明确指令时保持原样。
    *   当遇到非标记的普通代码行时，保持其不变。
3.  **应用命名约定：**
    *   在生成或修改代码时，优先应用 `REQUEST_FILE_START` 中提供的 `命名约定`。
    *   **重要：** 命名约定只应影响由你**生成或修改**的代码部分（即 `AI_ADDED` 或 `AI_MODIFIED` 区域）。你不能随意修改模板中未被明确指令触及的固定代码部分的命名。
4.  **生成中间输出：**
    *   首先生成包含所有 `// AI_ADDED/MODIFIED/DELETED` 标记的完整代码。这有助于后续的自动化工具进行变更追踪和人工核查。
5.  **生成最终输出：**
    *   在生成中间输出后，进一步处理该代码，**移除所有 `// AI_ADDED/MODIFIED/DELETED` 类型的标记**。
    *   移除所有模板中遗留的 `BLOCK_START/END` 和 `PLACEHOLDER/END_PLACEHOLDER` 标记。
    *   保留所有的 Docstrings 和常规的代码注释。

**你的输出必须是最终的、清理后的完整 Python 代码文件内容。**

"""

def generate_code(request: str, template: str) -> str:
    """
    使用生成的代码指令, 生成代码
    """
    bx = BianXieAdapter()
    result = bx.product(system_prompt = llm2 ,prompt = template + request)
    python_code = extract_(result,r"python")
    return python_code
