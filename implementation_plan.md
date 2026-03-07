# Implementation Plan

[Overview]
将当前面向各类 agent 生成、展示和测试的 `speckit` 前缀斜杠指令/skills 统一切换为 `sdd`，并移除对旧前缀 `speckit` 的对外兼容暴露。

本次修改的目标不是只改 README 文案，而是把“命令名前缀”从模板源头、CLI 本地生成逻辑、release 打包脚本、skills 安装逻辑、扩展命令校验规则、测试断言和用户文档中统一替换为 `sdd`，确保任意支持的 agent 初始化后看到和使用的都是 `/sdd.*` 或等价 `sdd-*` skills，而不再出现 `/speckit.*`。根据用户已确认的策略边界，本次为**直接切换**：不保留旧前缀别名、不做双写兼容、不在对外产物中同时暴露 `speckit` 与 `sdd`。

从代码与产物链路看，前缀传播有明确证据链：`templates/commands/*.md` 是命令正文与示例文案的源头；`src/specify_cli/__init__.py::_generate_commands_for_agent()` 将模板产出为 `speckit.{name}.md/.toml/.prompt.md/.agent.md`；`.github/workflows/scripts/create-release-packages.sh::generate_commands()` 以同样规则生成 release 压缩包中的命令文件；`install_ai_skills()` 又把这些命令名归一化后写成 `speckit-<command>` 技能目录；测试文件 `tests/test_speckit_commands.py`、`tests/test_ai_skills.py`、`tests/test_init_agents.py`、`tests/test_cline_agent.py`、`tests/test_extensions.py` 均对该前缀有硬编码断言；README 和 CLI Next Steps/Enhancement Commands 也向用户展示 `/speckit.*`。因此必须按“模板源头 → 生成逻辑 → 打包逻辑 → skills/扩展 → 测试 → 文档”的顺序整体切换，才能避免出现源码已改但产物、测试或文档仍残留旧前缀的半迁移状态。

[Types]
本次改动不引入新的 Python 类型系统对象，但需要统一一组与命名规则相关的逻辑常量与字符串约束，使各层围绕同一前缀工作。

建议引入或统一以下逻辑数据约束：

1. `COMMAND_PREFIX: str = "sdd"`
   - 作用：作为命令文件名、slash command 展示文本、skills 名称前缀、扩展命名规则的唯一前缀值。
   - 约束：不得再散落硬编码 `"speckit"` 作为对外命令前缀。

2. `GeneratedCommandFilename`
   - 逻辑格式：`sdd.<command>.<ext>`
   - 示例：
     - Markdown agent: `sdd.specify.md`
     - TOML agent: `sdd.plan.toml`
     - Cline prompt: `sdd.tasks.prompt.md`
     - Copilot agent: `sdd.implement.agent.md`
   - 校验规则：
     - `command` 必须来自 `templates/commands/*.md` 的 stem
     - 扩展名继续由各 agent 的 `output_extension` 决定

3. `GeneratedSkillName`
   - 逻辑格式：`sdd-<command>`
   - 示例：`sdd-specify`、`sdd-plan`
   - 校验规则：
     - skills 安装逻辑必须剥离 `sdd.` 文件名前缀后再生成 skill 名
     - metadata.source 仍指向 `templates/commands/<command>.md`

4. `ExtensionCommandNamePattern`
   - 当前模式：`speckit.{extension}.{command}`
   - 新模式：`sdd.{extension}.{command}`
   - 校验规则：
     - 扩展 manifest 中 command `name` 与 `aliases` 应匹配新前缀
     - 若仍检测到 `speckit.`，视为无效扩展命令命名

5. `DisplayedSlashCommand`
   - 逻辑格式：`/sdd.<command>`
   - 用途：README、CLI init 后提示、模板正文中的下游 handoff、使用示例、架构文档
   - 约束：用户文档中不得继续把 `/speckit.*` 作为推荐命令

[Files]
本次修改主要涉及模板源文件、命令生成实现、release 构建脚本、extensions 命名校验、测试与文档；不需要新增生产代码目录结构，但需要系统性修改现有文件。

详细变更如下：

