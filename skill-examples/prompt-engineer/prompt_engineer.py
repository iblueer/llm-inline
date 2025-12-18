#!/usr/bin/env python3
"""
图像生成提示词工程师技能
将用户提供的原始提示词整理为高约束、低歧义、可被图像生成模型稳定遵循的提示词
"""

import sys


def main(args):
    """提示词工程技能的主函数"""
    # 导入llmi运行时API
    import llmi_runtime

    try:
        # 解析参数
        if len(args) == 0:
            print("❌ 请提供原始提示词")
            print("Usage: llmi prompt-engineer \"你的原始提示词\"")
            return False

        # 获取用户输入的原始提示词
        original_prompt = args[0]

        if not original_prompt.strip():
            print("⚠️ 提示词内容为空")
            return True

        print("🔍 原始提示词:")
        print("=" * 60)
        print(original_prompt)
        print("=" * 60)
        print()

        # 构建系统提示词（严格遵循 prompt.md 的规则）
        system_prompt = """你是一名“图像生成 Prompt 工程师”，任务是将用户提供的【原始提示词】整理、重构为一个【高约束、低歧义、可被图像生成模型稳定遵循的提示词】。

请严格遵循以下原则进行整理：

【目标】
- 提高生成结果的一致性和可控性
- 明确哪些内容是“不可变约束”，哪些是“可变风格”
- 避免模型自由发挥或重新设计主体

【处理规则】
1. 不新增任何用户未明确提出的设计要素
2. 不进行审美发挥或补充创意
3. 将模糊描述改写为明确、可执行的约束
4. 将否定式描述（如“不要”“没有”）改写为正向、枚举式描述
5. 若用户描述中存在冲突或不清晰之处，请原样保留，但用【需要确认】标注，不自行假设

【输出结构】
请将整理后的 Prompt 按以下固定结构输出（不要改变顺序）：

【不可变规则】
- 描述哪些内容绝对不能被改变（如：真实产品、外观不可重设计、唯一参考图等）

【构图与空间约束】
- 描述画面构图、主体位置、比例、相机视角、光影方向等
- 只保留与画面结构直接相关的内容

【主体与结构约束】
- 用条目化方式描述主体外观、结构、按钮、开孔、形态等
- 使用正向描述，避免否定句

【风格与表现】
- 描述整体风格、颜色、质感、氛围
- 明确风格不能覆盖或以上约束"""

        # 构建用户提示词
        user_prompt = f"【原始提示词如下】\n<<<\n{original_prompt}\n>>>\n\n现在开始整理并输出【最终约束性 Prompt】。"

        # 通过llmi调用LLM进行提示词工程
        print("🔧 正在进行提示词工程优化...")
        print()

        optimized_prompt = llmi_runtime.call_llm(
            prompt=user_prompt,
            system_prompt=system_prompt
        )

        print("✨ 优化后的提示词:")
        print("=" * 60)
        print(optimized_prompt)
        print("=" * 60)
        print()
        print("✅ 提示词工程完成！")

        return True

    except Exception as e:
        print(f"❌ 提示词工程失败: {e}")
        return False


if __name__ == "__main__":
    main(sys.argv[1:])