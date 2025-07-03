# Web安全事件管理系统 - 前端

基于Vue 3 + TypeScript + Element Plus的现代化Web应用，用于管理和分析Web安全事件。

## 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全的JavaScript超集
- **Element Plus** - 基于Vue 3的企业级UI组件库
- **Vue Router** - 官方路由管理器
- **Pinia** - 现代化状态管理库
- **ECharts** - 数据可视化图表库
- **Axios** - HTTP客户端
- **Vite** - 快速构建工具

## 项目结构

```
frontend/
├── src/
│   ├── components/          # 通用组件
│   │   └── Layout/         # 布局组件
│   ├── views/              # 页面组件
│   │   ├── Dashboard/      # 监控大屏
│   │   ├── Events/         # 事件管理
│   │   ├── Analytics/      # 统计分析
│   │   └── Settings/       # 系统配置
│   ├── stores/             # 状态管理
│   ├── services/           # API服务
│   ├── types/              # TypeScript类型定义
│   ├── styles/             # 全局样式
│   └── router/             # 路由配置
├── public/                 # 静态资源
└── dist/                   # 构建输出
```

## 功能特性

### 🎯 核心功能
- **监控大屏** - 实时威胁统计、趋势分析图表
- **事件管理** - 安全事件列表、详情查看、状态管理
- **统计分析** - 威胁分析报告、数据可视化
- **系统配置** - 检测规则、AI模型参数设置

### 🎨 界面特性
- **响应式设计** - 适配桌面端和移动端
- **现代化UI** - 简洁美观的界面设计
- **暗色主题** - 支持浅色/深色主题切换
- **实时更新** - WebSocket实时数据推送

### 🔧 技术特性
- **TypeScript** - 完整类型支持，开发体验更好
- **组件化** - 可复用的组件架构
- **状态管理** - Pinia状态管理，数据响应式
- **路由守卫** - 页面级权限控制
- **API拦截** - 统一错误处理和请求拦截

## 快速开始

### 环境要求
- Node.js >= 16.0.0
- npm >= 7.0.0 或 yarn >= 1.22.0

### 安装依赖
```bash
cd frontend
npm install
```

### 开发模式
```bash
npm run dev
```
启动开发服务器，默认访问：http://localhost:3000

### 构建生产版本
```bash
npm run build
```

### 预览构建结果
```bash
npm run preview
```

### 代码检查
```bash
npm run lint
```

### 类型检查
```bash
npm run type-check
```

## 环境配置

在项目根目录创建环境配置文件：

### `.env.development`
```env
VITE_APP_TITLE=Web安全事件管理系统
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WEBSOCKET_URL=ws://localhost:8000/ws
```

### `.env.production`
```env
VITE_APP_TITLE=Web安全事件管理系统
VITE_API_BASE_URL=/api
VITE_WEBSOCKET_URL=wss://your-domain.com/ws
```

## 开发指南

### 组件开发
- 使用Composition API和`<script setup>`语法
- 组件文件采用PascalCase命名
- 样式使用scoped CSS和SCSS

### 状态管理
- 使用Pinia进行状态管理
- 按业务模块划分store
- 支持TypeScript类型推导

### API调用
- 统一使用services目录下的API函数
- 自动处理错误和loading状态
- 支持请求拦截和响应处理

### 路由配置
- 支持动态路由和路由守卫
- 自动生成面包屑导航
- 支持页面级权限控制

## 部署说明

### Docker部署
```bash
# 构建镜像
docker build -t web-security-frontend .

# 运行容器
docker run -p 3000:80 web-security-frontend
```

### Nginx部署
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /path/to/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

MIT License

## 联系我们

- 项目地址：https://github.com/your-org/web-security-system
- 问题反馈：https://github.com/your-org/web-security-system/issues
- 邮箱：dev@your-domain.com 