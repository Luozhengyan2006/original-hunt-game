# 🎨 扭曲画猜 (Twist Draw Guess)

一个创意多人在线绘画猜测游戏。

## 功能特点

- 🌐 **双语支持** - 中文/English
- 👥 **多人游戏** - 支持2-10人
- 🎯 **5轮游戏** - 完整的游戏流程
- 🎨 **Canvas绘图** - 实时绘画功能
- 📊 **实时计分** - 自动计分系统

## 游戏规则

1. **创建游戏** - 一名玩家创建游戏并获得游戏代码
2. **玩家加入** - 其他玩家使用游戏代码加入
3. **开始游戏** - 至少2名玩家后可开始
4. **每轮流程**：
   - 出题者收到3个真实关键词，可选择修改为假关键词来迷惑其他玩家
   - 所有玩家（包括出题者）根据关键词绘画
   - 其他玩家猜测哪幅画是出题者画的
   - 根据猜测结果计分
5. **计分规则**：
   - 猜对出题者：+1分
   - 被其他玩家误认为是出题者：+1分
   - 如果没人猜对，出题者+2分

## 本地运行

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动服务器
```bash
# 开发模式
python app.py

# 生产模式
python run_prod.py
```

访问: http://localhost:5000

## Vercel部署

详见 [VERCEL_DEPLOY.md](VERCEL_DEPLOY.md)

### 快速部署

```bash
# 安装Vercel CLI
npm install -g vercel

# 登录
vercel login

# 部署
vercel --prod
```

## 项目结构

```
game/
├── app.py              # Flask主应用
├── run_prod.py         # 生产环境启动脚本
├── requirements.txt    # Python依赖
├── keywords_library.json  # 关键词库
├── api/
│   └── index.py       # Vercel serverless入口
├── static/
│   ├── style.css      # 样式文件
│   └── game.js        # 前端逻辑
├── templates/
│   └── index.html     # 主页面
├── vercel.json        # Vercel配置
└── tests/             # 测试文件

```

## 技术栈

- **后端**: Flask + Flask-CORS
- **前端**: Vanilla JavaScript + Canvas API
- **部署**: Vercel Serverless

## 测试

```bash
# 运行测试（需要先启动服务器）
python test_simple.py
python test_game_flow.py
python test_lobby_sync.py
```

## 注意事项

⚠️ **Vercel限制**
- 当前版本使用内存存储，Vercel serverless环境下无法保持状态
- 建议在本地运行或使用外部数据库（Redis/MongoDB）

## License

MIT
