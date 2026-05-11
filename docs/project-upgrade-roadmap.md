# 毕设项目工程化升级路线图

## 1. 当前项目总览（As-Is）

### 1.1 现有能力
- 前端：Vue 3 单页上传界面，支持上传音频、展示预测结果、查询历史。
- 后端：Flask 提供 `/upload` 与 `/history` 接口，调用特征提取与模型推理。
- 模型：已训练并保存多个模型（LR/MBSGD/RF/SVM/KNN）到 `results/`。
- 数据：本地数据集 + 特征 CSV + 训练脚本。
- 数据库：SQLite（`history.db`）记录姓名、时间、预测结果。

### 1.2 主要现状特征
- 代码以“可运行原型”为主，尚未拆分为清晰的工程分层。
- 训练、推理、Web 服务强耦合在同一仓库根目录。
- 配置与路径存在硬编码，跨机器/跨系统迁移成本高。
- 缺少标准化工程资产（依赖管理分层、自动化测试、CI/CD、容器化、迁移脚本等）。

## 2. 与生产级项目的差距（Gap）

## 2.1 架构与代码组织
- 业务逻辑集中在单文件 `backend/app/app.py`，缺少模块边界（API/Service/Repository/Domain）。
- 训练代码、推理代码、数据处理代码复用边界不清晰，容易“改一处坏一片”。
- 缺少统一异常处理、日志、请求追踪、配置管理。

## 2.2 配置与环境
- 绝对路径硬编码（如 `/mnt/d/...`）导致不可移植。
- 前端 API 地址硬编码（`127.0.0.1:5000`），缺少环境区分（dev/test/prod）。
- 依赖文件不完整：后端缺少精简可复现的 Python requirements/pyproject。

## 2.3 数据库与数据治理
- 仅有 SQLite + 自动建表，缺少迁移体系（Alembic/Flyway 类）。
- 缺少实体约束与索引设计（例如上传历史按用户/时间检索优化）。
- 数据生命周期策略缺失（上传文件、中间特征、结果归档）。

## 2.4 测试与质量
- 缺少单元测试、接口测试、端到端测试分层。
- 缺少静态检查/格式化/lint 钩子与 CI 检查。
- 模型推理稳定性、异常输入与边界输入覆盖不足。

## 2.5 运维与部署
- 未容器化，部署流程依赖手工环境。
- 缺少可观测性（结构化日志、指标、健康检查）。
- 缺少性能优化基线（耗时、吞吐、并发、资源占用）。

## 3. 升级目标项目结构（To-Be）

```text
project/
  apps/
    api/                      # 后端服务（Flask/FastAPI 二选一）
      src/
        api/                  # 路由层
        services/             # 业务服务层
        repositories/         # 数据访问层
        domain/               # 领域模型/DTO
        ml/
          inference/          # 模型加载与推理
          feature_pipeline/   # 特征提取流水线
        core/
          config.py
          logging.py
          exceptions.py
        db/
          models/
          migrations/         # Alembic
      tests/
        unit/
        integration/
      pyproject.toml
    web/
      src/
        pages/
        components/
        api/                  # axios/fetch 封装
        stores/
      tests/
      package.json
  ml/
    training/                 # 训练脚本与可复现实验
    evaluation/
    model_registry/           # 可先本地目录，后续可接 MLflow
  data/
    raw/
    interim/
    processed/
  scripts/
    dev/
    release/
  infra/
    docker/
      api.Dockerfile
      web.Dockerfile
    compose/
      docker-compose.dev.yml
  docs/
    architecture.md
    api-spec.md
    project-upgrade-roadmap.md
  .github/
    workflows/
      ci.yml
  .env.example
  Makefile
  README.md
```

## 4. 推荐技术栈（练习“贴近生产”）

### 4.1 后端
- Python 3.11+
- FastAPI（优先）或保留 Flask 逐步改造
- SQLAlchemy + Alembic
- Pydantic（请求/响应与配置校验）
- pytest + httpx + pytest-cov

### 4.2 前端
- Vue 3 + Vite（替代 Vue CLI，构建更快）
- Pinia（状态管理）
- Axios 封装 + 环境变量（`VITE_API_BASE_URL`）
- Vitest + Playwright（单测 + E2E）

### 4.3 数据库
- 开发期 SQLite；进阶练习切换 PostgreSQL
- 迁移脚本 + 索引 + 约束 + 审计字段（created_at/updated_at）

### 4.4 工程化
- pre-commit（black/isort/ruff/eslint）
- GitHub Actions（lint + test + build）
- Docker + Compose（本地一键启动）

## 5. 学习与实施路线（按阶段推进）

## Phase 0：基线整理（1-2 周）
- 整理目录：把训练代码、服务代码、前端代码解耦。
- 清理硬编码路径，改为 `.env` + 配置类。
- 建立最小 README（启动、依赖、目录说明）。

## Phase 1：后端工程化（2-3 周）
- 拆分 API/Service/Repository。
- 引入 Pydantic DTO、统一异常处理、中间件日志。
- 增加健康检查、版本接口、请求 ID。

## Phase 2：数据库升级（1-2 周）
- 引入 Alembic 迁移。
- 设计表结构与索引（history 按 `user_name/upload_time`）。
- 增加基础 CRUD 与分页查询。

## Phase 3：测试体系（2 周）
- 单元测试覆盖特征处理、推理流程关键路径。
- 集成测试覆盖上传/历史接口。
- E2E 测试覆盖上传到结果展示完整链路。

## Phase 4：性能与可观测性（2 周）
- 增加性能基线（接口延迟、吞吐）。
- 推理缓存/模型单例加载/异步任务队列（可选 Celery）。
- 结构化日志 + 错误告警入口。

## Phase 5：部署与协作（1-2 周）
- Docker 化 + Compose 本地编排。
- CI 自动化（PR 必过 lint/test）。
- 版本策略与发布说明（SemVer + CHANGELOG）。

## 6. Git 能力训练清单（强关联生产）

- 分支策略：`main` + `dev` + `feature/*` + `fix/*`
- Commit 规范：Conventional Commits（`feat:`, `fix:`, `refactor:`）
- PR 模板：背景、改动、测试、风险、回滚方案
- 常用能力：
  - `git rebase` 整理提交
  - `git cherry-pick` 精准摘取
  - `git bisect` 定位回归
  - `git stash` 临时存档
  - `git tag` 版本发布

## 7. 第一批可执行改造任务（建议先做）

- [ ] 新建 `apps/api`，迁移 `backend/app/app.py` 成模块化结构
- [ ] 新建 `apps/web`（或迁移现有 `frontend`），接入环境变量 API 地址
- [ ] 新建 `.env.example`，移除硬编码绝对路径
- [ ] 新建 `requirements.txt`/`pyproject.toml`（后端）
- [ ] 增加 `pytest` 的 3 个最小测试（健康检查、上传参数校验、历史查询）
- [ ] 引入 Alembic 并生成首个迁移脚本
- [ ] 新建 `docker-compose.dev.yml`（api + web + db）

## 8. 结果验收标准（你可以用来做阶段复盘）

- 本地一条命令启动：前后端 + 数据库可用
- 新人按 README 可在 30 分钟内跑通
- PR 自动执行 lint + test 并产出报告
- 上传接口有明确错误码、日志和可追踪请求 ID
- 从 SQLite 切到 PostgreSQL 不改业务层代码

