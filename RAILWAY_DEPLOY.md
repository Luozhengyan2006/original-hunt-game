# 🚂 Railway 部署指南

## 📋 前提条件

✅ 代码已推送到GitHub
✅ 配置文件已准备好（Procfile, requirements.txt）

## 🚀 部署步骤（5分钟完成）

### 1️⃣ 访问Railway并登录

1. 打开 https://railway.app
2. 点击 **"Start a New Project"**
3. 选择 **"Login with GitHub"** 并授权

### 2️⃣ 创建新项目

1. 点击 **"New Project"**
2. 选择 **"Deploy from GitHub repo"**
3. 找到并选择：**`Luozhengyan2006/original-hunt-game`**
4. 如果没看到仓库，点击 **"Configure GitHub App"** 添加访问权限

### 3️⃣ 配置项目

Railway会自动检测到这是Flask项目，但需要确认：

1. **Root Directory**: 设置为 `game`
2. **Start Command**: 自动检测到 `python run_prod.py`（来自Procfile）
3. 点击 **"Deploy"**

### 4️⃣ 等待部署

- 首次部署需要2-3分钟
- 可以查看实时日志
- 看到 "Serving Flask app" 表示成功

### 5️⃣ 获取URL

部署成功后：
1. 点击项目 → **"Settings"** → **"Domains"**
2. 会看到类似：`your-project.up.railway.app`
3. 点击URL测试游戏！

### 6️⃣ 绑定自定义域名（可选）

如果你有域名：

1. 在Railway项目中，进入 **"Settings"** → **"Domains"**
2. 点击 **"Add Custom Domain"**
3. 输入你的域名（如：`game.yourdomain.com`）
4. Railway会给你CNAME记录
5. 去你的域名管理商（如阿里云、腾讯云）添加CNAME记录：
   ```
   类型: CNAME
   主机记录: game (或你想要的子域名)
   记录值: [Railway提供的地址]
   ```
6. 等待DNS生效（5-30分钟）
7. Railway自动配置SSL证书（免费HTTPS）

## 🔧 配置环境变量（可选）

如果需要设置密钥：

1. 进入 **"Variables"** 标签
2. 添加环境变量：
   - `SECRET_KEY`: 你的密钥（用于Flask session）
   - `PORT`: 5000（默认）

## 📊 监控和日志

- **Deployments**: 查看部署历史
- **Logs**: 实时查看应用日志
- **Metrics**: 查看CPU、内存使用情况

## 🔄 自动部署

Railway已自动配置：
- 每次推送到GitHub的`main`分支
- Railway会自动检测并重新部署
- 无需手动操作！

## 💰 费用说明

**免费层（Trial Plan）：**
- $5 信用额度/月
- 500小时执行时间
- 对于小规模游戏完全够用

**如果超出免费层：**
- 自动升级到Hobby Plan
- $5/月 + 按用量计费
- 通常小游戏 $5-10/月足够

## ✅ 部署检查清单

- [ ] GitHub仓库代码最新
- [ ] 登录Railway
- [ ] 选择仓库并部署
- [ ] 设置Root Directory为`game`
- [ ] 部署成功
- [ ] 测试游戏URL
- [ ] （可选）绑定自定义域名

## 🆘 常见问题

**Q: 部署失败怎么办？**
A: 查看Logs标签，通常是依赖包问题。确保requirements.txt正确。

**Q: 如何重新部署？**
A: 推送新代码到GitHub，或在Railway点击"Redeploy"。

**Q: 游戏数据会丢失吗？**
A: Railway实例重启时内存数据会丢失。如果需要持久化，考虑添加数据库。

**Q: 如何停止项目？**
A: Settings → Danger → Delete Project

## 🎮 下一步

部署成功后：
1. 分享你的游戏链接
2. 测试多人联机功能
3. 如需持久化数据，考虑添加Redis或数据库

---

需要帮助？查看Railway文档：https://docs.railway.app
