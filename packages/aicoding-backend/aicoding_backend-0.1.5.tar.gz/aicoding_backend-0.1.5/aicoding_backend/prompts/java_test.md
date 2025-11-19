# Java测试代码生成提示词
## 项目环境信息
- 项目框架：[PROJECT_FRAMEWORK] (Tomcat + SpringMVC / Spring Boot / Spring Cloud等)
- 测试类型：[TEST_TYPE] (unit / integration / e2e)
- 目标类：[TARGET_CLASS]
- 目标包路径：[TARGET_PACKAGE]
- 架构层级：[LAYER] (controller / service / dao / util / config)
- 业务域：[BUSINESS_DOMAIN] (用户管理 / 订单处理 / 支付系统等)
## 技术栈配置
### 核心测试框架
- JUnit 5 - 主测试框架
- Mockito 4.x - Mock框架，支持静态方法和final类
- AssertJ 3.x - 流式断言库
- Spring Test - Spring集成测试支持
### 层级特定技术
- Controller层：MockMvc / WebTestClient / TestRestTemplate
- Service层：@Mock / @Spy / @Captor
- DAO层：@DataJpaTest / TestContainers / H2内存数据库
- 集成测试：@SpringBootTest / @TestPropertySource
## 高级测试规范
### 1. 精准命名策略
```java
// 测试类命名模式
[TargetClass][Layer][TestType]Test
// 示例：UserServiceUnitTest, OrderControllerIntegrationTest

// 测试方法命名模式  
test[MethodName]_When[Condition]_Then[ExpectedOutcome]
// 示例：testCreateUser_WhenValidInput_ThenReturnUserDto
//      testFindUser_WhenUserNotExists_ThenThrowNotFoundException```

```
### 2. 注解配置最佳实践

```java
// 单元测试配置
@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT) // 仅在必要时使用

// Controller层测试
@WebMvcTest(controllers = [TARGET_CLASS].class)
@Import({SecurityConfig.class, ValidationConfig.class}) // 按需导入配置

// Service层测试  
@ExtendWith(MockitoExtension.class)
@TestInstance(TestInstance.Lifecycle.PER_CLASS) // 如需共享测试实例

// 集成测试
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
@Transactional
@Rollback
```

### 3. 测试数据管理策略

- 使用Builder模式创建测试数据对象
- 实现TestDataFactory统一管理测试数据
- 采用@TestConfiguration配置测试专用Bean
- 利用@Sql脚本初始化数据库状态

### 4. 高质量测试结构

```java 
// AAA模式 (Arrange-Act-Assert)
@Test
@DisplayName("应该在用户输入有效时成功创建用户")
void testCreateUser_WhenValidInput_ThenReturnCreatedUser() {
    // Given (Arrange) - 准备测试数据和Mock行为
    CreateUserRequest request = UserTestDataFactory.createValidUserRequest();
    User expectedUser = UserTestDataFactory.createUser();
    when(userRepository.save(any(User.class))).thenReturn(expectedUser);
    
    // When (Act) - 执行被测试方法
    UserDto result = userService.createUser(request);
    
    // Then (Assert) - 验证结果和交互
    assertThat(result)
        .isNotNull()
        .extracting(UserDto::getId, UserDto::getName, UserDto::getEmail)
        .containsExactly(expectedUser.getId(), expectedUser.getName(), expectedUser.getEmail());
    
    verify(userRepository, times(1)).save(argThat(user -> 
        user.getName().equals(request.getName()) && 
        user.getEmail().equals(request.getEmail())
    ));
    verifyNoMoreInteractions(userRepository);
}
```

## 全面测试场景覆盖

### 1. 正向场景测试

- ✅ 正常业务流程验证
- ✅ 边界值处理（最大值、最小值、临界点）
- ✅ 不同输入组合的处理

### 2. 异常场景测试

- ❌ 无效输入参数（null、空值、格式错误）
- ❌ 业务规则违反（重复创建、状态不匹配）
- ❌ 外部依赖异常（数据库连接失败、第三方服务异常）
- ❌ 并发访问冲突

### 3. 性能和安全测试

- ⚡ 大数据量处理能力
- 🔒 权限控制验证
- 🛡️ 输入安全性检查

## 高级Mock和断言技巧

### 1. 智能Mock策略

```java
// 使用ArgumentCaptor捕获复杂参数
@Captor
private ArgumentCaptor<UserCreateEvent> eventCaptor;

