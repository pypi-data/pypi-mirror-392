# Prisma Web3 Python

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-green)](https://www.sqlalchemy.org/)
[![AsyncIO](https://img.shields.io/badge/AsyncIO-✓-brightgreen)](https://docs.python.org/3/library/asyncio.html)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**异步 Web3 数据库 ORM** - 基于 SQLAlchemy 2.0 + AsyncIO 的高性能区块链数据访问层

[特性](#-特性) • [安装](#-安装) • [快速开始](#-快速开始) • [文档](#-文档) • [示例](#-示例) • [扩展](#-扩展)

</div>

---

## 📖 目录

- [简介](#-简介)
- [特性](#-特性)
- [架构](#-架构)  
- [安装](#-安装)
- [快速开始](#-快速开始)
- [核心概念](#-核心概念)
- [详细使用](#-详细使用)
- [扩展开发](#-扩展开发)
- [API 参考](#-api-参考)
- [最佳实践](#-最佳实践)
- [常见问题](#-常见问题)

---

## 🎯 简介

**Prisma Web3 Python** 是一个专为 Web3 应用设计的异步数据库 ORM 层，提供：

- 🚀 **高性能异步操作** - 基于 AsyncIO + AsyncPG
- 🔄 **跨链支持** - 统一的数据模型处理多链资产
- 🎨 **简洁的 API** - Repository 模式，开箱即用
- 🔌 **完全可扩展** - 暴露所有底层组件，支持自定义
- 📊 **类型安全** - 完整的类型提示支持
- 🌐 **链名规范化** - 自动处理链名缩写和标准名转换

**适用场景**：
- Web3 数据分析平台
- Token 追踪和监控系统
- 链上信号聚合服务
- DeFi 数据仓库
- NFT 元数据管理

---

## ✨ 特性

### 核心功能

| 功能 | 说明 |
|------|------|
| **异步优先** | 全异步 API，支持高并发操作 |
| **跨链设计** | 单表设计存储跨链 Token，支持多链地址映射 |
| **链名智能化** | 自动规范化链名（`sol` ↔ `solana`，`bsc` ↔ `binance-smart-chain`） |
| **Repository 模式** | 预构建的数据访问层，包含常用查询方法 |
| **灵活查询** | 支持符号、名称、别名、模糊搜索 |
| **批量操作** | 高效的批量插入和更新 |
| **完整扩展性** | 暴露 Models、Repositories、Session 等所有组件 |

### 数据模型

#### Token（代币）
- 跨链 Token 信息存储
- 支持 platforms 字段存储多链地址
- 自动主链选择（按优先级）
- 社交链接、分类、别名支持

#### Signal（信号）
- Token 信号追踪
- 来源、类型、频次统计
- 时间序列分析

#### PreSignal（预信号）
- 早期信号捕获
- 多维度评分（频道呼声、多信号、KOL讨论）
- 状态管理（开放/已转换/已关闭）

#### CryptoNews（加密新闻）
- 多源新闻聚合（TechFlow、ChainCatcher 等）
- 智能实体识别（关联的代币、股票、实体）
- JSONB 高效搜索（支持复杂查询）
- 趋势分析（热门货币、热门实体）

#### AIAnalysisResult（AI 分析结果）
- 统一存储所有来源的 AI 分析（Twitter、News、Telegram 等）
- 代币识别、情感分析、市场影响评估
- 通知管理和状态追踪
- 跨来源统计和趋势分析

---

## 🏗️ 架构

```
┌─────────────────────────────────────────────────────┐
│              Your Application                        │
│  (FastAPI / Flask / Django / Custom)                 │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│          Prisma Web3 Python Package                  │
│                                                      │
│  ┌──────────────┐    ┌──────────────┐              │
│  │ Repositories │◄───│   Models     │              │
│  │  - Token     │    │   - Token    │              │
│  │  - Signal    │    │   - Signal   │              │
│  │  - PreSignal │    │   - PreSignal│              │
│  └──────────────┘    └──────────────┘              │
│         │                    │                       │
│         └────────┬───────────┘                       │
│                  ▼                                   │
│        ┌──────────────────┐                         │
│        │   Database       │                         │
│        │   (Session Mgmt) │                         │
│        └──────────────────┘                         │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
          ┌──────────────────────────┐
          │   PostgreSQL Database    │
          │   (AsyncPG Driver)       │
          └──────────────────────────┘
```

---

## 📦 安装

### 要求

- Python 3.8+
- PostgreSQL 12+
- AsyncPG 驱动

### 使用 pip 安装

\`\`\`bash
# 基础安装
pip install prisma-web3-py

# 从源码安装（开发版）
git clone https://github.com/your-org/prisma-web3.git
cd prisma-web3/python
pip install -e .
\`\`\`

### 数据库设置

1. **创建数据库**：
\`\`\`bash
psql -U postgres
CREATE DATABASE your_database;
\`\`\`

2. **运行迁移**（使用 Prisma）：
\`\`\`bash
cd ../  # 回到项目根目录
npx prisma migrate dev
\`\`\`

3. **配置环境变量**：
\`\`\`bash
# .env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/your_database
\`\`\`

---

## 🚀 快速开始

### 1. 初始化数据库连接

\`\`\`python
import asyncio
from prisma_web3_py import init_db, close_db, get_db

async def main():
    # 初始化数据库连接池
    await init_db()

    try:
        # 你的业务逻辑
        async with get_db() as session:
            # 使用 session 进行数据库操作
            pass
    finally:
        # 关闭连接池
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())
\`\`\`

### 2. 使用 Repository 查询

\`\`\`python
from prisma_web3_py import get_db, TokenRepository

async def query_tokens():
    repo = TokenRepository()

    async with get_db() as session:
        # 获取 Token（支持链名缩写！）
        token = await repo.get_by_address(
            session,
            chain='sol',  # 自动转换为 'solana'
            token_address='oobQ3oX6ubRYMNMahG7VSCe8Z73uaQbAWFn6f22XTgo'
        )

        print(f"Token: {token.symbol} - {token.name}")
        print(f"Chain: {token.chain}")  # 输出: solana

        # 搜索 Tokens
        tokens = await repo.search_tokens(session, "BTC", limit=10)
        for t in tokens:
            print(f"- {t.symbol}: {t.name}")
\`\`\`

### 3. 插入数据

\`\`\`python
from prisma_web3_py import get_db, TokenRepository

async def insert_token():
    repo = TokenRepository()

    async with get_db() as session:
        token_data = {
            "chain": "eth",  # 使用缩写
            "token_address": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
            "symbol": "UNI",
            "name": "Uniswap",
            "coingecko_id": "uniswap",
            "decimals": 18,
            "platforms": {
                "ethereum": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
                "polygon-pos": "0xb33eaad8d922b1083446dc23f610c2567fb5180f"
            }
        }

        token_id = await repo.upsert_token(session, token_data)
        await session.commit()

        print(f"Token saved with ID: {token_id}")
\`\`\`

### 4. 创建数据（重要！）

**⚠️ 注意**: 使用 Repository 的 `create()` 方法，而不是直接创建 Model 对象！

\`\`\`python
from prisma_web3_py import get_db, PreSignalRepository

async def create_pre_signal():
    repo = PreSignalRepository()

    async with get_db() as session:
        # ✅ 正确：使用 repository.create()，自动处理 chain 标准化
        pre_signal = await repo.create(
            session,
            source="jin_vip",
            chain="sol",  # 自动转换为 'solana'
            token_address="oobQ3oX6ubRYMNMahG7VSCe8Z73uaQbAWFn6f22XTgo",
            signal_type="jin_vip",
            channel_calls=5,
            multi_signals=3,
            kol_discussions=2,
            token_narrative="Some description"
        )

        if pre_signal:
            await session.commit()
            print(f"✅ Created PreSignal ID: {pre_signal.id}")
        else:
            print("❌ Failed to create PreSignal")

# ❌ 错误示例：不要直接创建 Model 对象！
async def wrong_way():
    from prisma_web3_py import PreSignal

    async with get_db() as session:
        # ❌ 这样会导致外键错误，因为 chain 没有标准化！
        pre_signal = PreSignal(
            source="jin_vip",
            chain="sol",  # 不会自动转换，导致外键约束失败
            token_address="...",
            signal_type="jin_vip"
        )
        session.add(pre_signal)  # ❌ 会报错！
\`\`\`

**为什么必须使用 Repository？**

1. **自动链名标准化**: Repository 会自动将 `'sol'` 转换为 `'solana'`
2. **外键约束**: Token 表存储的是标准名，直接使用缩写会违反外键约束
3. **数据验证**: Repository 提供额外的数据验证和错误处理
4. **一致性**: 确保所有数据以统一格式存储

### 5. 使用 CryptoNews（加密新闻）

\`\`\`python
from datetime import datetime
from prisma_web3_py import get_db, CryptoNewsRepository

async def crypto_news_example():
    repo = CryptoNewsRepository()

    async with get_db() as session:
        # 1. 导入新闻数据（从 API）
        api_data = {
            "title": "OKX 将上线 SEI (Sei)，2Z (DoubleZero)现货交易",
            "category": 1,
            "source": "TechFlow",
            "content": "11 月 14 日，据官方公告...",
            "matchedCurrencies": [{"name": "SEI"}, {"name": "2Z"}],
            "entityList": ["OKX", "SEI", "2Z"],
            "createTime": "1763089364248"  # 毫秒时间戳
        }

        # 转换时间戳并创建新闻
        news_time = datetime.fromtimestamp(int(api_data["createTime"]) / 1000)
        news = await repo.create_news(
            session,
            title=api_data["title"],
            category=api_data["category"],
            source=api_data["source"],
            content=api_data["content"],
            matched_currencies=api_data.get("matchedCurrencies", []),
            entity_list=api_data.get("entityList", []),
            news_created_at=news_time
        )
        await session.commit()

        # 2. 按加密货币搜索新闻
        btc_news = await repo.search_by_currency(session, "BTC", hours=24)
        print(f"关于 BTC 的新闻: {len(btc_news)} 条")

        # 3. 按实体搜索新闻
        okx_news = await repo.search_by_entity(session, "OKX", hours=24)
        print(f"提到 OKX 的新闻: {len(okx_news)} 条")

        # 4. 获取热门货币
        trending = await repo.get_trending_currencies(session, hours=24, limit=10)
        print("热门货币:")
        for item in trending[:5]:
            print(f"  {item['currency']}: {item['mentions']} 次提及")

        # 5. 获取热门实体
        trending_entities = await repo.get_trending_entities(session, hours=24)
        print("热门实体:")
        for item in trending_entities[:5]:
            print(f"  {item['entity']}: {item['mentions']} 次提及")

        # 6. 搜索标签
        defi_news = await repo.search_by_tag(session, "defi", hours=24)
        print(f"DeFi 相关新闻: {len(defi_news)} 条")
\`\`\`

#### 5.1 新闻去重机制（重要！）

**⚠️ CryptoNews 使用双层去重机制防止重复导入：**

1. **数据库唯一约束**：`(source, source_link)` 防止相同来源的重复文章
2. **内容哈希**：`content_hash` (SHA256) 检测跨来源的相同内容

**方式 1: 使用 UPSERT 自动处理重复**（推荐）

\`\`\`python
from datetime import datetime
from prisma_web3_py import get_db, CryptoNewsRepository

async def import_news_with_upsert():
    """使用 UPSERT 优雅处理重复 - 推荐方式"""
    repo = CryptoNewsRepository()

    async with get_db() as session:
        # ✅ 使用 upsert_news() - 自动处理重复
        # 如果已存在 (source, source_link) → 更新
        # 如果不存在 → 插入
        news = await repo.upsert_news(
            session,
            title="OKX 将上线 SEI",
            category=1,
            source="TechFlow",
            source_link="https://techflow.com/article/123",  # 用于去重
            content="新闻内容...",
            matched_currencies=[{"name": "SEI"}],
            entity_list=["OKX", "SEI"],
            news_created_at=datetime.fromtimestamp(1763089364)
        )
        await session.commit()

        # 第二次导入相同链接 → 自动更新，不会报错
        news2 = await repo.upsert_news(
            session,
            title="【更新】OKX 将上线 SEI",  # 更新标题
            source="TechFlow",
            source_link="https://techflow.com/article/123",  # 相同链接
            content="更新的内容...",
            tags=["updated"]  # 添加标签
        )
        await session.commit()

        print(f"相同 ID: {news.id == news2.id}")  # True - 是同一条记录
\`\`\`

**方式 2: 批量导入自动去重**

\`\`\`python
async def batch_import_with_deduplication():
    """批量导入，自动跳过重复"""
    repo = CryptoNewsRepository()

    # API 返回的新闻列表（可能包含重复）
    api_response = {
        "list": [
            {"title": "News 1", "source": "TechFlow", "sourceLink": "https://...", ...},
            {"title": "News 2", "source": "ChainCatcher", "sourceLink": "https://...", ...},
            {"title": "News 1 Duplicate", "source": "TechFlow", "sourceLink": "https://...", ...},  # 重复!
        ]
    }

    async with get_db() as session:
        created_count = 0
        updated_count = 0

        for item in api_response["list"]:
            # upsert 会自动处理重复
            news = await repo.upsert_news(
                session,
                title=item["title"],
                source=item["source"],
                source_link=item.get("sourceLink"),
                content=item["content"],
                matched_currencies=item.get("matchedCurrencies", []),
                entity_list=item.get("entityList", []),
                news_created_at=datetime.fromtimestamp(int(item["createTime"]) / 1000)
            )

            if news:
                created_count += 1

        await session.commit()
        print(f"✅ 处理 {created_count} 条新闻（自动去重）")
\`\`\`

**方式 3: 内容级别去重检查（可选）**

\`\`\`python
from prisma_web3_py import CryptoNews

async def import_with_content_check():
    """使用 content_hash 检测跨来源的重复内容"""
    repo = CryptoNewsRepository()

    async with get_db() as session:
        content = "重要新闻内容..."

        # 1. 生成内容哈希
        content_hash = CryptoNews.generate_content_hash(content)

        # 2. 检查是否已存在相同内容（即使来源不同）
        duplicate = await repo.check_duplicate_by_hash(session, content_hash)

        if duplicate:
            print(f"⚠️  发现重复内容！")
            print(f"   已存在于：{duplicate.source}")
            print(f"   原链接：{duplicate.source_link}")
            print(f"   决策：跳过导入")
            return None

        # 3. 没有重复，安全导入
        news = await repo.create_news(
            session,
            title="独特的新闻",
            source="NewSource",
            content=content,
            source_link="https://newsource.com/article/456"
        )
        await session.commit()
        return news
\`\`\`

**去重机制说明**

| 去重级别 | 实现方式 | 检测范围 | 使用场景 |
|---------|---------|---------|---------|
| **URL 级别** | `(source, source_link)` 唯一约束 | 相同来源 + 相同链接 | 防止重复导入同一篇文章 |
| **内容级别** | `content_hash` (SHA256) 查询 | 跨来源的相同内容 | 发现转载/复制的内容 |

**错误处理示例**

\`\`\`python
from sqlalchemy.exc import IntegrityError

async def import_with_error_handling():
    repo = CryptoNewsRepository()

    async with get_db() as session:
        try:
            # 使用 create_news 会在重复时抛出异常
            news = await repo.create_news(
                session,
                source="TechFlow",
                source_link="https://...",  # 如果重复会报错
                content="...",
                title="..."
            )
            await session.commit()
        except IntegrityError:
            await session.rollback()
            print("⚠️  新闻已存在，跳过")

            # 或者改用 upsert 更新
            news = await repo.upsert_news(session, ...)
            await session.commit()
\`\`\`

**最佳实践建议**

1. ✅ **批量导入使用 `upsert_news()`** - 自动处理重复，无需异常处理
2. ✅ **有 `source_link` 时依赖唯一约束** - 数据库级别保证
3. ✅ **无 `source_link` 时使用内容哈希** - 通过 `check_duplicate_by_hash()` 检查
4. ✅ **定期清理旧数据** - `content_hash` 可用于发现完全相同的历史新闻

### 6. 使用 AIAnalysisResult（AI 分析结果统一存储）

**AIAnalysisResult** 是统一存储所有 AI 分析结果的表，支持 Twitter、News、Telegram 等多种来源的分析结果。

#### 核心功能

- 📊 **统一存储**：所有来源的 AI 分析结果存储在同一个表
- 🎯 **代币识别**：自动识别并存储提及的代币（JSONB 存储）
- 😊 **情感分析**：positive / negative / neutral + 置信度
- 📈 **市场影响**：bullish / bearish / neutral（新闻特有）
- 🔔 **通知管理**：should_notify + notified_at 追踪通知状态
- 📊 **趋势统计**：情感分布、代币提及排行、作者统计

#### 6.1 创建 Twitter 分析结果

\`\`\`python
from datetime import datetime
from prisma_web3_py import get_db, AIAnalysisRepository

async def save_twitter_analysis():
    """保存 Twitter 分析结果"""
    repo = AIAnalysisRepository()

    async with get_db() as session:
        # 从 Twitter Agent 获取分析结果后保存
        analysis_result = await repo.create_twitter_analysis(
            session,
            tweet_id="1234567890",
            tweet_text="BTC is going to the moon! 🚀",
            user_name="CryptoWhale",
            user_group="KOL",
            tweet_link="https://twitter.com/CryptoWhale/status/1234567890",
            tokens=[
                {"symbol": "BTC", "name": "Bitcoin", "chain": "bitcoin"}
            ],
            analysis={
                "sentiment": "positive",
                "confidence": 0.85,
                "summary": "Bullish sentiment on Bitcoin",
                "reasoning": "Strong positive language with moon emoji"
            },
            should_notify=True,
            model_name="deepseek/deepseek-v3.2-exp",
            analysis_version="v1.0"
        )
        await session.commit()

        print(f"✅ Saved Twitter analysis: ID={analysis_result.id}")
\`\`\`

#### 6.2 创建新闻分析结果

\`\`\`python
async def save_news_analysis():
    """保存新闻分析结果"""
    repo = AIAnalysisRepository()

    async with get_db() as session:
        # 从 News Agent 获取分析结果后保存
        analysis_result = await repo.create_news_analysis(
            session,
            news_id=12345,
            news_title="Binance Lists New Token XYZ",
            news_content="Binance announced the listing of XYZ token...",
            source="CoinDesk",
            source_link="https://coindesk.com/article/12345",
            matched_currencies=["XYZ", "BNB"],
            analysis_state={
                "category": "exchange_listing",
                "importance": "high",
                "market_impact": "bullish",
                "event_type": "bullish_event",
                "intensity": 0.8,
                "should_notify": True,
                "analysis": {
                    "sentiment": "positive",
                    "confidence": 0.9,
                    "summary": "Major exchange listing for XYZ",
                    "reasoning": "Binance listing typically drives significant price action",
                    "key_points": [
                        "Binance is a top-tier exchange",
                        "Listing announcements are bullish catalysts",
                        "XYZ gains exposure to millions of users"
                    ]
                }
            }
        )
        await session.commit()

        print(f"✅ Saved news analysis: ID={analysis_result.id}")
\`\`\`

#### 6.3 查询和统计

\`\`\`python
async def query_ai_analyses():
    """AI 分析结果查询示例"""
    repo = AIAnalysisRepository()

    async with get_db() as session:
        # 1. 获取最近 24 小时的所有分析
        all_analyses = await repo.get_recent_analyses(session, hours=24)
        print(f"📊 Total analyses (24h): {len(all_analyses)}")

        # 2. 只看 Twitter 分析
        twitter_analyses = await repo.get_recent_analyses(
            session,
            source_type='twitter',
            hours=24,
            limit=100
        )
        print(f"🐦 Twitter analyses: {len(twitter_analyses)}")

        # 3. 只看新闻分析
        news_analyses = await repo.get_recent_analyses(
            session,
            source_type='news',
            hours=24,
            limit=100
        )
        print(f"📰 News analyses: {len(news_analyses)}")

        # 4. 获取待通知的内容
        pending = await repo.get_pending_notifications(session)
        print(f"🔔 Pending notifications: {len(pending)}")

        # 5. 情感统计（所有来源）
        sentiment_stats = await repo.get_sentiment_stats(session, hours=24)
        print(f"😊 Sentiment distribution: {sentiment_stats}")
        # 输出: {'positive': 45, 'neutral': 120, 'negative': 35}

        # 6. Twitter 情感统计
        twitter_sentiment = await repo.get_sentiment_stats(
            session,
            source_type='twitter',
            hours=24
        )
        print(f"🐦 Twitter sentiment: {twitter_sentiment}")

        # 7. 代币提及排行
        top_tokens = await repo.get_token_mentions(session, hours=24, limit=10)
        print("\n🪙 Top mentioned tokens (24h):")
        for token in top_tokens:
            print(f"  {token['symbol']}: {token['mentions']} mentions")

        # 8. 作者统计（Twitter KOL）
        top_authors = await repo.get_author_stats(
            session,
            source_type='twitter',
            hours=24,
            limit=10
        )
        print("\n👤 Top Twitter authors:")
        for author in top_authors:
            print(
                f"  {author['author']}: {author['total']} tweets "
                f"(+{author['positive']} ⚪{author['neutral']} -{author['negative']})"
            )

        # 9. 综合统计
        stats = await repo.get_analysis_stats(session, hours=24)
        print("\n📈 Analysis Statistics (24h):")
        print(f"  Total: {stats['total_analyses']}")
        print(f"  By source: {stats['by_source']}")
        print(f"  Should notify: {stats['should_notify']}")
        print(f"  Notified: {stats['notified']}")
        print(f"  Pending: {stats['pending_notifications']}")

        # 10. 按特定代币搜索
        btc_analyses = await repo.search_by_token(
            session,
            token_symbol='BTC',
            hours=24,
            limit=50
        )
        print(f"\n🔍 BTC mentions: {len(btc_analyses)}")
\`\`\`

#### 6.4 通知管理

\`\`\`python
async def manage_notifications():
    """管理通知状态"""
    repo = AIAnalysisRepository()

    async with get_db() as session:
        # 1. 获取待通知列表
        pending = await repo.get_pending_notifications(session, source_type='twitter')

        for analysis in pending:
            print(f"Processing: {analysis.summary[:50]}...")

            # 2. 发送通知（你的通知逻辑）
            await send_notification(analysis)

            # 3. 标记为已通知
            success = await repo.mark_as_notified(session, analysis.id)
            if success:
                print(f"  ✅ Marked as notified")

        await session.commit()
\`\`\`

#### 6.5 使用场景

| 使用场景 | 方法 | 说明 |
|---------|------|------|
| **保存 Twitter 分析** | `create_twitter_analysis()` | 从 TwitterAgent 保存分析结果 |
| **保存新闻分析** | `create_news_analysis()` | 从 NewsAgent 保存分析结果 |
| **查询特定来源** | `get_by_source()` | 按 source_type + source_id 查询 |
| **获取最近分析** | `get_recent_analyses()` | 支持按来源类型过滤 |
| **情感统计** | `get_sentiment_stats()` | 跨来源或单一来源 |
| **代币热度** | `get_token_mentions()` | JSONB 查询，按提及次数排序 |
| **KOL 统计** | `get_author_stats()` | 作者发文质量分析 |
| **通知队列** | `get_pending_notifications()` | 获取待发送通知 |
| **标记已通知** | `mark_as_notified()` | 更新通知状态 |

#### 6.6 设计优势

✅ **统一管理**: 所有 AI 分析结果集中管理，便于跨来源统计和对比
✅ **灵活扩展**: 支持 Twitter、News、Telegram、Discord 等多种来源
✅ **JSONB 查询**: 高效的代币提及统计和趋势分析
✅ **防重复**: `(source_type, source_id)` 唯一约束
✅ **版本追踪**: 支持模型迭代和 A/B 测试（`analysis_version`）
✅ **通知管理**: 完整的通知状态追踪

### 7. 使用 Models 直接查询

\`\`\`python
from prisma_web3_py import get_db, Token, Signal
from sqlalchemy import select, func

async def custom_query():
    async with get_db() as session:
        # 自定义复杂查询
        stmt = (
            select(Token, func.count(Signal.id).label('signal_count'))
            .join(Signal, (Token.chain == Signal.chain) &
                          (Token.token_address == Signal.token_address))
            .group_by(Token.id)
            .order_by(func.count(Signal.id).desc())
            .limit(10)
        )

        result = await session.execute(stmt)
        for token, count in result:
            print(f"{token.symbol}: {count} signals")
\`\`\`

---

## 💡 核心概念

### 1. Repository Pattern（仓储模式）

Repository 是数据访问层的抽象，隐藏了 SQL 查询细节。

所有 Repository 都继承自 `BaseRepository`，提供基础 CRUD 方法。

### 2. 链名规范化

所有 Repository 自动处理链名转换：

\`\`\`python
# 这些都可以工作
await repo.get_by_address(session, "sol", "address")   # 缩写
await repo.get_by_address(session, "eth", "address")   # 缩写
await repo.get_by_address(session, "solana", "address")  # 标准名

# Repository 会自动转换为 CoinGecko 标准名存入数据库
\`\`\`

支持的链：Ethereum (`eth`), BSC (`bsc`), Solana (`sol`), Polygon (`poly`), Arbitrum (`arb`), Base (`base`) 等 18+ 条链。

### 3. 跨链 Token 设计

Token 表采用单表设计存储跨链资产：

\`\`\`python
{
    "chain": "ethereum",        # 主链（优先级最高）
    "token_address": "0x...",   # 主链地址
    "symbol": "UNI",
    "platforms": {              # 跨链地址映射 (JSONB)
        "ethereum": "0x...",
        "polygon-pos": "0x...",
        "arbitrum-one": "0x..."
    }
}
\`\`\`

### 4. 异步 Context Manager

使用 `get_db()` 自动管理 Session 生命周期：

\`\`\`python
async with get_db() as session:
    # session 自动创建
    result = await repo.get_all(session)
    await session.commit()
    # session 自动关闭
\`\`\`

---

## 📚 详细使用

### 使用 get_db() 和 Repository 的完整指南

#### 基础模式：使用 Context Manager

\`\`\`python
from prisma_web3_py import get_db, TokenRepository

async def basic_usage():
    # 1. 创建 repository 实例
    repo = TokenRepository()

    # 2. 使用 get_db() 获取 session
    async with get_db() as session:
        # 3. 执行数据库操作
        token = await repo.get_by_address(
            session,
            chain='sol',  # 自动标准化
            token_address='xxx'
        )

        # 4. 提交事务
        await session.commit()
        # session 自动关闭
\`\`\`

#### 完整的增删改查示例

\`\`\`python
from prisma_web3_py import (
    get_db,
    TokenRepository,
    SignalRepository,
    PreSignalRepository
)

async def crud_examples():
    token_repo = TokenRepository()
    signal_repo = SignalRepository()
    pre_signal_repo = PreSignalRepository()

    async with get_db() as session:
        # ========== CREATE ==========

        # 方式1: 使用 repository.create()（推荐）
        pre_signal = await pre_signal_repo.create(
            session,
            source="source1",
            chain="sol",  # ✅ 自动转换为 'solana'
            token_address="xxx",
            signal_type="type1",
            channel_calls=5
        )

        # 方式2: 使用专用方法
        signal = await signal_repo.upsert_signal(
            session,
            chain="eth",  # ✅ 自动转换为 'ethereum'
            token_address="0x123",
            source="source1",
            signal_type="kol"
        )

        # ========== READ ==========

        # 单个查询
        token = await token_repo.get_by_address(
            session,
            chain='bsc',  # ✅ 自动转换为 'binance-smart-chain'
            token_address='0x456'
        )

        # 批量查询
        recent_tokens = await token_repo.get_recent_tokens(
            session,
            chain='sol',
            limit=100
        )

        # 搜索
        search_results = await token_repo.search_tokens(
            session,
            search_term='BTC',
            limit=20
        )

        # ========== UPDATE ==========

        # 使用 BaseRepository 的 update_by_id
        success = await token_repo.update_by_id(
            session,
            id=token.id,
            symbol='NEW_SYMBOL'
        )

        # 或者使用 upsert
        token_id = await token_repo.upsert_token(
            session,
            {
                'chain': 'eth',
                'token_address': '0x789',
                'symbol': 'UNI',
                'name': 'Uniswap'
            }
        )

        # ========== DELETE ==========

        success = await token_repo.delete_by_id(session, id=123)

        # 提交所有更改
        await session.commit()
\`\`\`

#### 处理第三方数据的正确方式

当你从外部源（API、消息队列等）接收数据时：

\`\`\`python
async def handle_external_data(data: dict):
    """
    处理外部数据的正确方式

    Args:
        data: 来自第三方的数据，例如：
        {
            "source": "jin_vip",
            "chain": "sol",  # 可能是缩写
            "token_address": "xxx",
            "signal_type": "jin_vip",
            "signals": {
                "channel_calls": 5,
                "multi_signals": 3,
                "kol_discussions": 2
            },
            "description": "Token narrative..."
        }
    """
    pre_signal_repo = PreSignalRepository()

    # 准备数据
    pre_signal_data = {
        "source": data.get("source"),
        "chain": data.get("chain"),  # 保持原样，repository 会处理
        "token_address": data.get("token_address"),
        "signal_type": data.get("signal_type"),
    }

    # 添加 signals 数据
    signals = data.get("signals", {})
    if signals:
        pre_signal_data.update({
            "channel_calls": signals.get("channel_calls", 0),
            "multi_signals": signals.get("multi_signals", 0),
            "kol_discussions": signals.get("kol_discussions", 0),
        })

    # 添加代币叙事
    if data.get("description"):
        pre_signal_data["token_narrative"] = data["description"]

    # ✅ 正确方式：使用 repository.create()
    async with get_db() as session:
        pre_signal = await pre_signal_repo.create(
            session,
            **{k: v for k, v in pre_signal_data.items() if v is not None}
        )

        if pre_signal:
            await session.commit()
            print(f"✅ Created PreSignal ID: {pre_signal.id}")
            return pre_signal
        else:
            print("❌ Failed to create PreSignal")
            return None

    # ❌ 错误方式：直接创建 Model 对象
    # from prisma_web3_py import PreSignal
    # async with get_db() as session:
    #     pre_signal = PreSignal(**pre_signal_data)  # ❌ chain 不会标准化！
    #     session.add(pre_signal)
    #     await session.commit()  # ❌ 外键约束错误！
\`\`\`

#### 批量操作（高性能批处理）

TokenRepository 提供了专门的批处理方法，性能比循环操作快 **10-100 倍**：

\`\`\`python
async def batch_operations():
    """批处理操作示例 - 高性能！"""
    repo = TokenRepository()

    async with get_db() as session:
        # ========== 1. 批量 UPSERT（推荐） ==========
        tokens_data = [
            {
                "chain": "eth",  # 自动标准化为 'ethereum'
                "token_address": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
                "symbol": "UNI",
                "name": "Uniswap",
                "decimals": 18
            },
            {
                "chain": "bsc",  # 自动标准化为 'binance-smart-chain'
                "token_address": "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82",
                "symbol": "CAKE",
                "name": "PancakeSwap"
            },
            {
                "chain": "sol",  # 自动标准化为 'solana'
                "token_address": "oobQ3oX6ubRYMNMahG7VSCe8Z73uaQbAWFn6f22XTgo",
                "symbol": "HAWK",
                "name": "Hawk Token"
            }
        ]

        # 批量 UPSERT - 使用 PostgreSQL ON CONFLICT，超快！
        result = await repo.batch_upsert_tokens(session, tokens_data)
        await session.commit()

        print(f"✅ 批量 UPSERT 完成:")
        print(f"   处理: {result['total_processed']} 条")
        print(f"   成功: {result['inserted']} 条")
        print(f"   失败: {result['failed']} 条")

        # ========== 2. 批量按地址查询 ==========
        addresses = [
            ('eth', '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984'),  # UNI
            ('bsc', '0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82'),  # CAKE
            ('sol', 'oobQ3oX6ubRYMNMahG7VSCe8Z73uaQbAWFn6f22XTgo')   # HAWK
        ]

        tokens = await repo.batch_get_by_addresses(session, addresses)
        print(f"\n✅ 批量查询: 找到 {len(tokens)} 个 tokens")

        # ========== 3. 批量按符号搜索 ==========
        symbols = ['BTC', 'ETH', 'SOL', 'UNI', 'CAKE']
        tokens = await repo.batch_search_by_symbols(session, symbols, exact=True)
        print(f"\n✅ 批量符号搜索: 找到 {len(tokens)} 个 tokens")

        for token in tokens:
            print(f"   - {token.symbol}: {token.name} ({token.chain})")

        # ========== 4. 批量搜索（分组结果） ==========
        search_terms = ['bitcoin', 'ethereum', 'solana']
        results = await repo.batch_search_tokens(
            session,
            search_terms,
            limit_per_term=3
        )

        print(f"\n✅ 批量搜索（分组）:")
        for term, token_list in results.items():
            print(f"   '{term}': {len(token_list)} 个结果")
            for token in token_list:
                print(f"      - {token.symbol}: {token.name}")
\`\`\`

**性能对比**：

| 操作 | 循环方式 | 批处理方式 | 性能提升 |
|------|---------|-----------|---------|
| 查询 100 个 tokens | ~2-5 秒 | ~0.05 秒 | **40-100x** |
| UPSERT 100 个 tokens | ~3-8 秒 | ~0.1 秒 | **30-80x** |
| 搜索 10 个符号 | ~0.5-1 秒 | ~0.05 秒 | **10-20x** |

**最佳实践**：
- ✅ **批量操作优先**：超过 5 条记录时，使用批处理方法
- ✅ **链名自动标准化**：所有批处理方法都支持链名缩写
- ✅ **错误处理**：`batch_upsert_tokens` 返回详细的成功/失败统计
- ✅ **单次提交**：批处理完成后一次性 commit，减少数据库往返

#### 错误处理

\`\`\`python
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

async def error_handling():
    repo = PreSignalRepository()

    async with get_db() as session:
        try:
            pre_signal = await repo.create(
                session,
                source="source1",
                chain="sol",
                token_address="xxx",
                signal_type="type1"
            )

            await session.commit()
            return pre_signal

        except IntegrityError as e:
            # 外键约束、唯一约束违反
            await session.rollback()
            print(f"Integrity error: {e}")
            raise

        except SQLAlchemyError as e:
            # 其他数据库错误
            await session.rollback()
            print(f"Database error: {e}")
            raise

        except Exception as e:
            # 其他错误
            await session.rollback()
            print(f"Unexpected error: {e}")
            raise
\`\`\`

### 主要操作概览

- ✅ **Token 查询、创建、更新** - 使用 `TokenRepository`
- ✅ **Token 批处理操作** - 使用 `TokenRepository` 批处理方法（性能提升 10-100 倍）
- ✅ **Signal 管理** - 使用 `SignalRepository`
- ✅ **PreSignal 处理** - 使用 `PreSignalRepository`
- ✅ **自定义查询** - 直接使用 Models + SQLAlchemy
- ✅ **批量导入** - 使用 `TokenImporter`

详细 API 文档请参考 [API 参考](#-api-参考) 部分。

---

## 🔌 扩展开发

Prisma Web3 Python 完全可扩展。详细指南请参考 [EXTENSION_GUIDE.md](EXTENSION_GUIDE.md)。

### 快速示例

#### 1. 继承 BaseRepository

\`\`\`python
from prisma_web3_py import BaseRepository, Token

class MyTokenRepository(BaseRepository[Token]):
    async def get_high_value_tokens(self, session, min_supply: float):
        # 自定义查询
        pass
\`\`\`

#### 2. 使用 Models 直接查询

\`\`\`python
from prisma_web3_py import get_db, Token
from sqlalchemy import select

async with get_db() as session:
    stmt = select(Token).where(Token.symbol == 'BTC')
    result = await session.execute(stmt)
\`\`\`

#### 3. 扩展现有 Repository

\`\`\`python
from prisma_web3_py import TokenRepository

class ExtendedTokenRepository(TokenRepository):
    async def new_feature(self, session):
        # 添加新方法
        pass
\`\`\`

---

## 📖 API 参考

### 核心组件

\`\`\`python
from prisma_web3_py import (
    # Core
    Base, get_db, init_db, close_db, AsyncSessionLocal,

    # Models
    Token, Signal, PreSignal, SignalStatus, CryptoNews, AIAnalysisResult,

    # Repositories
    BaseRepository, TokenRepository, SignalRepository, PreSignalRepository,
    CryptoNewsRepository, AIAnalysisRepository,

    # Utils
    TokenImporter, ChainConfig
)
\`\`\`

### TokenRepository 主要方法

**单个查询**:
- `get_by_address(session, chain, token_address)` - 按链和地址查询
- `search_tokens(session, search_term, chain, limit)` - 搜索
- `search_by_symbol(session, symbol, exact)` - 按符号搜索
- `search_by_name(session, name, exact)` - 按名称搜索
- `search_by_alias(session, alias)` - 按别名搜索（使用 JSONB @> 操作符）
- `fuzzy_search(session, text, threshold, limit)` - 模糊搜索（支持 pg_trgm）
- `get_recent_tokens(session, chain, limit)` - 最近创建
- `get_recently_updated_tokens(session, hours, chain, limit)` - 最近更新

**批处理操作**（高性能）:
- `batch_get_by_addresses(session, addresses)` - 批量按地址获取（比循环快 10-100 倍）
- `batch_search_by_symbols(session, symbols, exact)` - 批量按符号搜索
- `batch_search_tokens(session, search_terms, chain, limit_per_term)` - 批量搜索（返回分组结果）
- `batch_upsert_tokens(session, tokens_data)` - 批量插入/更新（使用 PostgreSQL UPSERT）

**单个写入**:
- `upsert_token(session, token_data)` - 插入或更新单个 token

### CryptoNewsRepository 主要方法

**创建和去重**（重要！）:
- `upsert_news(session, title, source, content, source_link, ...)` - 插入或更新新闻（推荐）
- `create_news(session, title, category, source, content, ...)` - 创建新闻（重复时抛异常）
- `check_duplicate_by_hash(session, content_hash)` - 检查内容级别重复

**基础查询**:
- `get_recent_news(session, hours, source, sector, limit)` - 获取最近新闻
- `get_news_by_source(session, source, hours, limit)` - 按来源查询
- `get_news_by_sector(session, sector, hours, limit)` - 按行业查询

**JSONB 高级查询**（使用 PostgreSQL @> 操作符）:
- `search_by_currency(session, currency_name, hours, limit)` - 按加密货币搜索
- `search_by_entity(session, entity_name, hours, limit)` - 按实体搜索
- `search_by_tag(session, tag, hours, limit)` - 按标签搜索

**趋势分析**（使用 jsonb_array_elements）:
- `get_trending_currencies(session, hours, limit)` - 获取热门货币
- `get_trending_entities(session, hours, limit)` - 获取热门实体

**其他**:
- `search_news(session, search_term, search_in_content, limit)` - 关键词搜索
- `get_news_statistics(session, hours)` - 统计信息

**去重机制**:
- **唯一约束**: `(source, source_link)` 防止重复导入
- **内容哈希**: `content_hash` (SHA256) 用于跨来源去重
- **推荐**: 使用 `upsert_news()` 自动处理重复

### AIAnalysisRepository 主要方法

**创建方法**:
- `create_twitter_analysis(session, tweet_id, tweet_text, user_name, ...)` - 创建 Twitter 分析结果
- `create_news_analysis(session, news_id, news_title, news_content, ...)` - 创建新闻分析结果

**查询方法**:
- `get_by_source(session, source_type, source_id)` - 按来源查询特定分析
- `get_recent_analyses(session, source_type, hours, limit)` - 获取最近分析（可按来源过滤）
- `get_pending_notifications(session, source_type)` - 获取待通知列表
- `search_by_token(session, token_symbol, hours, limit)` - 按代币搜索分析（JSONB @> 查询）

**统计方法**:
- `get_sentiment_stats(session, source_type, hours)` - 情感统计（按来源）
- `get_token_mentions(session, hours, limit)` - 代币提及排行（JSONB 数组展开）
- `get_author_stats(session, source_type, hours, limit)` - 作者发文统计
- `get_analysis_stats(session, hours)` - 综合统计信息

**通知管理**:
- `mark_as_notified(session, analysis_id)` - 标记为已通知

**特点**:
- ✅ **统一管理**: 跨来源（Twitter、News、Telegram）统一存储
- ✅ **JSONB 查询**: 高效的代币提及和趋势分析
- ✅ **防重复**: `(source_type, source_id)` 唯一约束
- ✅ **版本追踪**: 支持模型迭代（`analysis_version`）

完整 API 请查看源码注释。

---

## 🎯 最佳实践

### 1. 始终使用 Repository 创建数据

✅ **推荐**：
\`\`\`python
# 使用 repository.create()
repo = PreSignalRepository()
async with get_db() as session:
    result = await repo.create(session, chain='sol', ...)
    await session.commit()
\`\`\`

❌ **避免**：
\`\`\`python
# 直接创建 Model 对象
from prisma_web3_py import PreSignal
pre_signal = PreSignal(chain='sol', ...)  # 不会标准化 chain
session.add(pre_signal)
\`\`\`

### 2. 使用 Context Manager

✅ **推荐**：
\`\`\`python
async with get_db() as session:
    result = await repo.get_all(session)
    await session.commit()
    # session 自动关闭，连接归还到连接池
\`\`\`

❌ **避免**：
\`\`\`python
session = AsyncSessionLocal()  # 手动管理
result = await repo.get_all(session)
await session.close()  # 容易忘记
\`\`\`

### 3. 正确的错误处理

✅ **推荐**：
\`\`\`python
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

async with get_db() as session:
    try:
        result = await repo.create(session, **data)
        await session.commit()
        return result
    except IntegrityError as e:
        # 外键、唯一约束错误
        await session.rollback()
        logger.error(f"Integrity error: {e}")
        raise
    except SQLAlchemyError as e:
        # 其他数据库错误
        await session.rollback()
        logger.error(f"Database error: {e}")
        raise
\`\`\`

### 4. 使用链名缩写

✅ **推荐**：
\`\`\`python
# 使用缩写，更简洁
await repo.get_by_address(session, 'sol', 'address')
await repo.get_by_address(session, 'eth', 'address')
await repo.get_by_address(session, 'bsc', 'address')
\`\`\`

✅ **也可以**：
\`\`\`python
# 使用标准名，更明确
await repo.get_by_address(session, 'solana', 'address')
await repo.get_by_address(session, 'ethereum', 'address')
\`\`\`

### 5. 处理外部数据

当接收外部数据（API、消息队列）时：

✅ **推荐**：
\`\`\`python
async def handle_external_data(data: dict):
    repo = PreSignalRepository()
    async with get_db() as session:
        # repository 会自动标准化 chain
        result = await repo.create(session, **data)
        await session.commit()
        return result
\`\`\`

❌ **避免**：
\`\`\`python
from prisma_web3_py import PreSignal
async with get_db() as session:
    # 外部 data['chain'] 可能是 'sol'，不会被标准化
    obj = PreSignal(**data)
    session.add(obj)  # ❌ 可能导致外键错误
\`\`\`

### 6. 批量操作的事务处理

✅ **推荐**：
\`\`\`python
async with get_db() as session:
    for item in items:
        await repo.create(session, **item)
    # 一次性提交所有操作
    await session.commit()
\`\`\`

❌ **避免**：
\`\`\`python
# 每个操作都单独提交
for item in items:
    async with get_db() as session:
        await repo.create(session, **item)
        await session.commit()  # 性能低下
\`\`\`

---

## ❓ 常见问题

### Q1: 为什么会出现外键约束错误？

**A**: 最常见的原因是直接创建 Model 对象而不是使用 Repository：

\`\`\`python
# ❌ 错误：直接创建对象
from prisma_web3_py import PreSignal
pre_signal = PreSignal(chain='sol', ...)  # chain 不会标准化
session.add(pre_signal)  # ❌ 外键错误！

# ✅ 正确：使用 repository
from prisma_web3_py import PreSignalRepository
repo = PreSignalRepository()
pre_signal = await repo.create(session, chain='sol', ...)  # ✅ 自动标准化
\`\`\`

**解决方案**: 始终使用 Repository 的 `create()` 方法或专用方法来创建数据。

### Q2: 如何处理链名？

**A**: 所有 Repository 都自动规范化链名。你可以使用缩写（`sol`, `eth`, `bsc`）或标准名（`solana`, `ethereum`, `binance-smart-chain`），数据库会统一存储为 CoinGecko 标准名。

**链名映射表**:
- `sol` → `solana`
- `eth` → `ethereum`
- `bsc` → `binance-smart-chain`
- `poly` → `polygon-pos`
- `arb` → `arbitrum-one`
- `base` → `base`
- 等 18+ 条链...

### Q3: 可以直接使用 SQLAlchemy Model 吗？

**A**: **查询可以，创建不建议**。

\`\`\`python
# ✅ 查询：可以直接使用 Model
from prisma_web3_py import Token
from sqlalchemy import select

stmt = select(Token).where(Token.symbol == 'BTC')
result = await session.execute(stmt)

# ❌ 创建：不要直接创建 Model
token = Token(chain='sol', ...)  # 不会标准化
session.add(token)  # 可能导致错误

# ✅ 创建：使用 Repository
repo = TokenRepository()
token = await repo.create(session, chain='sol', ...)  # 自动标准化
\`\`\`

### Q4: 如何执行自定义查询？

**A**: 三种方式：
1. 直接使用 Models + SQLAlchemy（仅查询）
2. 继承 BaseRepository（添加新方法）
3. 扩展现有 Repository（扩展功能）

详见 [扩展开发](#-扩展开发) 或 [EXTENSION_GUIDE.md](EXTENSION_GUIDE.md)。

### Q5: 支持哪些数据库？

**A**: 目前只支持 **PostgreSQL**（使用 AsyncPG 驱动）。

### Q6: 处理外部数据时应该注意什么？

**A**: 外部数据（API、消息队列等）可能包含链名缩写，必须通过 Repository 处理：

\`\`\`python
# 外部数据
data = {"chain": "sol", "token_address": "xxx", ...}

# ✅ 正确：使用 repository.create()
repo = PreSignalRepository()
async with get_db() as session:
    result = await repo.create(session, **data)
    await session.commit()
\`\`\`

详见 [详细使用](#-详细使用) 中的"处理第三方数据的正确方式"。

---

## 📚 文档

- **扩展指南**: [EXTENSION_GUIDE.md](EXTENSION_GUIDE.md) - 如何扩展模块
- **架构文档**: [ARCHITECTURE.md](ARCHITECTURE.md) - 系统架构说明
- **导入指南**: [IMPORT_GUIDE.md](IMPORT_GUIDE.md) - Token 数据导入

---

## 🛠️ 开发工具

### 测试

\`\`\`bash
# 运行所有测试
python scripts/run_all_tests.py

# 运行特定测试
python scripts/test_token.py
python scripts/test_signal.py
python scripts/test_pre_signal.py
\`\`\`

### 数据导入

\`\`\`bash
# 导入 token 数据
python scripts/import_token_recognition_data.py
\`\`\`

### 验证

\`\`\`bash
# 验证数据一致性
python scripts/verify_consistency.py

# 测试数据库连接
python scripts/test_connection.py
\`\`\`

---

## 📝 更新日志

### v0.1.8 (最新)
- ✨ 完全暴露 Models、Repositories、Session 等组件
- ✨ 新增扩展指南（EXTENSION_GUIDE.md）
- 🐛 修复外键约束问题（链名规范化）
- 📚 新增详细 README 文档

### v0.1.6
- ✨ 新增链名自动规范化功能
- ✨ TokenRepository 新增多种搜索方法
- ♻️ 移除 TokenRecognition 模块

---

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证。

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

<div align="center">

**如果这个项目对你有帮助，请给我们一个 ⭐️！**

Made with ❤️ by the Prisma Web3 Team

</div>