- 现有文件修改
  - `src/specify_cli/__init__.py`
    - 将 `_generate_commands_for_agent()` 中输出文件名从 `speckit.*` 改为 `sdd.*`
    - 将 skills 安装逻辑中 `speckit.` 剥离和 `speckit-` skill name 改为 `sdd.` / `sdd-`
    - 更新 `init()` 末尾展示给用户的 `/speckit.*` 命令为 `/sdd.*`
    - 检查帮助文本、示例说明、security/context 提示中是否存在旧前缀残留
  - `.github/workflows/scripts/create-release-packages.sh`
    - `generate_commands()` 输出文件名从 `speckit.$name.*` 改为 `sdd.$name.*`
    - `generate_copilot_prompts()` 的 glob 从 `speckit.*.agent.md` 改为 `sdd.*.agent.md`
  - `src/specify_cli/extensions.py`
    - 扩展命令名校验规则从 `speckit.{extension}.{command}` 改为 `sdd.{extension}.{command}`
    - 若有 alias/registered command 相关文案，也需同步改为 `sdd`
  - `templates/commands/analyze.md`
  - `templates/commands/checklist.md`
  - `templates/commands/clarify.md`
  - `templates/commands/constitution.md`
  - `templates/commands/design.md`
  - `templates/commands/implement.md`
  - `templates/commands/plan.md`
  - `templates/commands/prd2spec.md`
  - `templates/commands/preview.md`
  - `templates/commands/specify.md`
  - `templates/commands/tasks.md`
  - `templates/commands/taskstoissues.md`
    - 将正文、Usage、handoff、下游命令、说明文字中的 `/speckit.*`、`speckit.*` 全部替换为 `/sdd.*`、`sdd.*`
    - 保持命令语义不变，仅改变前缀与相关示例
  - `README.md`
    - 快速开始、Available Slash Commands、Detailed Process、示例命令全部切换到 `/sdd.*`
    - 如仍有 “The `/speckit.*` commands are available” 类表述需统一改写
  - `docs/quickstart.md`
  - `docs/index.md`
  - `docs/README.md`
  - `docs/installation.md`
  - `docs/upgrade.md`
  - `spec-driven.md`
    - 搜索并更新用户可见的旧前缀引用
  - `tests/test_speckit_commands.py`
    - 文件内容中的 `/speckit.*` 断言与说明更新为 `/sdd.*`
    - 视需要重命名测试文件本身为 `tests/test_sdd_commands.py`
  - `tests/test_ai_skills.py`
    - `speckit.*` 文件夹/文件名、`speckit-*` skill 名、frontmatter 中 `agent: speckit.plan` 等断言改为 `sdd.*` / `sdd-*`
  - `tests/test_init_agents.py`
    - 初始化后生成的命令文件断言改为 `sdd.*`
  - `tests/test_cline_agent.py`
    - `.cline/workflows/sdd.*.prompt.md` 断言替换
  - `tests/test_extensions.py`
    - 扩展命令名、alias、输出文件名、校验规则样例全部从 `speckit.*` 切换为 `sdd.*`
  - `tests/test_agent_consistency.py`
    - 若测试中校验生成产物命名前缀，也需同步替换
  - `CHANGELOG.md`
    - 记录 breaking change：slash commands / skills 前缀由 `speckit` 改为 `sdd`
  - `pyproject.toml`
    - 如果本次修改触及 `src/specify_cli/__init__.py` 的对外行为，按仓库 AGENTS.md 要求递增版本号

- 可选文件重命名
  - `tests/test_speckit_commands.py` -> `tests/test_sdd_commands.py`
    - 目的：避免测试文件名和语义长期保留旧品牌词
    - 需要同步 pytest 自动发现与引用（通常无需额外配置）

- 不建议修改/删除
  - `src/specify_cli/agent_registry.py`
    - agent 元数据与目录结构无须因命令前缀变化而改变
  - `scripts/bash/update-agent-context.sh`
  - `scripts/powershell/update-agent-context.ps1`
    - 这些脚本主要处理上下文文件，不直接生成 slash command 文件名；仅在用户文案残留时再局部调整

[Functions]
本次实现重点是修改现有命令生成和命名归一化函数，不需要增加复杂新函数，但建议抽出统一前缀常量以减少再次散落硬编码。

