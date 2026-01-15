# Vercel部署指南

## 部署步骤

1. **安装Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **登录Vercel**
   ```bash
   vercel login
   ```

3. **部署到Vercel**
   ```bash
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