// 验证事件发布
verify(eventPublisher).publishEvent(eventCaptor.capture());
UserCreateEvent capturedEvent = eventCaptor.getValue();
assertThat(capturedEvent.getUserId()).isEqualTo(expectedUserId);

// 使用Answer进行复杂Mock行为
when(userRepository.findById(anyLong())).thenAnswer(invocation -> {
    Long id = invocation.getArgument(0);
    return id > 0 ? Optional.of(createUserWithId(id)) : Optional.empty();
});
```

### 2. 流式断言最佳实践

```java
// 集合断言
assertThat(userList)
    .hasSize(3)
    .extracting(User::getName)
    .containsExactlyInAnyOrder("张三", "李四", "王五");

// 异常断言
assertThatThrownBy(() -> userService.deleteUser(-1L))
    .isInstanceOf(IllegalArgumentException.class)
    .hasMessageContaining("用户ID不能为负数")
    .hasNoCause();

// 软断言（多个断言失败时全部显示）
SoftAssertions.assertSoftly(softly -> {
    softly.assertThat(user.getName()).isEqualTo("张三");
    softly.assertThat(user.getAge()).isBetween(18, 65);
    softly.assertThat(user.getEmail()).contains("@");
});
```

## 特定层级测试要求

### Controller层测试

```java
@WebMvcTest(UserController.class)
class UserControllerTest {
    
    @Test
    void testCreateUser_WhenValidRequest_ThenReturnCreated() throws Exception {
        // 测试HTTP请求处理、参数验证、响应格式
        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(createUserRequest)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").exists())
                .andExpect(jsonPath("$.name").value("张三"))
                .andExpect(header().exists("Location"));
    }
}
```

### Service层测试

```java
// 重点测试业务逻辑、事务处理、异常处理
@Test
void testTransferMoney_WhenSufficientBalance_ThenTransferSuccessfully() {
    // 测试复杂业务逻辑、多步骤操作、事务一致性
}
```

### DAO层测试

```java
@DataJpaTest
@TestPropertySource(locations = "classpath:application-test.properties")
class UserRepositoryTest {
    
    @Test
    void testFindByEmail_WhenEmailExists_ThenReturnUser() {
        // 测试数据访问逻辑、SQL查询、数据映射
    }
}
```

## 代码质量保证

### 1. 测试覆盖率要求

- 行覆盖率 ≥ 80%
- 分支覆盖率 ≥ 70%
- 方法覆盖率 ≥ 90%
- 核心业务逻辑 = 100%

### 2. 测试维护性

- 使用有意义的测试名称和注释
- 避免测试间的相互依赖
- 保持测试方法简洁（单一职责）
- 定期重构重复的测试代码

### 3. 持续集成配置

```java
// 测试分组标记
@Tag("unit")
@Tag("fast")
class UserServiceUnitTest { }

@Tag("integration") 
@Tag("slow")
class UserServiceIntegrationTest { }
```

## 输出要求

请基于以上规范和` [CLASS_DETAILS] `信息生成完整的测试类，包含：

1. **完整的导包语句** - 包含所有必需的测试框架导入
2. **精确的类级注解配置** - 根据测试类型选择合适的注解组合
3. **结构化的测试数据工厂** - TestDataFactory类或Builder模式
4. **全场景测试方法集合** - 覆盖正常、边界、异常情况
5. **高质量断言和验证** - 使用AssertJ流式断言和Mockito验证
6. **清晰的文档注释** - `@DisplayName`和方法注释说明测试意图
7. **性能和安全测试用例** - 针对关键业务场景
8. **测试配置和辅助方法** - `@BeforeEach`、`@AfterEach`等生命周期方法

**特殊要求：**[SPECIFIC_REQUIREMENTS]

**生成的测试代码应该能够直接运行，无需额外修改，并能作为团队测试代码的标准模板。**