详细函数修改建议如下：

1. 修改函数：`_generate_commands_for_agent()`
   - 文件：`src/specify_cli/__init__.py`
   - 当前行为：输出 `speckit.{name}.toml/.prompt.md/.agent.md/.md`
   - 需要改为：输出 `sdd.{name}.toml/.prompt.md/.agent.md/.md`
   - 影响：本地 `specify init` 生成的所有 agent 命令文件名

2. 修改函数：`install_ai_skills()`
   - 文件：`src/specify_cli/__init__.py`
   - 当前行为：
     - 识别 `speckit.` 前缀文件
     - 生成 `speckit-<command>` skill 目录
     - 生成 `# Speckit <Command> Skill` 标题
   - 需要改为：
     - 识别 `sdd.` 前缀文件
     - 生成 `sdd-<command>` skill 目录
     - 生成 `# Sdd <Command> Skill` 或更自然的 `# SDD <Command> Skill` 标题
   - 注意：若模板目录 fallback 仍读到旧命令名，需统一归一到新前缀，不做旧前缀兼容

3. 修改函数：CLI `init()` 尾部的 next steps / enhancement command 渲染逻辑
   - 文件：`src/specify_cli/__init__.py`
   - 当前行为：输出 `/speckit.constitution` 等
   - 需要改为：输出 `/sdd.constitution` 等

4. 修改函数：`generate_commands()`
   - 文件：`.github/workflows/scripts/create-release-packages.sh`
   - 当前行为：release 包内输出 `speckit.$name.$ext`
   - 需要改为：`sdd.$name.$ext`

5. 修改函数：`generate_copilot_prompts()`
   - 文件：`.github/workflows/scripts/create-release-packages.sh`
   - 当前行为：遍历 `speckit.*.agent.md`
   - 需要改为：遍历 `sdd.*.agent.md`

6. 修改函数：扩展命令校验/注册相关函数
   - 文件：`src/specify_cli/extensions.py`
   - 重点函数：
     - `ExtensionManifest._validate()` 中对 command name 的正则/提示
     - `CommandRegistrar.register_commands_for_agent()` / 相关注册逻辑（如包含前缀假设）
   - 需要改为：要求 `sdd.{extension}.{command}` 命名

7. 可新增常量：`COMMAND_PREFIX = "sdd"`
   - 文件：`src/specify_cli/__init__.py`（必要时 `extensions.py` 也声明或复用）
   - 目的：减少后续再次出现硬编码 `speckit`/`sdd`

[Classes]
本次修改不新增生产类，也不需要改变现有类继承结构；主要需要扩展现有 pytest 测试类中的断言目标，使其围绕 `sdd` 前缀工作。

具体影响如下：

- 修改测试类
  - `TestPrd2Spec` in `tests/test_speckit_commands.py`
    - 下游 handoff 断言由 `speckit.plan` 改为 `sdd.plan`
  - `TestSpecifyCommand`
    - handoffs 与命令示例断言改为 `sdd.plan`
  - `TestPlanCommand`
    - usage 断言从 `/speckit.plan <spec.md>` 改为 `/sdd.plan <spec.md>`
  - `TestDesignCommand`
    - usage 断言从 `/speckit.design <spec.md>` 改为 `/sdd.design <spec.md>`
  - `TestTasksCommand`
    - usage 断言从 `/speckit.tasks <plan.md>` 改为 `/sdd.tasks <plan.md>`
  - `TestAnalyzeCommand`
    - usage 断言从 `/speckit.analyze <plan.md|tasks.md>` 改为 `/sdd.analyze <plan.md|tasks.md>`
  - `TestPreviewCommand`
    - 如有命令文字引用，也同步改为 `sdd`

- `tests/test_ai_skills.py` 中的类
  - `TestInstallAiSkills`
    - 目录名与 skill 名期望值改为 `sdd-specify`、`sdd-plan`、`sdd-tasks`
  - `TestCommandCoexistence`
    - 命令文件名改为 `sdd.*`
  - `TestNewProjectCommandSkip`
    - fake extract 的文件名改为 `sdd.specify.md`

