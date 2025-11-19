# AutoReport Optimization Plan

## 1. Goals & Scope
- Shorten end-to-end report generation time without sacrificing accuracy or formatting.
- Reduce maintenance overhead via clearer module boundaries and observability.
- Cover every major subsystem: resource handling, data ingestion/standardization, modeling, map generation, document assembly, infra/tooling.

## 2. Resource Download & Management (`src/autoreport/processor/downloader.py`, `resource_manager.py`, `pipelines/resource_handler.py`)
| Task | Why | Acceptance |
| --- | --- | --- |
| Centralize retry/backoff policy per resource type | Current downloader duplicates retry logic across handlers | Single config-driven retry/backoff used by both streaming & file downloads |
| Hash-based cache validation | Avoid re-downloading identical satellite/logo files when hash unchanged | Downloader logs cache hit/miss and skips download if hash matches |
| Parallel-but-bounded downloads | Thread pool currently unbounded by resource size | Introduce semaphore (config) and log queue depth |

## 3. Data Pipeline & Standardization (`processor/data/*.py`, `pipelines/data_pipeline.py`)
1. **Refactor stage graph**: make extraction → matcher → standardizer explicit objects with typed outputs; today `DataPipeline` mixes IO, validation, state.
2. **Schema validation**: define pydantic models for UAV & lab datasets to catch column drift.
3. **Incremental processing**: cache intermediate parquet files keyed by mission id to skip repeated cleaning runs.
4. **Unit test harness**: add fixtures hitting `matcher.py`, `standardizer.py` to lock regression.

## 4. Modeling Layer (`processor/model_gateway.py`, `processor/data/processor.py`)
- Abstract model invocation so new engines (local, remote) share a `ModelGateway` interface.
- Log feature vectors and outputs with redaction to aid debugging.
- Add benchmark CLI (`python -m autoreport.tools.benchmark_model`) to profile latency per indicator.

## 5. Map Generation (`processor/maps/*`)
- **Current status**: geometry caching + KML cache done (see `docs/map_optimization_plan.md`).
- **Next work**: per plan section – profiling hooks, faster Alpha Shape, normalized color scales, optional parallel rendering, persisted geometry cache.

## 6. Document Assembly (`generator/`, `document/`)
| Area | Improvement |
| --- | --- |
| Template engine | migrate scattered string formatting to Jinja2 templates with include/extends |
| Asset embedding | ensure map/image insertion handles relative paths + fallback text |
| Pagination controls | centralize page breaks and section numbering rules |
| Test coverage | golden-file tests comparing generated docx/pdf metadata |

## 7. Configuration & Validation (`config_validator.py`, `config/*.py`)
- Build layered config (default → customer override → CLI flags).
- Provide schema docs and auto-generated sample config.
- Improve validator logging to list required/optional fields, not only raw warnings.

## 8. Observability & Tooling
1. **Structured logging**: adopt JSON logs (flag-controlled) for key pipelines.
2. **Metrics hooks**: optional Prometheus or simple CSV to track runtime per stage.
3. **CLI UX**: add `--dry-run` & `--profile` modes to skip heavy work or emit timing.

## 9. Refactoring Candidates
- **Pipelines vs Processor duplication**: unify `pipelines/data_pipeline.py` and legacy `processor/data/processor.py` responsibilities.
- **Map generator packaging**: keep `processor/maps/__init__.py` as façade; document that `maps.py` legacy path is deprecated.
- **Error handling**: replace try/except logging chains with `safe_operation` decorator usage in downloader/model sections for consistency.

## 10. Next Steps
1. Implement profiling hooks (maps + pipeline) & structured logging.
2. Stand up schema validation tests for data ingestion.
3. Kick off template refactor for document generator with Jinja2 prototype.
4. Decide on roadmap owners & integrate tasks into issue tracker.

