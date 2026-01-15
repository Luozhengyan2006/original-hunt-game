# Vercel部署指南

## 方法一：通过Vercel网页部署（推荐）

### 步骤：

1. **访问Vercel官网**
   - 打开 https://vercel.com
   - 使用GitHub账号登录

2. **导入项目**
   - 点击 "Add New..." → "Project"
   - 选择你的GitHub仓库：`Luozhengyan2006/original-hunt-game`
   - 选择 `game` 目录作为根目录

3. **配置项目**
   - Framework Preset: 选择 "Other"
   - Root Directory: 设置为 `game`
   - Build Command: 留空
   - Output Directory: 留空
   - Install Command: `pip install -r requirements.txt`

4. **环境变量（可选）**
   - 如需配置密钥等，在Environment Variables中添加

5. **部署**
   - 点击 "Deploy" 按钮
   - 等待部署完成（约1-2分钟）
   - 获取部署URL（如：https://your-project.vercel.app）

## 方法二：通过Vercel CLI部署

### 前置要求：
- 安装Node.js和npm（从 https://nodejs.org 下载）

### 步骤：

1. **安装Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **登录Vercel**
   ```bash
   vercel login
   ```

3. **首次部署（测试环境）**
   ```bash
   cd c:\Users\97746\OneDrive\Desktop\git\game
   vercel
   ```

4. **部署到生产环境**
   ```bash
   vercel --prod
   ```

## 配置说明

- `vercel.json` - Vercel配置文件
- `api/index.py` - Serverless函数入口
- `requirements.txt` - Python依赖

## 注意事项

⚠️ **重要限制：**

Vercel的免费版有以下限制：
- 单个函数最大执行时间：10秒
- 内存限制：1024MB
- 无法保持长连接（WebSocket）
- 无法存储持久化数据

### 建议的解决方案：

1. **使用外部数据库**
   - Redis (Upstash)
   - MongoDB (MongoDB Atlas)
   - PostgreSQL (Supabase)

2. **实时通信**
   - 使用轮询代替WebSocket
   - 前端每2-3秒请求一次状态更新

3. **当前实现**
   - 游戏状态存储在内存中
   - 每个请求都是独立的
   - 适合快速测试和演示

## 环境变量

如需配置环境变量，在Vercel项目设置中添加：
- `SECRET_KEY` - Flask密钥
- 其他必要的配置

## 本地测试

```bash
vercel dev
```

这将在本地运行Vercel环境进行测试。
