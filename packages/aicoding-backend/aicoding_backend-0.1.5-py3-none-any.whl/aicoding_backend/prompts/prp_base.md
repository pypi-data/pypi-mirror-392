名称: "基础 PRP 模板 v2 - 上下文丰富且带验证循环"
描述: |

## 目的
该模板专为 AI 代理优化，使其能够通过充分的上下文和自我验证能力，通过迭代改进实现可工作的代码。

## 核心原则
1. **上下文为王**: 包含所有必要的文档、示例和注意事项
2. **验证循环**: 提供 AI 可运行和修复的可执行测试/检查
3. **信息密集**: 使用代码库中的关键词和模式
4. **渐进式成功**: 从简单开始，验证后再增强
5. **全局规则**: 确保遵循 CLAUDE.md 中的所有规则

---

## 目标
[需要构建什么 - 明确说明最终状态和期望]

## 为什么
- [业务价值和用户影响]
- [与现有功能的集成]
- [解决的问题以及为谁解决]

## 什么
[用户可见的行为和技术需求]

### 成功标准
- [ ] [具体的可衡量结果]

## 所有必需的上下文

### 文档和参考资料（列出实现功能所需的所有上下文）
```yaml
# 必读 - 将这些包含在您的上下文窗口中
- url: [官方 API 文档 URL]
  why: [您需要的具体章节/方法]
  
- file: [path/to/example.java]
  why: [要遵循的模式，要避免的陷阱]
  
- doc: [库文档 URL] 
  section: [关于常见陷阱的具体章节]
  critical: [防止常见错误的关键见解]

- docfile: [PRPs/ai_docs/file.md]
  why: [用户粘贴到项目中的文档]

```

### 当前代码库结构（在项目根目录运行 `tree` 命令）以获取代码库概览
```bash

```

### 期望的代码库结构（包含要添加的文件及文件职责）
```bash

```

### 已知的代码库陷阱和库怪癖
```typescript
// 关键: [库名称] 需要 [特定设置]
// 示例: React 组件需要使用 PascalCase 命名
// 示例: Vue 3 组合式 API 需要正确的响应式引用
// 示例: 我们使用 TypeScript 严格模式
```

## 实施蓝图

### 数据模型和结构

创建核心数据模型，确保类型安全和一致性。
```typescript
示例: 
 - 接口定义
 - 类型别名
 - Zod 验证模式
 - 枚举类型
```

### 按顺序完成 PRP 所需完成的任务列表

```yaml
任务 1:
修改 jd.gms.item.site.web/src/main/java/jd/gms/item/site/controller/task/TaskControllerNew.java:
  - 在addTaskV2方法中，submitTaskService.submitTask4File调用成功后
  - 添加缓存记录逻辑：RedisCacheUtil.hIncrBy("task:usage:stat:" + getUserCodeLowerCase(), type, 1L)
  - 添加try-catch块确保缓存失败不影响主流程
  - 添加适当的日志记录

任务 N:
...

```

### 每个任务所需的伪代码（根据需要添加到每个任务）
```java

// 任务 1 - 修改addTaskV2方法
public SiteResult addTaskV2(...) {
    // ... 现有代码 ...
    
    TaskResult taskResult = submitTaskService.submitTask4File(...);
    
    // 新增：记录任务使用统计
    try {
        if (taskResult.isSuccess()) {
            taskUsageStatService.recordTaskUsage(getUserCodeLowerCase(), type);
        }
    } catch (Exception e) {
        log.warn("记录任务使用统计失败，不影响主流程, erp={}, type={}", getUserCodeLowerCase(), type, e);
    }
    
    // ... 现有代码 ...
}
```

### 集成点
```yaml
缓存配置:
  - 使用现有RedisCacheUtil工具类
  - 缓存过期时间：30天
  - key命名规范：task:usage:stat:{erp}
  
依赖注入:
  - 在TaskControllerNew中添加TaskUsageStatService注入
  - 使用现有@Autowired注解模式
  
接口规范:
  - 查询接口：GET /new/task/getUsageStat?erp={erp}
  - 返回格式：SiteResult<TaskUsageStatDTO>
```

## 验证循环

### 级别 1: 语法和样式
```bash
# 编译检查
mvn compile -pl [本次生成、修改的代码文件]
# 预期: 无编译错误
```

### 级别 2: 单元测试（每个新功能/文件/函数使用现有测试模式）
```java
// 创建 TaskUsageStatServiceTest.java
@Test
public void testRecordTaskUsage() {
    // 测试记录功能
    taskUsageStatService.recordTaskUsage("testErp", "1");
    
    // 验证记录结果
    TaskUsageStatDTO stat = taskUsageStatService.getTaskUsageStat("testErp");
    assertEquals(1L, stat.getTypeCount().get("1").longValue());
}

@Test
public void testGetTaskUsageStat() {
    // 测试查询功能
    taskUsageStatService.recordTaskUsage("testErp", "1");
    taskUsageStatService.recordTaskUsage("testErp", "2");
    
    TaskUsageStatDTO stat = taskUsageStatService.getTaskUsageStat("testErp");
    assertNotNull(stat);
    assertEquals("testErp", stat.getErp());
    assertEquals(2, stat.getTypeCount().size());
}
```

```bash
# 运行并迭代直到通过:
mvn test -Dtest=NewFeatureTest
# 如果失败: 阅读错误，理解根本原因，修复代码，重新运行（永远不要通过 mock 来通过测试）
```

### 级别 3: 集成测试
```bash
# 启动服务后测试
curl -X POST "http://localhost:8080/new/task/addtaskV2" \
  -F "type=1" \
  -F "upload=@test.xlsx"

# 然后查询统计
curl "http://localhost:8080/new/task/getUsageStat?erp=testuser"
# 预期返回: {"success":true,"data":{"erp":"testuser","typeCount":{"1":1}}}
```

## 最终验证清单
- [ ] 所有测试通过
- [ ] 无 lint 错误
- [ ] 无类型错误
- [ ] 手动测试成功: [具体的 curl/命令]
- [ ] 错误情况得到优雅处理
- [ ] 日志信息丰富但不冗长
- [ ] 文档已更新（如需要）

---

## 要避免的反模式
- ❌ 当现有模式有效时不要创建新模式
- ❌ 不要因为"应该可以工作"而跳过验证
- ❌ 不要忽略失败的测试 - 修复它们
- ❌ 不要在异步上下文中使用同步函数
- ❌ 不要硬编码应该是配置的值
- ❌ 不要捕获所有异常 - 要具体
