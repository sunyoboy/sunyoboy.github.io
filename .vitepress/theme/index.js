import DefaultTheme from 'vitepress/theme'
import './custom.css'

export default {
  ...DefaultTheme,
  enhanceApp({ router }) {
    if (typeof window !== 'undefined') {
      // 点击左上角「知识全景图」跳转到全景图页面
      const observer = new MutationObserver(() => {
        const titleLink = document.querySelector('.VPNavBarTitle a')
        if (titleLink && titleLink.getAttribute('href') === '/') {
          titleLink.setAttribute('href', '/docs/knowledge-tree.html')
        }
      })
      observer.observe(document.body, { childList: true, subtree: true })
    }
  }
}
