import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Knowing & Doing',
  description: '知行合一',
  lang: 'zh-CN',
  appearance: true,
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '问题清单', link: '/questions/index' },
      { text: '复盘', link: '/review/2026/2026' },
      { text: '个人成长', link: '/growth/2026-年度OKR' },
      { text: '知识库', link: '/docs/' },
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
              text: '6月 · 4000点拉锯',
              collapsed: false,
              items: [
                { text: '📅 月复盘 · 经济日历', link: '/review/2026/06/2026-06' },
                { text: '06-17 周三 · FOMC落地点评', link: '/review/2026/06/2026-06-17' },
                { text: '📋 本周持仓建议', link: '/review/2026/06/2026-06-11-本周持仓建议' },
                { text: '📊 06-12 持仓分析', link: '/review/2026/06/2026-06-12-持仓分析' },
                { text: '📈 净值与仓位跟踪', link: '/review/2026/06/2026-06-12-净值跟踪' },
                { text: '06-11 周四 · FOMC前夕', link: '/review/2026/06/2026-06-11' },
                { text: '06-08 周一 · 黑色星期一', link: '/review/2026/06/2026-06-08' },
                { text: '06-05 周五 · 非农冲击', link: '/review/2026/06/2026-06-05' },
                { text: '06-04 周四', link: '/review/2026/06/2026-06-04' },
                { text: '06-03 周三', link: '/review/2026/06/2026-06-03' },
                { text: '06-02 周二', link: '/review/2026/06/2026-06-02' },
                { text: '06-01 周一', link: '/review/2026/06/2026-06-01' }
              ]
            },
            {
              text: '5月',
              collapsed: true,
              items: [
                { text: '05-28 周四', link: '/review/2026/05/2026-05-28' },
                { text: '05-27 周三 · 伊朗空袭', link: '/review/2026/05/2026-05-27' },
                { text: '05-26 周二', link: '/review/2026/05/2026-05-26' },
                { text: '05-25 周一', link: '/review/2026/05/2026-05-25' },
                { text: '05-22 周五', link: '/review/2026/05/2026-05-22' },
                { text: '05-21 周四', link: '/review/2026/05/2026-05-21' }
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
            { text: '📖 阅读清单', link: '/growth/阅读清单' },
            { text: '💰 财务仪表盘', link: '/growth/财务仪表盘' },
            { text: '🛠️ 技能树', link: '/growth/技能树' },
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
                    { text: '06-16 复查结果', link: '/questions/2026/06/2026-06-16' },
                    { text: '06-12 复查结果', link: '/questions/2026/06/2026-06-12' },
                    { text: '06-11 情况汇总', link: '/questions/2026/06/2026-06-11' }
                  ]
                }
              ]
            },
            {
              text: '2026年',
              collapsed: false,
              items: [
                {
                  text: '5月',
                  collapsed: false,
                  items: [
                    { text: '05-21', link: '/questions/2026/05/2026-05-21' },
                    { text: '05-22', link: '/questions/2026/05/2026-05-22' },
                    { text: '05-26', link: '/questions/2026/05/2026-05-26' }
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
            {
              text: '🧠 提升认知',
              collapsed: false,
              items: [
                { text: '矛盾论', link: '/docs/contradiction' },
                { text: '实践论', link: '/docs/practice-theory' },
                { text: '三大法宝', link: '/docs/three-weapons' }
              ]
            },
            {
              text: '💹 投资交易',
              collapsed: false,
              items: [
                { text: 'A股做T操作指南', link: '/docs/t-trading' },
                { text: '宽基ETF做T策略', link: '/docs/index-etf-trading' },
                { text: 'A股行情分析', link: '/docs/a-share-2026-05-26' },
                { text: '盈利分红型行业', link: '/docs/profitable-industries' },
                { text: '十五五投资方向', link: '/docs/fifteen-five-investment' },
                { text: '海鸥期权策略', link: '/docs/seagull-strategy' },
                { text: '建仓纪律', link: '/docs/position-discipline' },
                { text: 'FOMC会议时间表', link: '/docs/fomc-schedule' },
                { text: '股票工具与渠道', link: '/docs/stock-tools' }
              ]
            },
            {
              text: '🧠 思维认知',
              collapsed: true,
              items: [
                { text: '个人操作系统', link: '/docs/personal-os' },
                { text: '保持好心态', link: '/docs/peace-of-mind' },
                { text: '巴菲特1998演讲', link: '/docs/buffett-1998' },
                { text: '想赢怕输的心态', link: '/docs/fear-greed' },
                { text: '预期与现实的差距', link: '/docs/expectation-gap' },
                { text: '投资心智', link: '/docs/mindset' },
                { text: 'AI工具全景分析', link: '/docs/ai-tools-analysis' },
                { text: '个人开发者深耕方向', link: '/docs/solo-dev-strategy' }
              ]
            },
            {
              text: '🔧 其他',
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
