---
layout: page
---
<script setup>
import {
  VPTeamPage,
  VPTeamPageTitle,
  VPTeamMembers,
  VPTeamPageSection
} from 'vitepress/theme'

const coreTeam = [
  {
    avatar: 'https://avatars.githubusercontent.com/u/144450118?v=4',
    name: "Dunamix",
    title: 'Creator | Lead Developer',
    desc: 'Core architect and maintainer of Nexios. Focused on async performance and clean architecture.',
    links: [
      { icon: 'github', link: 'https://github.com/TechWithDunamix' },
      { icon: 'twitter', link: 'https://twitter.com/mrdunamix' }
    ],
    sponsor: 'https://github.com/sponsors/TechWithDunamix'
  }
]

const maintainers = [
  {
    avatar: 'https://avatars.githubusercontent.com/u/55154055?v=4',
    name: "Mohammed Al-Ameen",
    title: 'Core Developer',
    desc: 'Leads database integration and authentication systems development.',
    links: [
      { icon: 'github', link: 'https://github.com/struckchure' },
      { icon: 'twitter', link: 'https://x.com/struckchure' }
    ]
  }
]

const emeriti = [
  // Past team members who made significant contributions
]
</script>

<VPTeamPage>
  <VPTeamPageTitle>
    <template #title>
      Our Team
    </template>
    <template #lead>
      The development of Nexios is guided by an experienced team of developers who are passionate about building fast, clean, and developer-friendly web frameworks. The project thrives thanks to contributions from our amazing community.
    </template>
  </VPTeamPageTitle>

  <VPTeamPageSection>
    <template #title>Core Team</template>
    <template #lead>The core development team behind Nexios.</template>
    <template #members>
      <VPTeamMembers size="medium" :members="coreTeam" />
    </template>
  </VPTeamPageSection>

  <VPTeamPageSection>
    <template #title>Maintainers</template>
    <template #lead>Active maintainers helping to ensure Nexios's continued development and success.</template>
    <template #members>
      <VPTeamMembers size="medium" :members="maintainers" />
    </template>
  </VPTeamPageSection>

  
</VPTeamPage>

<style scoped>
.content {
  padding: 0 24px;
}

.partner-benefits {
  margin: 24px 0;
  padding: 24px;
  border-radius: 8px;
  background-color: var(--vp-c-bg-soft);
}

.partner-benefits h4 {
  margin-top: 0;
}

.partner-benefits ul {
  padding-left: 20px;
}
</style>

::: tip Join Us!
We're always looking for contributors who are passionate about Python and web development. Check out our [Contributing Guide](/contributing/) to get started.
:::

::: info Get Support
Need help with Nexios? Join our [Discord community](https://discord.gg/nexios) or open an issue on [GitHub](https://github.com/nexios-labs/nexios/issues).
:::