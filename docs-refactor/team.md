---
layout: page
---
<script setup>
import {
  VPTeamPage,
  VPTeamPageTitle,
  VPTeamMembers
} from 'vitepress/theme'

const members = [
  {
    avatar: 'https://avatars.githubusercontent.com/u/144450118?v=4',
    name: "Dunamix",
    title: 'Creator | Lead Developer', 
    links: [
      { icon: 'github', link: 'https://github.com/TechWithDunamix' },
      { icon: 'twitter', link: 'https://twitter.com/mrdunamix' }
    ]
  },

  {
    avatar: 'https://avatars.githubusercontent.com/u/55154055?v=4',
    name: "Mohammed Al-Ameen",
    title: 'Developer', 
    links: [
      { icon: 'github', link: 'https://github.com/struckchure' },
      { icon: 'twitter', link: 'https://x.com/struckchure' }
    ]
  }
]
</script>

<VPTeamPage>
  <VPTeamPageTitle>
    <template #title>
      Our Team
    </template>
    <template #lead>
      The development of Nexios is driven by a passionate and growing community of developers. Below are some early contributors who’ve chosen to be featured as part of this journey.
    </template>
  </VPTeamPageTitle>
  <VPTeamMembers :members />
</VPTeamPage>