import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Knowing & Doing',
  description: '知行合一',
  lang: 'zh-CN',
  appearance: true,
  themeConfig: {
    siteTitle: '网站全景图',
    nav: [
      { text: '首页', link: '/' },
      { text: '复盘', link: '/review/2026/2026' },
      { text: '知识库', link: '/docs/' },
      { text: '个人成长', link: '/growth/2026-年度OKR' },
      { text: '问题清单', link: '/questions/index' },
      { text: 'Index', link: '/catalog' }
    ],
    sidebar: {
      '/review/': [
        {
          text: '2026年',
          collapsed: false,
          items: [
            { text: '年度复盘', link: '/review/2026/2026' },
            {
              text: '6月',
              collapsed: false,
              items: [
                {
                  text: '📂 专题报告',
                  collapsed: false,
                  items: [
                    { text: '📅 月复盘 · 经济日历', link: '/review/2026/06/2026-06' },
                    { text: '📋 本周持仓建议', link: '/review/2026/06/2026-06-11-本周持仓建议' },
                    { text: '📊 持仓分析', link: '/review/2026/06/2026-06-12-持仓分析' },
                    { text: '📈 净值与仓位跟踪', link: '/review/2026/06/2026-06-12-净值跟踪' }
                  ]
                },
                {
                  text: '📂 日复盘',
                  collapsed: true,
                  items: [
                    { text: '06-29 · 全面拉升+K型分化', link: '/review/2026/06/2026-06-29' },
                    { text: '06-26 · 月末杀跌+宽基入场', link: '/review/2026/06/2026-06-26' },
                    { text: '06-25 · 美光反转+PCE落地', link: '/review/2026/06/2026-06-25' },
                    { text: '06-24 · 缩量企稳+科创领涨', link: '/review/2026/06/2026-06-24' },
                    { text: '06-23 · 加速下跌+持仓诊断', link: '/review/2026/06/2026-06-23' },
                    { text: '06-22 · 高低切换', link: '/review/2026/06/2026-06-22' },
                    { text: '06-18 · 端午前收官', link: '/review/2026/06/2026-06-18' },
                    { text: '06-17 · FOMC落地', link: '/review/2026/06/2026-06-17' },
                    { text: '06-11 · FOMC前夕', link: '/review/2026/06/2026-06-11' },
                    { text: '06-08 · 黑色星期一', link: '/review/2026/06/2026-06-08' },
                    { text: '06-05 · 非农冲击', link: '/review/2026/06/2026-06-05' },
                    { text: '06-04', link: '/review/2026/06/2026-06-04' },
                    { text: '06-03', link: '/review/2026/06/2026-06-03' },
                    { text: '06-02', link: '/review/2026/06/2026-06-02' },
                    { text: '06-01', link: '/review/2026/06/2026-06-01' }
                  ]
                }
              ]
            },
            {
              text: '5月',
              collapsed: true,
              items: [
                { text: '📋 W21 周复盘 (5.20-5.24)', link: '/review/2026/05/2026-W21' },
                { text: '📊 月度市场概况 (05-26)', link: '/review/2026/05/2026-05-26-月度市场概况' },
                { text: '05-28', link: '/review/2026/05/2026-05-28' },
                { text: '05-27 · 伊朗空袭', link: '/review/2026/05/2026-05-27' },
                { text: '05-26', link: '/review/2026/05/2026-05-26' },
                { text: '05-25', link: '/review/2026/05/2026-05-25' },
                { text: '05-22', link: '/review/2026/05/2026-05-22' },
                { text: '05-21', link: '/review/2026/05/2026-05-21' }
              ]
            }
          ]
        }
      ],
      '/growth/': [
        {
          text: '个人成长',
          collapsed: false,
          items: [
            { text: '🔥 信条', link: '/growth/信条' },
            { text: '🔄 方法论', link: '/growth/方法论' },
            { text: '🎯 年度 OKR', link: '/growth/2026-年度OKR' },
            { text: '📋 个人周报模板', link: '/growth/个人周报模板' },
            { text: '📖 阅读清单(14本)', link: '/growth/阅读清单' },
            { text: '💰 财务仪表盘', link: '/growth/财务仪表盘' },
            { text: '🛠️ 技能树', link: '/growth/技能树' },
            { text: '📈 第二增长曲线', link: '/growth/第二增长曲线' },
            {
              text: '2026年',
              collapsed: false,
              items: [
                {
                  text: '6月',
                  collapsed: false,
                  items: [
                    { text: '月回顾', link: '/growth/2026/06/2026-06-月回顾' }
                  ]
                }
              ]
            }
          ]
        }
      ],
      '/questions/': [
        {
          text: '问题清单',
          collapsed: false,
          items: [
            { text: '📋 总览', link: '/questions/index' },
            {
              text: '特别专题',
              collapsed: false,
              items: [
                {
                  text: '管理孕期',
                  collapsed: false,
                  items: [
                    { text: '📅 全程日历', link: '/questions/孕期全程日历' },
                    { text: '06-27 复查结果', link: '/questions/2026/06/2026-06-27' },
                    { text: '06-22 复查结果', link: '/questions/2026/06/2026-06-22' },
                    { text: '06-16 复查结果', link: '/questions/2026/06/2026-06-16' },
                    { text: '06-12 复查结果', link: '/questions/2026/06/2026-06-12' },
                    { text: '06-11 情况汇总', link: '/questions/2026/06/2026-06-11' }
                  ]
                }
              ]
            },
            {
              text: '2026年',
              collapsed: true,
              items: [
                {
                  text: '5月',
                  collapsed: false,
                  items: [
                    { text: '05-26', link: '/questions/2026/05/2026-05-26' },
                    { text: '05-22', link: '/questions/2026/05/2026-05-22' },
                    { text: '05-21', link: '/questions/2026/05/2026-05-21' }
                  ]
                }
              ]
            }
          ]
        }
      ],
      '/docs/': [
        {
          text: '知识库',
          collapsed: false,
          items: [
            { text: '知识库首页', link: '/docs/' },
            { text: '🗺️ 网站全景图', link: '/docs/knowledge-tree' },
            {
              text: '💹 投资体系',
              collapsed: false,
              items: [
                { text: '🔴 FOMC决策全景', link: '/docs/fomc-schedule' },
                { text: '📦 开源量化项目调研', link: '/docs/opensource-quant-projects' },
                { text: '📊 申万行业分类', link: '/docs/shenwan-industry-classification' },
                { text: '📐 投资纪律指标化', link: '/docs/investment-discipline-indicators' },
                { text: '📐 决策方法论与策略体系', link: '/docs/decision-methodology' },
                { text: '📖 范·撒普 核心提炼', link: '/docs/van-tharp-trade-your-way' },
                { text: '交易纪律', link: '/docs/position-discipline' },
                { text: 'MA5 偏离度 · 持仓纪律', link: '/docs/ma5-deviation-discipline' },
                { text: '股票评估框架', link: '/docs/stock-evaluation' },
                { text: '🚫 为什么盯盘不可取', link: '/docs/why-not-watch-market' },
                { text: '💼 上班族交易规划', link: '/docs/office-worker-trading' },
                { text: 'A股做T操作指南', link: '/docs/t-trading' },
                { text: '宽基ETF做T策略', link: '/docs/index-etf-trading' },
                { text: '盈利分红型行业', link: '/docs/profitable-industries' },
                { text: '十五五投资方向', link: '/docs/fifteen-five-investment' },
                { text: '海鸥期权策略', link: '/docs/seagull-strategy' },
                { text: '巴菲特1998演讲', link: '/docs/buffett-1998' },
                { text: '想赢怕输的心态', link: '/docs/fear-greed' },
                { text: '投资心智', link: '/docs/mindset' },
                { text: '🧠 自我认知框架', link: '/docs/self-awareness' },
                { text: '🧠 NLP 逻辑层次 · 迪尔茨', link: '/docs/nlp-dilts-logical-levels' },
                { text: '🧠 卡尼曼 思考快与慢', link: '/docs/kahneman-thinking-fast-slow' },
                { text: '🫱 团队质疑七层过滤', link: '/docs/team-critical-thinking' },
                { text: '📚 完善操作系统的推荐书单', link: '/docs/reading-list-recommendations' },
                { text: 'A股行情分析', link: '/docs/a-share-2026-05-26' },
                { text: '🔄 美股-A股 AI全产业链对标', link: '/docs/us-china-ai-hardware-mapping' },
                { text: '股票工具与渠道', link: '/docs/stock-tools' }
              ]
            },
            {
              text: '🧠 认知体系',
              collapsed: true,
              items: [
                { text: '个人操作系统', link: '/docs/personal-os' },
                { text: '🧬 仿生学习系统', link: '/docs/digestion-learning-system' },
                { text: '矛盾论', link: '/docs/contradiction' },
                { text: '实践论', link: '/docs/practice-theory' },
                { text: '三大法宝', link: '/docs/three-weapons' },
                { text: '保持好心态', link: '/docs/peace-of-mind' },
                { text: '预期与现实的差距', link: '/docs/expectation-gap' },
                { text: '🤖 AI编程模型收费对比 2026', link: '/docs/ai-coding-models-2026' },
                { text: '🔀 AI聚合平台性价比', link: '/docs/ai-model-aggregators-2026' },
                { text: '🏦 美国AI投入ROI分析', link: '/docs/us-ai-capex-roi-analysis' },
                { text: '⚔️ 中美AI研发成本对比', link: '/docs/us-ai-monopoly-analysis' },
                { text: '🔒 Claude Fable 5 + 禁令分析', link: '/docs/claude-fable-5-analysis' },
                { text: '🫘 豆包专业版价值评估', link: '/docs/doubao-pro-evaluation' },
                { text: 'AI工具全景分析', link: '/docs/ai-tools-analysis' },
                { text: '🚀 前端输出加速', link: '/docs/frontend-output-acceleration' },
                { text: '个人开发者深耕方向', link: '/docs/solo-dev-strategy' }
              ]
            },
            {
              text: '🔧 站点',
              collapsed: true,
              items: [
                { text: '决策记录', link: '/docs/decision-log' },
                { text: '部署说明', link: '/docs/deploy' }
              ]
            }
          ]
        }
      ]
    },
    search: {
      provider: 'local'
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/sunyoboy' }
    ]
  }
})
