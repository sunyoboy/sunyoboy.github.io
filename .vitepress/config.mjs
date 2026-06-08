import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Knowing & Doing',
  description: '知行合一',
  lang: 'zh-CN',
  appearance: true,
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '复盘', link: '/review/2026/2026' },
      { text: '问题清单', link: '/questions/index' },
      { text: '知识库', link: '/docs/' },
      { text: '关于', link: '/about' }
    ],
    sidebar: {
      '/review/': [
        {
          text: '2026年',
          collapsed: false,
          items: [
            { text: '年度复盘', link: '/review/2026/2026' },
            {
              text: '5月',
              collapsed: false,
              items: [
                { text: '月复盘', link: '/review/2026/05/2026-05' },
                { text: 'W21 周复盘', link: '/review/2026/05/2026-W21' },
                { text: '05-21', link: '/review/2026/05/2026-05-21' },
                { text: '05-22', link: '/review/2026/05/2026-05-22' },
                { text: '05-25', link: '/review/2026/05/2026-05-25' },
                { text: '05-26', link: '/review/2026/05/2026-05-26' },
                { text: '05-27', link: '/review/2026/05/2026-05-27' },
                { text: '05-28', link: '/review/2026/05/2026-05-28' }
              ]
            },
            {
              text: '6月',
              collapsed: false,
              items: [
                { text: '06-01（周一）', link: '/review/2026/06/2026-06-01' },
                { text: '06-02（周二）', link: '/review/2026/06/2026-06-02' },
                { text: '06-03（周三）', link: '/review/2026/06/2026-06-03' },
                { text: '06-04（周四）', link: '/review/2026/06/2026-06-04' },
                { text: '06-05（周五）', link: '/review/2026/06/2026-06-05' }
              ]
            }
          ]
        }
      ],
      '/questions/': [
        {
          text: '2026年',
          collapsed: false,
          items: [
            { text: '问题汇总', link: '/questions/index' },
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
      ],
      '/docs/': [
        {
          text: '知识库',
          collapsed: false,
          items: [
            { text: '知识库首页', link: '/docs/' },
            { text: '股票工具与渠道', link: '/docs/stock-tools' },
            { text: '决策记录', link: '/docs/decision-log' },
            { text: '部署说明', link: '/docs/deploy' },
            { text: 'A股行情 05-26', link: '/docs/a-share-2026-05-26' },
            { text: '十五五投资方向', link: '/docs/fifteen-five-investment' },
            { text: 'A股做T操作指南', link: '/docs/t-trading' },
            { text: 'AI工具全景分析', link: '/docs/ai-tools-analysis' }
          ]
        }
      ]
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/sunyoboy' }
    ]
  }
})
