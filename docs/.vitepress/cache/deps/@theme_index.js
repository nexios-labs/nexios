import "./chunk-627NGWSC.js";
import {
  computed,
  ref,
  shallowReadonly,
  shallowRef
} from "./chunk-JN5NFW2R.js";

// node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/index.js
import "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/styles/fonts.css";

// node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/without-fonts.js
import "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/styles/vars.css";
import "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/styles/base.css";
import "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/styles/icons.css";
import "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/styles/utils.css";
import "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/styles/components/custom-block.css";
import "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/styles/components/vp-code.css";
import "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/styles/components/vp-code-group.css";
import "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/styles/components/vp-doc.css";
import "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/styles/components/vp-sponsor.css";
import VPBadge from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPBadge.vue";
import Layout from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/Layout.vue";
import { default as default2 } from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPBadge.vue";
import { default as default3 } from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPButton.vue";
import { default as default4 } from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPDocAsideSponsors.vue";
import { default as default5 } from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPFeatures.vue";
import { default as default6 } from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPHomeContent.vue";
import { default as default7 } from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPHomeFeatures.vue";
import { default as default8 } from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPHomeHero.vue";
import { default as default9 } from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPHomeSponsors.vue";
import { default as default10 } from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPImage.vue";
import { default as default11 } from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPLink.vue";
import { default as default12 } from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPNavBarSearch.vue";
import { default as default13 } from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPSocialLink.vue";
import { default as default14 } from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPSocialLinks.vue";
import { default as default15 } from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPSponsors.vue";
import { default as default16 } from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPTeamMembers.vue";
import { default as default17 } from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPTeamPage.vue";
import { default as default18 } from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPTeamPageSection.vue";
import { default as default19 } from "C:/Users/dunamix/Documents/Nexios/node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/components/VPTeamPageTitle.vue";

// node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/composables/layout.js
import { inBrowser, onContentUpdated, useRoute } from "vitepress";

// node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/shared.js
var UnpackStackView = Symbol("stack-view:unpack");
function stackView(..._layers) {
  const layers = _layers.filter((layer) => isObject(layer));
  if (layers.length <= 1)
    return _layers[0];
  const allKeys = new Set(layers.flatMap((layer) => Reflect.ownKeys(layer)));
  const allKeysArray = [...allKeys];
  return new Proxy({}, {
    // TODO: optimize for performance, this is a hot path
    get(_, prop) {
      if (prop === UnpackStackView)
        return layers;
      return stackView(...layers.map((layer) => layer[prop]).filter((v) => v !== void 0));
    },
    set() {
      throw new Error("StackView is read-only and cannot be mutated.");
    },
    has(_, prop) {
      return allKeys.has(prop);
    },
    ownKeys() {
      return allKeysArray;
    },
    getOwnPropertyDescriptor(_, prop) {
      for (const layer of layers) {
        const descriptor = Object.getOwnPropertyDescriptor(layer, prop);
        if (descriptor)
          return descriptor;
      }
    }
  });
}
stackView.unpack = function(obj) {
  return obj == null ? void 0 : obj[UnpackStackView];
};
function isObject(value) {
  return Object.prototype.toString.call(value) === "[object Object]";
}

// node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/support/utils.js
import { withBase } from "vitepress";

// node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/composables/data.js
import { useData as useData$ } from "vitepress";
var useData = useData$;

// node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/support/sidebar.js
function getSidebarGroups(sidebar2) {
  const groups = [];
  let lastGroupIndex = 0;
  for (const index in sidebar2) {
    const item = sidebar2[index];
    if (item.items) {
      lastGroupIndex = groups.push(item);
      continue;
    }
    if (!groups[lastGroupIndex]) {
      groups.push({ items: [] });
    }
    groups[lastGroupIndex].items.push(item);
  }
  return groups;
}

// node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/composables/outline.js
import { getScrollOffset } from "vitepress";

// node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/composables/sidebar.js
var isOpen = ref(false);

// node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/composables/layout.js
var headers = shallowRef([]);
var sidebar = shallowRef([]);
var is960 = shallowRef(false);
function useLayout() {
  const { frontmatter, theme: theme2 } = useData();
  const isHome = computed(() => {
    return !!(frontmatter.value.isHome ?? frontmatter.value.layout === "home");
  });
  const hasSidebar = computed(() => {
    return frontmatter.value.sidebar !== false && sidebar.value.length > 0 && !isHome.value;
  });
  const isSidebarEnabled = computed(() => hasSidebar.value && is960.value);
  const sidebarGroups = computed(() => {
    return hasSidebar.value ? getSidebarGroups(sidebar.value) : [];
  });
  const hasAside = computed(() => {
    if (isHome.value)
      return false;
    if (frontmatter.value.aside != null)
      return !!frontmatter.value.aside;
    return theme2.value.aside !== false;
  });
  const leftAside = computed(() => {
    if (!hasAside.value)
      return false;
    return frontmatter.value.aside == null ? theme2.value.aside === "left" : frontmatter.value.aside === "left";
  });
  const hasLocalNav = computed(() => {
    return headers.value.length > 0;
  });
  return {
    isHome,
    sidebar: shallowReadonly(sidebar),
    sidebarGroups,
    hasSidebar,
    isSidebarEnabled,
    hasAside,
    leftAside,
    headers: shallowReadonly(headers),
    hasLocalNav
  };
}

// node_modules/.pnpm/vitepress@2.0.0-alpha.5_@al_55cacafd01b0f53dc501fef9f1793683/node_modules/vitepress/dist/client/theme-default/without-fonts.js
var theme = {
  Layout,
  enhanceApp: ({ app }) => {
    app.component("Badge", VPBadge);
  }
};
var without_fonts_default = theme;
export {
  default2 as VPBadge,
  default3 as VPButton,
  default4 as VPDocAsideSponsors,
  default5 as VPFeatures,
  default6 as VPHomeContent,
  default7 as VPHomeFeatures,
  default8 as VPHomeHero,
  default9 as VPHomeSponsors,
  default10 as VPImage,
  default11 as VPLink,
  default12 as VPNavBarSearch,
  default13 as VPSocialLink,
  default14 as VPSocialLinks,
  default15 as VPSponsors,
  default16 as VPTeamMembers,
  default17 as VPTeamPage,
  default18 as VPTeamPageSection,
  default19 as VPTeamPageTitle,
  without_fonts_default as default,
  useLayout
};
//# sourceMappingURL=@theme_index.js.map
