# SmartPaper 现代化设计指南

## 设计原则

### 1. 简洁专业
- 去除冗余装饰，聚焦核心内容
- 使用专业的 SVG 图标，避免 emoji
- 保持视觉层次清晰

### 2. 一致性
- 统一的设计语言
- 可复用的组件库
- 标准化的交互模式

### 3. 可访问性
- 符合 WCAG AA 标准
- 颜色对比度 ≥ 4.5:1
- 清晰的焦点状态

### 4. 响应式
- 移动优先设计
- 流式布局
- 触控友好

---

## 配色方案

### 主色调
```
Primary:    #1e40af  (学术蓝)
Hover:      #1e3a8a  (深蓝)
Light:      #dbeafe  (浅蓝背景)
```

### 语义色
```
Success:    #059669  (绿色)
Warning:    #d97706  (橙色)
Error:      #dc2626  (红色)
Info:       #0891b2  (青色)
```

### 中性色
```
Text Primary:   #1e293b  (主要文字)
Text Secondary: #475569  (次要文字)
Text Tertiary:  #64748b  (辅助文字)
Bg Primary:     #ffffff  (白色背景)
Bg Secondary:   #f8fafc  (浅灰背景)
Bg Tertiary:    #f1f5f9  (更浅灰)
Border:         #e2e8f0  (边框)
```

---

## 图标系统

### 图标设计规范
- 使用 Feather Icons 风格
- 24x24 像素标准尺寸
- 2px 描边宽度
- 圆角端点

### 图标使用原则
- 使用语义化的 SVG 图标
- 保持图标一致性
- 避免装饰性图标

### 图标组件

#### 导航图标
```vue
<IconHome />      <!-- 首页 -->
<IconUpload />     <!-- 上传 -->
<IconLibrary />    <!-- 论文库 -->
<IconAnalysis />   <!-- 分析 -->
<IconFileText />  <!-- 文件 -->
<IconCompare />   <!-- 对比 -->
<IconMap />       <!-- 地图 -->
<IconSettings />  <!-- 设置 -->
```

#### 操作图标
```vue
<IconSearch />    <!-- 搜索 -->
<IconBell />      <!-- 通知 -->
```

---

## 认证页面设计

