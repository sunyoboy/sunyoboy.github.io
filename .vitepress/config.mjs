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
      { text: '知识库', link: '/docs/stock-tools' },
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
                { text: '05-21', link: '/review/2026/05/2026-05-21' }
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
                { text: '05-26', link: '/questions/2026/05/2026-05-26' },
                { text: '05-22', link: '/questions/2026/05/2026-05-22' },
                { text: '05-21', link: '/questions/2026/05/2026-05-21' }
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
            { text: '股票工具与渠道', link: '/docs/stock-tools' },
            { text: '决策记录', link: '/docs/decision-log' },
            { text: '部署说明', link: '/docs/deploy' },
            { text: 'A股行情 05-26', link: '/docs/a-share-2026-05-26' }
          ]
        }
      ]
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com' }
    ]
  }
})