- 不需要修改的核心类
  - `AgentMeta`, `StepTracker`, `BannerGroup`, `ExtensionRegistry`, `ExtensionManager`, `CommandRegistrar` 的结构可保持不变
  - 仅在其内部字符串规则涉及旧前缀时做局部修改

[Dependencies]
本次改动不需要新增第三方依赖，现有 Python、pytest、shell 工具链已足够覆盖实现与验证。

依赖层的唯一变化是版本发布语义：

- `pyproject.toml`
  - 需要递增版本号（因为 `src/specify_cli/__init__.py` 对外行为变化，且 AGENTS.md 明确要求）
- `CHANGELOG.md`
  - 记录 breaking change / command prefix rename

无需新增 npm、pip、系统命令或其他测试依赖。

[Testing]
测试重点是证明“模板 → 本地生成 → release 打包 → skills → 扩展 → 文档”链路已全部切换到 `sdd`，且没有旧前缀残留造成回归。

建议测试策略如下：

1. 模板与命令文本测试
   - 更新 `tests/test_speckit_commands.py`（或重命名后文件）
   - 断言所有 usage、handoff、文案示例都使用 `/sdd.*`
   - 断言不再要求 `/speckit.*`

2. skills 安装测试
   - 更新 `tests/test_ai_skills.py`
   - 验证：
     - skills 目录名为 `sdd-*`
     - 命令文件名为 `sdd.*`
     - frontmatter 中 `agent: sdd.plan`
     - fallback/skip/cleanup 场景仍成立

3. agent 初始化产物测试
   - 更新 `tests/test_init_agents.py`、`tests/test_cline_agent.py`
   - 验证初始化后各 agent 输出的是 `sdd.*.md/.toml/.prompt.md/.agent.md`

4. extension 命名规则测试
   - 更新 `tests/test_extensions.py`
   - 验证：
     - `sdd.test.hello` 合法
     - `speckit.test.hello` 不再作为合法模式
     - alias 和注册文件名同步为 `sdd.*`

5. 一致性与回归测试
   - 运行现有 pytest 全量测试，至少覆盖：
     - `tests/test_speckit_commands.py` / `tests/test_sdd_commands.py`
     - `tests/test_ai_skills.py`
     - `tests/test_init_agents.py`
     - `tests/test_cline_agent.py`
     - `tests/test_extensions.py`
     - `tests/test_agent_consistency.py`
   - 增加一次全文搜索，确认仓库主干可交付文件中不再残留对外旧前缀（允许 changelog 或历史分析文档按上下文保留说明）

6. 构建验证
   - 运行 release 打包脚本或最小化等价验证
   - 检查生成包中的命令文件实际前缀为 `sdd.`

[Implementation Order]
实施顺序应先改命令生成 SSOT，再改模板与测试，最后收口文档和版本信息，以降低中间态冲突风险。

1. 在 `src/specify_cli/__init__.py` 中引入统一前缀常量并修改 `_generate_commands_for_agent()`、`install_ai_skills()`、CLI 展示文案。
2. 在 `.github/workflows/scripts/create-release-packages.sh` 中同步修改 release 产物文件名前缀和 Copilot prompt glob。
3. 在 `src/specify_cli/extensions.py` 中把扩展命名校验规则切换到 `sdd.{extension}.{command}`。
4. 批量更新 `templates/commands/*.md` 中所有 `/speckit.*`、`speckit.*` 引用为 `sdd` 前缀。
5. 更新 `tests/test_speckit_commands.py`、`tests/test_ai_skills.py`、`tests/test_init_agents.py`、`tests/test_cline_agent.py`、`tests/test_extensions.py` 等硬编码断言；必要时重命名测试文件。
6. 更新 `README.md`、`spec-driven.md`、docs 目录中的用户示例与命令说明，保证对外文档一致。
7. 更新 `pyproject.toml` 版本号与 `CHANGELOG.md` 记录，满足仓库变更规则。
8. 运行构建/测试验证，重点检查生成文件名、skills 名、扩展校验与 README 示例是否全部变为 `sdd`。
9. 在 Act mode 中按最小必要文件集执行修改并回归验证，确认无旧前缀残留后提交结果。