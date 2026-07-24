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
              text: '7月',
              collapsed: false,
              items: [
                {
                  text: '📂 周复盘',
                  collapsed: false,
                  items: [
                    { text: '📋 W29 周计划 (7/13-7/17)', link: '/review/2026/07/2026-W29' },
                    { text: '📋 W28 周复盘 (7/6-7/11)', link: '/review/2026/07/2026-W28' },
                  ]
                },
                {
                  text: '📂 日复盘',
                  collapsed: false,
                  items: [
                    { text: '07-24 · 全面回调·有色回落·极简实践', link: '/review/2026/07/2026-07-24' },
                    { text: '07-23 · 科创加速下跌·有色连热三天', link: '/review/2026/07/2026-07-23' },
                    { text: '07-22 · 下午跳水·科技领跌·国债卖飞', link: '/review/2026/07/2026-07-22' },
                    { text: '07-21 · 暴力反弹·结构反转·银行补跌', link: '/review/2026/07/2026-07-21' },
                    { text: '07-20 · 一日游反弹·银行英雄', link: '/review/2026/07/2026-07-20' },
                    { text: '07-17 · 四连跌·美伊冲突·澜起反垄断', link: '/review/2026/07/2026-07-17' },
                    { text: '07-16 · 长鑫申购·全面下跌·科创-4%', link: '/review/2026/07/2026-07-16' },
                    { text: '07-15 · 三重事件+中报截止·极致分化', link: '/review/2026/07/2026-07-15' },
                    { text: '07-14 · V型反转·创业板+3.43%', link: '/review/2026/07/2026-07-14' },
                    { text: '07-13 · 崩盘式普跌·上证-2.06%', link: '/review/2026/07/2026-07-13' },
                    { text: '07-10 · 科技杀跌·科创-5.53%', link: '/review/2026/07/2026-07-10' },
                    { text: '07-09 · 全面暴力反弹+止损触发', link: '/review/2026/07/2026-07-09' },
                    { text: '07-08 · 美伊战事+金叉变死叉', link: '/review/2026/07/2026-07-08' },
                    { text: '07-07 · 失守4000+4涨27跌', link: '/review/2026/07/2026-07-07' },
                    { text: '07-06 · 周一盘前+央行放水', link: '/review/2026/07/2026-07-06' },
                    { text: '07-03 · 期货分裂+不加仓', link: '/review/2026/07/2026-07-03' },
                    { text: '07-02 · 全线暴跌+三只清仓', link: '/review/2026/07/2026-07-02' },
                    { text: '07-01 · 新刀第一天+卫星减仓', link: '/review/2026/07/2026-07-01' }
                  ]
                }
              ]
            },
            {
              text: '6月',
              collapsed: true,
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
                    { text: '06-30 · 换刀完成+百花齐放', link: '/review/2026/06/2026-06-30' },
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
                {
                  text: '📂 周复盘',
                  collapsed: false,
                  items: [
                    { text: '📋 W21 周复盘 (5.20-5.24)', link: '/review/2026/05/2026-W21' },
                  ]
                },
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
            { text: '📋 下半年读书计划', link: '/growth/读书计划-2026下半年' },
            { text: '💰 财务仪表盘', link: '/growth/财务仪表盘' },
            { text: '🛠️ 技能树', link: '/growth/技能树' },
            { text: '📈 第二增长曲线', link: '/growth/第二增长曲线' },
            { text: '💼 软件工程师价值转移', link: '/growth/软件工程师价值转移与行动方向' },
            { text: '💡 投资教训与根因分析', link: '/growth/投资教训与根因分析' },
            {
              text: '2026年',
              collapsed: false,
              items: [
                {
                  text: '6月',
                  collapsed: true,
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
                    { text: '🛒 饮食与零食清单', link: '/questions/孕期饮食与零食清单' },
                    { text: '💝 异地陪伴指南', link: '/questions/孕期异地陪伴指南' },
                    { text: '07-06 常规血检', link: '/questions/2026/07/2026-07-06' },
                    { text: '07-01 检验汇总', link: '/questions/2026/07/2026-07-01' },
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
                  text: '6月',
                  collapsed: false,
                  items: [
                    { text: '06-24 问题汇总', link: '/questions/2026/06/2026-06-24' },
                    { text: '06-24 盯盘+拖延+NLP', link: '/questions/2026/06/2026-06-24-盯盘与NLP' }
                  ]
                },
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
                { text: '🔪 做减法·交易极简', link: '/docs/minimalism-trading' },
                { text: '🎙️ 梁文锋·全文分析', link: '/docs/liang-wenfeng-transcript-analysis' },
                { text: '🔻 Capitulation信号·底部识别', link: '/docs/market-bottom-signals' },
                { text: '📦 开源量化项目调研', link: '/docs/opensource-quant-projects' },
                { text: '🤖 华泰AI涨乐Skills安装指南', link: '/docs/htsc-skills-setup' },
                { text: '🔧 AI金融工具·分工指南', link: '/docs/ai-tools-selection-guide' },
                { text: '🏪 问财SkillHub技能库', link: '/docs/iwencai-skills' },
                { text: '🚀 AI工具飞轮加速', link: '/docs/ai-tools-flywheel' },
                { text: '💰 AI工具·副业变现', link: '/docs/ai-tools-sidehustle' },
                { text: '🔧 AI金融投资工具调研', link: '/docs/ai-finance-tools' },
                { text: '📊 申万行业分类', link: '/docs/shenwan-industry-classification' },
                { text: '📐 投资纪律指标化', link: '/docs/investment-discipline-indicators' },
                { text: '📐 决策方法论与策略体系', link: '/docs/decision-methodology' },
                { text: '🌍 资产定价权全景图', link: '/docs/asset-pricing-power' },
                { text: '🗺️ 投资理论全景图', link: '/docs/investment-theories-map' },
                { text: '📖 格伦姆·聪明的投资者', link: '/docs/graham-intelligent-investor' },
                { text: '🌐 博格·指数基金之父', link: '/docs/bogle-index-investing' },
                { text: '🌦️ 达利欧·全天候组合', link: '/docs/dalio-all-weather' },
                { text: '🔄 马克斯·周期与第二层思维', link: '/docs/marks-market-cycles' },
                { text: '📖 范·撒普 核心提炼', link: '/docs/van-tharp-trade-your-way' },
                { text: '交易纪律', link: '/docs/position-discipline' },
                { text: '📋 交易执行SOP', link: '/docs/trading-sop-pdca' },
                { text: '📐 交易决策矩阵·速查卡', link: '/docs/trading-decision-matrix' },
                { text: '🔄 每日复盘SOP', link: '/docs/daily-review-sop' },
                { text: '🤖 每日复盘Skill', link: '/docs/knowingdoing-review-skill' },
                { text: '📱 手机端速查清单', link: '/docs/mobile-checklist' },
                { text: '📖 外部交易规则参考', link: '/docs/trading-rules-external' },
                { text: 'MA5 偏离度 · 持仓纪律', link: '/docs/ma5-deviation-discipline' },
                { text: '股票评估框架', link: '/docs/stock-evaluation' },
                { text: '🚫 为什么盯盘不可取', link: '/docs/why-not-watch-market' },
                { text: '💼 上班族交易规划', link: '/docs/office-worker-trading' },
                { text: 'A股做T操作指南', link: '/docs/t-trading' },
                { text: '宽基ETF做T策略', link: '/docs/index-etf-trading' },
                { text: '📋 三账户ETF观察清单 07-06', link: '/docs/etf-watchlist-2026-07-06' },
                { text: '🔭 自选股观察清单 07-22', link: '/docs/etf-watchlist-2026-07-22' },
                { text: '🎯 HALO观察池·对标美股', link: '/docs/watchlist-halo' },
                { text: '📜 债券ETF投资入门', link: '/docs/bond-investment-basics' },
                { text: '🏛️ 中国首席经济学家论坛', link: '/docs/chief-economist-forum' },
                { text: '🏦 基金公司与基金经理观察清单', link: '/docs/fund-managers-watchlist' },
                { text: '🎯 曹名长·深度价值投资框架', link: '/docs/cao-mingchang-value-investing' },
                { text: '🛡️ 防御型ETF买入优先级', link: '/docs/defensive-etf-buy-guide' },
                { text: '🔄 反者道之动·跨文化谱系', link: '/docs/reversal-is-the-movement-of-dao' },
                { text: '盈利分红型行业', link: '/docs/profitable-industries' },
                { text: '十五五投资方向', link: '/docs/fifteen-five-investment' },
                { text: '🇺🇸对标美股·十五五ETF', link: '/docs/fifteen-five-us-benchmark' },
                { text: '海鸥期权策略', link: '/docs/seagull-strategy' },
                { text: '巴菲特1998演讲', link: '/docs/buffett-1998' },
                { text: '想赢怕输的心态', link: '/docs/fear-greed' },
                { text: '投资心智', link: '/docs/mindset' },
                { text: '🧠 自我认知框架', link: '/docs/self-awareness' },
                { text: '🧠 NLP 逻辑层次 · 迪尔茨', link: '/docs/nlp-dilts-logical-levels' },
                { text: '🧠 卡尼曼 思考快与慢', link: '/docs/kahneman-thinking-fast-slow' },
                { text: '📖 《掌控习惯》精炼', link: '/docs/atomic-habits' },
                { text: '🫱 团队质疑七层过滤', link: '/docs/team-critical-thinking' },
                { text: '📚 完善操作系统的推荐书单', link: '/docs/reading-list-recommendations' },
                { text: '✍️ 人生散文阅读指南 · 为人之道', link: '/docs/essay-reading-guide' },
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
                { text: '🔡 维特根斯坦·语言澄清', link: '/docs/wittgenstein-language-clarity' },
                { text: '矛盾论', link: '/docs/contradiction' },
                { text: '实践论', link: '/docs/practice-theory' },
                { text: '三大法宝', link: '/docs/three-weapons' },
                { text: '🏛️ 斯多葛主义', link: '/docs/stoicism' },
                { text: '🪣 第欧根尼·犬儒学派', link: '/docs/diogenes-cynicism' },
                { text: '🧹 断舍离·极简生活', link: '/docs/minimalism-declutter' },
                { text: '☯️ 周易四大核心语录', link: '/docs/yijing-four-quotes' },
                { text: '🦁 荀子·天人相分化性起伪', link: '/docs/xunzi-philosophy' },
                { text: '⚖️ 韩非·李斯·法家双峰', link: '/docs/hanfei-lisi-legalism' },
                { text: '🏛️ 先秦诸子百家·思想全景', link: '/docs/hundred-schools-of-thought' },
                { text: '☯️ 易传名句全集', link: '/docs/yijing-famous-quotes' },
                { text: '📜 古文诸子百家引用分析', link: '/docs/古文诸子百家引用分析' },
                { text: '📖 史铁生·轮椅上的人生哲学', link: '/docs/shi-tiesheng-philosophy' },
                { text: '📜 《资治通鉴》·人生主线', link: '/docs/zizhi-tongjian-life-mainline' },
                { text: '📚 古文经典排名', link: '/docs/classics-ranking' },
                { text: '🗺️ 人生维度框架', link: '/docs/life-framework' },
                { text: '📜 做人做事原则', link: '/docs/life-principles' },
                { text: '📺 《天道》《大染坊》之道', link: '/docs/tv-wisdom-tiandao-daranfang' },
                { text: '📺 《大明王朝》《士兵突击》', link: '/docs/tv-daming-soldiers-sortie' },
                { text: '📺 《我的团长我的团》', link: '/docs/tv-my-chief-my-regiment' },
                { text: '🧗 《徒手攀岩》', link: '/docs/free-solo' },
                { text: '🎬 《人生七年》', link: '/docs/7-up-series' },
                { text: '🎨 审美·纯粹地活着', link: '/docs/aesthetics' },
                { text: '🔫 枪炮病菌与钢铁', link: '/docs/guns-germs-steel' },
                { text: '🎯 加文·贝克投资大师课', link: '/docs/gavin-baker-investment' },
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
