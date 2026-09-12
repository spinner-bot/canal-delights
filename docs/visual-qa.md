# 视觉质量验收文档 (Visual QA)

> 记录 Renderer 的功能矩阵和测试结果

---

## 功能矩阵

### 图形类型支持

| 类型码 | 名称 | 实色填充 | 线性渐变 | 径向渐变 | 描边 | 状态 |
|--------|------|----------|----------|----------|------|------|
| P | Point | ✅ | N/A | N/A | N/A | PASS |
| L | Line | N/A | N/A | N/A | ✅ | PASS |
| R | Rect | ✅ | LIMITED | LIMITED | ✅ | PASS |
| RR | RoundedRect | ✅ | LIMITED | LIMITED | ✅ | PASS |
| C | Circle | ✅ | LIMITED | LIMITED | ✅ | PASS |
| E | Ellipse | ✅ | LIMITED | LIMITED | ✅ | PASS |
| G | Polygon | ✅ | LIMITED | LIMITED | ✅ | PASS |
| A | Arc | N/A | N/A | N/A | ✅ | PASS |
| Q | Quadratic | N/A | N/A | N/A | ✅ | PASS |
| B | Cubic | N/A | N/A | N/A | ✅ | PASS |
| PATH | CompoundPath | ✅ | LIMITED | LIMITED | ✅ | PASS |
| RG | Ring | ✅ | LIMITED | ✅ | ✅ | PASS |
| T | Text | ✅ | N/A | N/A | N/A | PASS |
| GR | Group | ✅ | LIMITED | LIMITED | ✅ | PASS |

### 状态说明

- **PASS**: 功能正常，可用于正式资产
- **LIMITED**: 功能可用但有已知限制（见下方）
- **FAIL**: 功能不可用或存在严重问题

### 已知限制

1. **渐变**：
   - 线性渐变已经实现投影色带与多边形裁切；径向渐变使用嵌套轮廓近似。
   - 凹多边形径向渐变、圆环内孔仍需人工视觉验收，因此继续标为 LIMITED。

2. **圆角矩形 (RR)**：
   - 实色圆角正确；渐变会使用采样轮廓，边缘平滑度取决于采样精度。

3. **双后端**：纯 Turtle 与批量 Canvas 加速模式共享同一套 DSL；复杂视觉能力不得产生模式间内容差异。

---

## 测试结果

### 单元测试

```
命令: python -m pytest tests/ -v
结果: 53 passed
```

**测试覆盖：**
- 颜色校验与转换 ✅
- RGBA 预混色 ✅
- 颜色插值 ✅
- 坐标转换 ✅
- Transform 变换 ✅
- 贝塞尔曲线采样 ✅
- 椭圆采样 ✅
- 点在多边形内测试 ✅

### 可视化测试

**Primitive Gallery**

```
命令: python examples/primitive_gallery.py
平台: Windows, Python 3.13.5
日期: 2026-09-12
```

**已验证项目：**
- [x] 14 种类型码均可渲染
- [x] 实色填充正确
- [x] 线性渐变可见（投影色带裁切）
- [x] 径向渐变可见（嵌套轮廓近似）
- [x] 描边线宽可配置
- [x] 文字渲染正常
- [x] Group 组合正确

**待人工确认：**
- [ ] 渐变裁切边界是否精确
- [ ] 圆角矩形渐变效果
- [ ] 复杂路径闭合

---

## 颜色系统

### RGB256 支持

- [x] 标准 RGB (r, g, b) 格式
- [x] RGBA (r, g, b, a) 输入
- [x] Alpha 预混色实现
- [x] 颜色校验（范围、类型）

### 渐变系统

- [ ] 线性渐变（数据格式与颜色插值已实现，绘制未实现）
- [ ] 径向渐变（数据格式与颜色插值已实现，绘制未实现）
- [x] 多色标支持（2、3、5 个）
- [x] 色标位置 0.0-1.0
- [x] 颜色插值正确

---

## Transform 系统

- [x] 平移 (translate)
- [x] 缩放 (scale)
- [x] 旋转 (rotate)
- [x] 枢轴点 (pivot)
- [x] Group 嵌套变换

---

## 性能观察

| 场景 | 绘制时间 | 备注 |
|------|----------|------|
| Primitive Gallery (14种) | < 1s | 静态画面，无卡顿 |
| 简单食物 (粽子) | < 0.5s | 约 10 个 primitive |

---

## 待改进项

1. **渐变裁切优化**：实现完整的 Sutherland-Hodgman 多边形裁切
2. **圆角矩形渐变**：精确裁切到圆角轮廓
3. **性能测试**：大量 primitive 时的帧率测试
4. **命中测试**：完成点击区域的精确测试

---

## 下一步

G1 闸门验收条件：

- [x] pytest 全部通过 (36/36)
- [x] Primitive Gallery 可运行
- [x] 14 种类型码定义一致
- [x] 不使用 sys.path 修改
- [ ] 三个 Gallery 全部完成（gradient_gallery, transform_gallery 待实现）
- [ ] 人工视觉验收

---

*文档版本: v1.0*
*更新日期: 2026-09-12*
*状态: G1 进行中*
