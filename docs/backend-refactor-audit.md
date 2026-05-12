# 后端改造标注清单（2026-05-11）

本文用于第一阶段重构前的“定位+建议”。  
优先级定义：
- `P0`：必须先改，不改会影响可运行性/可迁移性/稳定性。
- `P1`：建议尽快改，关系到维护成本和协作效率。
- `P2`：可后续迭代，关系到性能与工程质量上限。

## 1. 后端 API 主文件（最高优先）

文件：[backend/app/app.py](/D:/大学材料/毕设/project/backend/app/app.py)

| 优先级 | 位置 | 问题标注 | 修改建议 |
|---|---|---|---|
| P0 | `:23`, `:27`, `:98-102` | 使用绝对路径 `/mnt/d/...` 加载特征与模型，跨机器不可移植 | 用 `pathlib + 项目根目录 + 环境变量` 组织路径；通过 `.env` 配置 `MODEL_DIR`、`ARTIFACT_DIR` |
| P0 | `:89-104` | 模型与预处理资源在模块导入时立即加载，启动即重负载，不利于测试与容错 | 改为“应用启动钩子”或“懒加载单例”，并在加载失败时给出明确日志/错误码 |
| P0 | `:121-165` | 上传接口未覆盖关键错误分支（非法扩展名时无返回；`userName` 缺失会 KeyError） | 增加参数校验和统一错误响应：400（参数问题）/415（文件类型）/500（服务异常） |
| P0 | `:161-164` | `finally` 中直接删除文件，若文件不存在会抛异常，掩盖原始错误 | 删除前判断 `os.path.exists`，并捕获清理阶段异常写日志 |
| P0 | `:91` | 数据库 URL 固定写死为 sqlite，环境不可切换 | 改为 `SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///...")` |
| P0 | `:117-118` | `db.create_all()` 直接在运行时建表，不可追踪 schema 变更 | 引入 Alembic 迁移；运行时移除 `create_all()` |
| P1 | `:14-18`, `:44-86`, `:121-178` | 路由、业务、数据访问、模型推理混在单文件 | 拆分为 `api/routes.py`、`services/predict_service.py`、`repositories/history_repo.py` |
| P1 | `:90` | `CORS(app)` 全开，生产风险高 | 限制来源为环境变量白名单（dev/prod 分离） |
| P1 | `:66-86` | 投票逻辑依赖 `model==model2` 的对象比较，语义脆弱 | 用模型名称/配置驱动（如 `{"name":"mbsgd","needs_batch2":true}`） |
| P1 | `:77` | `pred.drop_duplicates()` 假设 `pred` 是带该方法的对象，兼容性差 | 统一将预测结果转为 `numpy/list` 后处理 |
| P1 | `:168-178` | `/history` 全量查询无分页，数据量大后会慢 | 增加分页参数 `page/page_size` 并默认排序 |
| P2 | `:10`, `:129`, `:173` | 时间使用与时区策略不统一（`now` 与 `utcnow` 混用） | 统一使用 UTC 存储，返回时格式化时区 |
| P2 | 全文件 | 中文注释出现乱码 | 统一文件编码为 UTF-8，修复乱码文案 |

## 2. 前后端联调耦合点（后端改造时必须一起处理）

文件：[frontend/src/components/File_Upload.vue](/D:/大学材料/毕设/project/frontend/src/components/File_Upload.vue)

| 优先级 | 位置 | 问题标注 | 修改建议 |
|---|---|---|---|
| P0 | `:48`, `:61` | 前端写死 `http://127.0.0.1:5000` | 改为环境变量（如 `VUE_APP_API_BASE_URL` 或迁移 Vite 的 `VITE_API_BASE_URL`） |
| P1 | `:56-57`, `:65-66` | 仅控制台报错，无用户可见错误状态 | 增加错误提示与 loading 状态，便于接口调试 |
| P1 | `:45-46` | 上传前未校验 `selectedFile/userName` | 在前端先行校验，减少无效请求 |

## 3. 推理/特征脚本（与后端共享逻辑，需并行改）

文件：[Get_Feature.py](/D:/大学材料/毕设/project/Get_Feature.py)

| 优先级 | 位置 | 问题标注 | 修改建议 |
|---|---|---|---|
| P0 | `:10`, `:86` | `KALDI_ROOT` 硬编码 Linux 路径 | 改为可选环境变量，不在代码中写死 |
| P1 | `:67-74` | 特征合并与后端实现重复，容易漂移 | 抽成共享模块 `ml/feature_pipeline`，服务与脚本共用 |
| P2 | 全文件 | 与服务代码混放在仓库根目录 | 迁到 `ml/training` 或 `apps/api/src/ml` |

文件：[test/test2.py](/D:/大学材料/毕设/project/test/test2.py)

| 优先级 | 位置 | 问题标注 | 修改建议 |
|---|---|---|---|
| P1 | `:10`, `:14`, `:78-82` | 绝对路径硬编码，且与 API 逻辑高度重复 | 改为调用服务层函数或统一配置模块，不复制业务逻辑 |
| P1 | `:72` | 目录脚本式遍历，不是自动化测试 | 改造成 `pytest` 测试用例，纳入 CI |

## 4. 训练与产物管理（后端上线稳定性的前提）

文件：[utils_data_preprocessing.py](/D:/大学材料/毕设/project/utils_data_preprocessing.py)

| 优先级 | 位置 | 问题标注 | 修改建议 |
|---|---|---|---|
| P1 | `:41`, `:52` | 训练产物写入固定相对路径 `results/` | 定义统一产物目录（环境变量/配置），并记录模型版本 |
| P1 | `:16-26` | 训练数据字段强依赖 `ifPD`，缺 schema 校验 | 加入输入 schema 校验与失败提示 |

## 5. 依赖与项目边界（影响后端可复现）

文件：[package.json](/D:/大学材料/毕设/project/package.json) 与 [frontend/package.json](/D:/大学材料/毕设/project/frontend/package.json)

| 优先级 | 位置 | 问题标注 | 修改建议 |
|---|---|---|---|
| P1 | 根目录 `package.json:2-4` | `axios` 装在根目录，前端依赖边界混乱 | 将前端依赖全部收敛到 `frontend/package.json` |

## 6. 建议的改造执行顺序（对应 feature 分支）

1. `feature/config-env`  
目标：清理全部硬编码路径、数据库 URL、前端 API 地址。

2. `feature/backend-structure`  
目标：拆分 `app.py` 为路由/服务/仓储/配置模块。

3. `feature/error-handling-validation`  
目标：统一错误处理、请求参数校验、上传清理安全。

4. `feature/db-migration`  
目标：引入 Alembic，移除 `create_all()`，实现可迁移 schema。

5. `feature/test-foundation`  
目标：为上传与历史接口建立 pytest 集成测试。

## 7. 第一批“必须改”的最小闭环（建议本周完成）

- [ ] `app.py` 中所有 `/mnt/d/...` 改为配置路径
- [ ] 前端 API 地址改环境变量
- [ ] `/upload` 增加参数校验和错误码
- [ ] 文件删除做存在性判断
- [ ] 移除运行时 `db.create_all()`，准备迁移工具