### 登录页面
- **布局**：居中卡片设计
- **背景**：渐变背景 (135deg, #667eea 0%, #764ba2 100%)
- **卡片**：白色背景，16px 圆角，阴影
- **Logo**：80x80 图标，渐变背景
- **表单**：单列布局
- **按钮**：主按钮全宽，社交登录次按钮

### 注册页面
- **布局**：与登录页面一致
- **字段**：姓名、邮箱、密码、确认密码
- **验证**：密码强度指示器
- **条款**：服务条款和隐私政策复选框

### 忘记密码
- **布局**：简化的登录页面
- **字段**：仅邮箱地址
- **提示**：说明文字

### 重置密码
- **布局**：注册页面变体
- **字段**：新密码、确认新密码
- **特性**：密码强度指示器

---

## 数据表格设计

### 表格结构
```
┌─────────────────────────────────────────────┐
│  [搜索框]              [操作按钮组]        │  ← 工具栏
├─────────────────────────────────────────────┤
│  标题1  标题2  标题3  标题4  操作          │  ← 表头
├─────────────────────────────────────────────┤
│  数据1  数据2  数据3  数据4  [编辑][删除]   │
│  数据1  数据2  数据3  数据4  [编辑][删除]   │  ← 表格内容
│  ...                                       │
├─────────────────────────────────────────────┤
│  显示 1-10 条，共 100 条    [上一页][下一页]│  ← 分页
└─────────────────────────────────────────────┘
```

### 表格样式
- **背景**：白色
- **边框**：1px solid #e2e8f0
- **圆角**：12px
- **表头**：浅灰背景 (#f8fafc)
- **行高**：56px
- **悬停**：浅蓝背景 (#f0f9ff)

### 表格功能
- 排序
- 搜索
- 分页
- 行内操作

---

## 统计卡片设计

### 卡片结构
```
┌────────────────────────┐
│  [图标]                │
├────────────────────────┤
│  标签文字              │
│  统计数值              │
│  ↑ 12% 较上周          │
└────────────────────────┘
```

### 卡片样式
- **背景**：白色
- **边框**：1px solid #e2e8f0
- **圆角**：12px
- **内边距**：24px
- **阴影**：悬停时显示

### 卡片类型
- **primary**：主要统计（论文总数）
- **success**：成功统计（已分析）
- **warning**：警告统计（待处理）
- **info**：信息统计（本周分析）

---

## 表单设计

### 表单布局
```
┌────────────────────────┐
│  标签                  │
│  [输入框]               │
│                        │
│  标签                  │
│  [输入框]               │
│  错误提示              │
│                        │
│  [主按钮] [次按钮]      │
└────────────────────────┘
```

### 表单样式
- **标签**：14px，500 字重
- **输入框**：40px 高度，8px 圆角
- **错误**：红色文字，12px
- **按钮**：主按钮全宽

### 表单验证
- 实时验证
- 清晰的错误提示
- 成功状态反馈

---

## 侧边栏设计

### 侧边栏结构
```
┌────────────────────────┐
│  Logo 图标  Logo 文字  │  ← Logo 区域
├────────────────────────┤
│  工作区                │  ← 分组标题
│  • 工作台总览          │
│  • 导入与解析          │
│  • 论文库 (12)         │  ← 徽章
│  • 分析工作流          │
├────────────────────────┤
│  分析工具              │
│  • 单篇分析            │
│  • 多篇对比            │
│  • 研究地图            │
├────────────────────────┤
│  设置                  │
│  • 系统设置            │
│  • 帮助文档            │
├────────────────────────┤
│  用户头像  用户信息    │  ← 用户区域
└────────────────────────┘
```

### 侧边栏样式
- **宽度**：280px
- **背景**：渐变蓝 (linear-gradient(180deg, #1e40af 0%, #1e3a8a 100%))
- **文字**：白色
- **导航项**：48px 高度，8px 圆角
- **激活状态**：半透明白色背景
- **徽章**：紫色背景 (#7c3aed)

---

## 响应式断点

```css
xs:  640px   /* 手机竖屏 */
sm:  640px   /* 手机横屏 */
md:  768px   /* 平板 */
lg:  1024px  /* 小笔记本 */
xl:  1280px  /* 桌面 */
2xl: 1536px  /* 大屏 */
```

### 移动端适配
- 侧边栏：抽屉式导航
- 表格：横向滚动
- 表单：单列布局
- 按钮：全宽

---

## 动画规范

### 过渡时长
```
Fast:   150ms  /* 按钮、输入框 */
Base:   200ms  /* 组件 */
Slow:   300ms  /* 模态框 */
```

### 缓动函数
```css
ease-out:     cubic-bezier(0.4, 0, 0.2, 1)
ease-in-out:  cubic-bezier(0.4, 0, 0.2, 1)
```

### 动画类型
- **淡入淡出**：opacity
- **上滑**：translateY(-20px) → 0
- **缩放**：scale(0.95) → 1
- **旋转**：spinner 加载

---

## 间距系统

基于 8px 网格：

```
xs:  4px   /* 紧密元素 */
sm:  8px   /* 图标文字 */
md:  16px  /* 默认间距 */
lg:  24px  /* 区块间距 */
xl:  32px  /* 大区块间距 */
2xl: 48px  /* 页面间距 */
```

---

## 圆角系统

```
sm:  4px   /* 按钮、标签 */
md:  8px   /* 输入框 */
lg:  12px  /* 卡片 */
xl:  16px  /* 模态框 */
full: 9999px /* 徽章、头像 */
```

---

## 阴影系统

```
sm:  0 1px 2px rgba(0, 0, 0, 0.05)
md:  0 4px 6px rgba(0, 0, 0, 0.1)
lg:  0 10px 15px rgba(0, 0, 0, 0.1)
xl:  0 20px 25px rgba(0, 0, 0, 0.1)
```

---

## 字体系统

### 字体栈
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto',
             'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans',
             'Helvetica Neue', sans-serif;
```

### 字号
```
H1:  40px  /* 页面标题 */
H2:  30px  /* 区块标题 */
H3:  24px  /* 组件标题 */
H4:  20px  /* 小标题 */
Body: 16px  /* 正文 */
Small: 14px /* 辅助文字 */
Xs:   12px /* 标签、脚注 */
```

### 字重
```
Bold:      700  /* 标题 */
Semibold:  600  /* 次级标题 */
Medium:    500  /* 组件 */
Regular:   400  /* 正文 */
Light:     300  /* 辅助 */
```

### 行高
```
Tight:     1.2   /* 标题 */
Normal:    1.5   /* 代码 */
Relaxed:   1.6   /* 正文 */
```

---

## 组件库使用指南

### 按钮
```vue
<!-- 主按钮 -->
<button class="btn btn-primary">提交</button>

<!-- 次要按钮 -->
<button class="btn btn-secondary">取消</button>

<!-- 危险按钮 -->
<button class="btn btn-danger">删除</button>

<!-- 大按钮 -->
<button class="btn btn-primary btn-lg">大按钮</button>

<!-- 小按钮 -->
<button class="btn btn-primary btn-sm">小按钮</button>
```

### 输入框
```vue
<!-- 标准输入框 -->
<input class="input" placeholder="请输入..." />

<!-- 带图标的输入框 -->
<div class="input-with-icon">
  <IconSearch />
  <input class="input" placeholder="搜索..." />
</div>

<!-- 错误状态 -->
<input class="input input-error" placeholder="错误状态" />
```

### 标签
```vue
<!-- 成功标签 -->
<span class="badge badge-success">成功</span>

<!-- 浅色标签 -->
<span class="badge badge-success-light">已完成</span>
```

### 统计卡片
```vue
<StatCard
  label="论文总数"
  :value="24"
  change="12%"
  variant="primary"
>
  <template #icon>
    <svg>...</svg>
  </template>
</StatCard>
```

### 数据表格
```vue
<DataTable
  :data="tableData"
  :columns="columns"
  searchable
  :page-size="10"
  @sort="handleSort"
>
  <template #cell-status="{ row }">
    <span class="badge" :class="getStatusClass(row.status)">
      {{ row.status }}
    </span>
  </template>
  <template #actions="{ row }">
    <button @click="edit(row)">编辑</button>
    <button @click="delete(row)">删除</button>
  </template>
</DataTable>
```

---

## 最佳实践

### 1. 布局原则
- 使用网格和 Flex 布局
- 保持视觉对齐
- 使用一致的间距

### 2. 色彩使用
- 主色用于主要操作
- 语义色表示状态
- 中性色用于文本和背景

### 3. 文字使用
- 清晰的视觉层次
- 合理的字号和字重
- 充足的行高

### 4. 交互设计
- 明确的悬停状态
- 清晰的焦点指示
- 合理的动画时长

### 5. 可访问性
- 提供焦点样式
- 确保颜色对比度
- 添加 ARIA 标签

---

## 常见问题

### Q: 如何自定义主题颜色？
A: 修改 `src/assets/styles/variables.css` 中的颜色变量。

### Q: 如何添加新图标？
A: 在 `src/components/icons/` 创建新组件，使用 Feather Icons 风格。

### Q: 如何实现暗色模式？
A: 样式系统已预留暗色模式变量，在 `@media (prefers-color-scheme: dark)` 中定义。

### Q: 如何优化移动端体验？
A: 使用响应式断点，调整布局，优化触控区域大小。

---

## 资源链接

- [Feather Icons](https://feathericons.com/) - 图标库
- [Tailwind CSS](https://tailwindcss.com/) - 设计系统参考
- [Figma](https://www.figma.com/) - 设计工具
- [WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/) - 可访问性标准
