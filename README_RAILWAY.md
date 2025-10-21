# Railway 快速部署指南

## 🚀 三步部署到Railway

### 第1步：上传到GitHub

```bash
git add .
git commit -m "准备部署到Railway"
git push
```

### 第2步：在Railway部署

1. 访问：**https://railway.app/**
2. GitHub登录
3. 选择 "Deploy from GitHub repo"
4. 选择你的仓库
5. 点击Deploy

### 第3步：配置环境变量

在Railway控制台添加：

| 变量名 | 值 |
|--------|---|
| `DATABASE_PATH` | `/app/data/project_management.db` |
| `SECRET_KEY` | 随机字符串（见下方） |
| `FLASK_ENV` | `production` |

生成SECRET_KEY：
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## ✅ 完成！

等待5-10分钟构建完成后：

1. Railway会自动生成域名
2. 访问：`https://your-app.railway.app`
3. 登录：admin / admin123

---

## 📖 详细教程

查看完整教程：[Railway部署详细教程.md](./Railway部署详细教程.md)

包含：
- 详细步骤说明
- 常见问题解决
- 优化配置技巧
- 进阶功能

---

## 💡 注意事项

1. **免费额度**：500小时/月（约21天）
2. **数据持久化**：免费版重启可能丢失数据，建议定期备份
3. **首次构建**：需要5-10分钟
4. **自动部署**：每次push到GitHub会自动重新部署

---

## 🔗 有用链接

- Railway官网：https://railway.app/
- 完整教程：[Railway部署详细教程.md](./Railway部署详细教程.md)
- Railway文档：https://docs.railway.app/

---

**总耗时：10分钟**  
**费用：免费**  
**访问：全球可达**

🎉 开始部署吧！

