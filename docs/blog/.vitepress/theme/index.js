import DefaultTheme from "vitepress/theme";
import { withBase } from "vitepress";
import { nextTick, onMounted, onUnmounted } from "vue";
import "./style.css";

export default {
  extends: DefaultTheme,
  enhanceApp({ app, router }) {
    app.config.globalProperties.$withBase = withBase;
    router.onAfterRouteChanged = async () => {
      if (typeof document === "undefined") return;
      await nextTick();
      document.dispatchEvent(new Event("van:shopping-graph-ready"));
    };
  },
  setup() {
    let appearance, content;
    onMounted(() => {
      const update = () => {
        document.body.dataset.theme = document.documentElement.classList.contains("dark") ? "dark" : "light";
      };
      update();
      appearance = new MutationObserver(update);
      appearance.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
      const initializeGraphs = () => document.dispatchEvent(new Event("van:shopping-graph-ready"));
      content = new MutationObserver(initializeGraphs);
      content.observe(document.body, { childList: true, subtree: true });
      initializeGraphs();
    });
    onUnmounted(() => {
      appearance?.disconnect();
      content?.disconnect();
    });
  },
};
