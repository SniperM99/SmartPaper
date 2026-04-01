# SmartPaper 样式指南

本文档展示 SmartPaper Vue 界面样式系统的所有组件和使用示例。

## 目录

1. [配色方案](#配色方案)
2. [按钮组件](#按钮组件)
3. [输入组件](#输入组件)
4. [卡片组件](#卡片组件)
5. [标签组件](#标签组件)
6. [布局组件](#布局组件)
7. [状态组件](#状态组件)

---

## 配色方案

### 主色调 - 学术蓝

<div style="display: flex; gap: 16px; margin-bottom: 16px;">
  <div style="width: 100px; height: 100px; background-color: #1e40af; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white;">
    Primary
  </div>
  <div style="width: 100px; height: 100px; background-color: #1e3a8a; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white;">
    Hover
  </div>
  <div style="width: 100px; height: 100px; background-color: #dbeafe; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #1e3a8a;">
    Light
  </div>
</div>

```css
--color-primary: #1e40af;
--color-primary-hover: #1e3a8a;
--color-primary-light: #dbeafe;
--color-primary-dark: #1e3a8a;
```

### 语义色

<div style="display: flex; gap: 16px; margin-bottom: 16px;">
  <div style="width: 80px; height: 80px; background-color: #059669; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white;">Success</div>
  <div style="width: 80px; height: 80px; background-color: #d97706; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white;">Warning</div>
  <div style="width: 80px; height: 80px; background-color: #dc2626; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white;">Error</div>
  <div style="width: 80px; height: 80px; background-color: #0891b2; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white;">Info</div>
</div>

```css
--color-success: #059669;
--color-warning: #d97706;
--color-error: #dc2626;
--color-info: #0891b2;
```

---

## 按钮组件

### 标准按钮

<div style="display: flex; gap: 12px; align-items: center; margin-bottom: 24px;">
  <button style="padding: 8px 16px; background-color: #1e40af; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">
    主按钮
  </button>
  <button style="padding: 8px 16px; background-color: transparent; color: #1e40af; border: 1px solid #1e40af; border-radius: 8px; cursor: pointer; font-weight: 500;">
    次要按钮
  </button>
  <button style="padding: 8px 16px; background-color: #059669; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">
    成功
  </button>
  <button style="padding: 8px 16px; background-color: #dc2626; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">
    危险
  </button>
</div>

### 大小变体

<div style="display: flex; gap: 12px; align-items: center; margin-bottom: 24px;">
  <button style="padding: 6px 12px; background-color: #1e40af; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500; font-size: 14px;">
    小按钮
  </button>
  <button style="padding: 8px 16px; background-color: #1e40af; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500; font-size: 16px;">
    标准按钮
  </button>
  <button style="padding: 12px 24px; background-color: #1e40af; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500; font-size: 18px;">
    大按钮
  </button>
</div>

### 幽灵按钮和禁用状态

<div style="display: flex; gap: 12px; align-items: center;">
  <button style="padding: 8px 16px; background-color: transparent; color: #1e293b; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">
    幽灵按钮
  </button>
  <button style="padding: 8px 16px; background-color: #1e40af; color: white; border: none; border-radius: 8px; cursor: not-allowed; font-weight: 500; opacity: 0.6;" disabled>
    禁用按钮
  </button>
</div>

---

## 输入组件

### 标准输入框

<div style="max-width: 400px; margin-bottom: 24px;">
  <input type="text" placeholder="请输入内容" style="width: 100%; height: 40px; padding: 0 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 16px;">
</div>

### 输入框变体

<div style="max-width: 400px; display: flex; flex-direction: column; gap: 12px;">
  <input type="text" placeholder="小输入框" style="width: 100%; height: 32px; padding: 0 8px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px;">
  <input type="text" placeholder="标准输入框" style="width: 100%; height: 40px; padding: 0 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 16px;">
  <input type="text" placeholder="大输入框" style="width: 100%; height: 48px; padding: 0 16px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 18px;">
  <input type="text" placeholder="错误状态" style="width: 100%; height: 40px; padding: 0 12px; border: 1px solid #dc2626; border-radius: 8px; font-size: 16px;">
  <input type="text" placeholder="禁用状态" disabled style="width: 100%; height: 40px; padding: 0 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 16px; background-color: #f1f5f9; cursor: not-allowed; color: #94a3b8;">
</div>

---

## 卡片组件

### 标准卡片

<div style="border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); overflow: hidden; max-width: 400px; margin-bottom: 24px;">
  <div style="padding: 16px 24px; border-bottom: 1px solid #e2e8f0; background-color: #f8fafc;">
    <h3 style="font-size: 18px; font-weight: 600; color: #1e293b; margin: 0;">卡片标题</h3>
  </div>
  <div style="padding: 24px;">
    <p style="color: #475569; margin: 0 0 16px 0;">这是卡片的主要内容区域。</p>
    <p style="color: #64748b; margin: 0;">可以包含文本、图片、表单等各种内容。</p>
  </div>
  <div style="padding: 16px 24px; border-top: 1px solid #e2e8f0; background-color: #f8fafc; display: flex; gap: 8px;">
    <button style="padding: 8px 16px; background-color: #1e40af; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">确认</button>
    <button style="padding: 8px 16px; background-color: transparent; color: #1e40af; border: 1px solid #1e40af; border-radius: 8px; cursor: pointer; font-weight: 500;">取消</button>
  </div>
</div>

### 可点击卡片（悬停效果）

<div style="border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); overflow: hidden; max-width: 400px; cursor: pointer; transition: all 0.2s; margin-bottom: 24px;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 10px 15px -3px rgba(0, 0, 0, 0.1)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 1px 2px rgba(0, 0, 0, 0.05)';">
  <div style="padding: 24px;">
    <h3 style="font-size: 18px; font-weight: 600; color: #1e293b; margin: 0 0 8px 0;">可点击卡片</h3>
    <p style="color: #475569; margin: 0;">悬停时会上升并显示阴影效果</p>
  </div>
</div>

---

## 标签组件

### 深色背景标签

<div style="display: flex; gap: 12px; align-items: center; margin-bottom: 24px;">
  <span style="display: inline-flex; align-items: center; padding: 4px 12px; font-size: 12px; font-weight: 500; color: white; border-radius: 999px; background-color: #059669;">
    成功
  </span>
  <span style="display: inline-flex; align-items: center; padding: 4px 12px; font-size: 12px; font-weight: 500; color: white; border-radius: 999px; background-color: #0891b2;">
    进行中
  </span>
  <span style="display: inline-flex; align-items: center; padding: 4px 12px; font-size: 12px; font-weight: 500; color: white; border-radius: 999px; background-color: #d97706;">
    警告
  </span>
  <span style="display: inline-flex; align-items: center; padding: 4px 12px; font-size: 12px; font-weight: 500; color: white; border-radius: 999px; background-color: #dc2626;">
    错误
  </span>
</div>

### 浅色背景标签

<div style="display: flex; gap: 12px; align-items: center;">
  <span style="display: inline-flex; align-items: center; padding: 4px 12px; font-size: 12px; font-weight: 500; color: #059669; border-radius: 999px; background-color: #d1fae5;">
    已完成
  </span>
  <span style="display: inline-flex; align-items: center; padding: 4px 12px; font-size: 12px; font-weight: 500; color: #0891b2; border-radius: 999px; background-color: #ecfeff;">
    处理中
  </span>
  <span style="display: inline-flex; align-items: center; padding: 4px 12px; font-size: 12px; font-weight: 500; color: #d97706; border-radius: 999px; background-color: #fef3c7;">
    待审核
  </span>
  <span style="display: inline-flex; align-items: center; padding: 4px 12px; font-size: 12px; font-weight: 500; color: #dc2626; border-radius: 999px; background-color: #fee2e2;">
    已失败
  </span>
</div>

---

## 布局组件

### 统计卡片

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; margin-bottom: 24px;">
  <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px;">
    <div style="width: 48px; height: 48px; border-radius: 12px; background-color: #dbeafe; color: #1e40af; display: flex; align-items: center; justify-content: center; margin-bottom: 16px;">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
      </svg>
    </div>
    <div style="font-size: 12px; font-weight: 500; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">论文总数</div>
    <div style="font-size: 30px; font-weight: 700; color: #1e293b; margin-top: 4px;">24</div>
    <div style="font-size: 14px; color: #059669; margin-top: 12px;">↑ 12% 较上周</div>
  </div>

  <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px;">
    <div style="width: 48px; height: 48px; border-radius: 12px; background-color: #d1fae5; color: #059669; display: flex; align-items: center; justify-content: center; margin-bottom: 16px;">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
    </div>
    <div style="font-size: 12px; font-weight: 500; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">已分析</div>
    <div style="font-size: 30px; font-weight: 700; color: #1e293b; margin-top: 4px;">18</div>
    <div style="font-size: 14px; color: #059669; margin-top: 12px;">↑ 8% 较上周</div>
  </div>
</div>

---

## 状态组件

### 加载 Spinner

<div style="display: flex; gap: 24px; align-items: center; margin-bottom: 24px;">
  <div style="width: 24px; height: 24px; border: 3px solid #e2e8f0; border-top-color: #1e40af; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
  <div style="width: 16px; height: 16px; border: 2px solid #e2e8f0; border-top-color: #1e40af; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
  <div style="width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top-color: #1e40af; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
</div>

### 骨架屏

<div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; max-width: 400px;">
  <div style="width: 100%; height: 20px; background: linear-gradient(90deg, #f1f5f9 25%, #f8fafc 50%, #f1f5f9 75%); background-size: 200% 100%; animation: shimmer 1.5s ease-in-out infinite; border-radius: 4px; margin-bottom: 8px;"></div>
  <div style="width: 80%; height: 20px; background: linear-gradient(90deg, #f1f5f9 25%, #f8fafc 50%, #f1f5f9 75%); background-size: 200% 100%; animation: shimmer 1.5s ease-in-out infinite; border-radius: 4px; margin-bottom: 8px;"></div>
  <div style="width: 60%; height: 20px; background: linear-gradient(90deg, #f1f5f9 25%, #f8fafc 50%, #f1f5f9 75%); background-size: 200% 100%; animation: shimmer 1.5s ease-in-out infinite; border-radius: 4px;"></div>
</div>

<style>
@keyframes spin {
  to { transform: rotate(360deg); }
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>

---

## 使用建议

1. **保持一致性**：在项目中统一使用提供的组件和样式，避免自定义样式
2. **响应式设计**：使用提供的网格和布局工具类，确保在不同设备上的良好体验
3. **可访问性**：确保颜色对比度符合 WCAG 标准，为交互元素提供焦点样式
4. **性能优化**：合理使用过渡动画，避免过度使用影响性能

## 下一步

- 查看 [docs/DESIGN_SPEC.md](DESIGN_SPEC.md) 了解详细的设计规范
- 查看代码实现：`src/assets/styles/`
- 查看示例组件：`src/components/` 和 `src/views/`
