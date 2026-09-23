/**
 * Island Engines — Production Portal Scripts
 * Clean, lightweight, dependency-free vanilla JavaScript.
 * Built with AI assistance for development & transparency.
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. All 20 Bookmarked Community Creator Sites & Workshops
  const COMMUNITY_SITES = [
    {
      name: "The Sudrian Boilersmiths (TSBS)",
      url: "https://thesudrianboilersmiths.org/",
      domain: "thesudrianboilersmiths.org",
      icon: "🔥",
      tag: "Workshop & Models",
      desc: "Premier classic Sodor creator group crafting locomotives, rolling stock, and scenic models for Trainz."
    },
    {
      name: "Toolshed Trainz (MC Bunn)",
      url: "https://toolshedtrainz.wixsite.com/mcbunncafe/sites-1",
      domain: "toolshedtrainz.wixsite.com",
      icon: "🛖",
      tag: "Routes & Hub",
      desc: "Comprehensive directory of Thomas fan routes, rolling stock, models, and community links."
    },
    {
      name: "Mid Sodor Model Works 3D",
      url: "https://midsodormodelworks.wixsite.com/midsodormodelworks3d",
      domain: "midsodormodelworks.wixsite.com",
      icon: "🏔️",
      tag: "Narrow & Standard Gauge",
      desc: "Detailed 3D locomotives, narrow gauge engines, rolling stock, and classic railway items."
    },
    {
      name: "The Old Guard's Van 3D",
      url: "https://theoldguardsvan3d.jimdofree.com/",
      domain: "theoldguardsvan3d.jimdofree.com",
      icon: "🏮",
      tag: "Rolling Stock & Figures",
      desc: "Iconic Thomas & Friends rolling stock, brake vans, figures, and heritage Trainz models."
    },
    {
      name: "Crovan's Gate Works",
      url: "https://crovansgateworks.wixsite.com/crovansgateworks",
      domain: "crovansgateworks.wixsite.com",
      icon: "⚙️",
      tag: "Engines & Workshops",
      desc: "Dedicated Sodor workshop releasing steam engines, rolling stock, and unique Trainz reskins."
    },
    {
      name: "Sudrian Railways (NorthWestern)",
      url: "https://sudrianrailways.wixsite.com/sudrian-railways-1",
      domain: "sudrianrailways.wixsite.com",
      icon: "🚂",
      tag: "RWS & TVS Models",
      desc: "Authentic Railway Series and TV series rolling stock, character models, and route content."
    },
    {
      name: "The Branchline Crew",
      url: "https://bigboyproducions12.wixsite.com/the-branchline-crew",
      domain: "bigboyproducions12.wixsite.com",
      icon: "🌾",
      tag: "Fan Productions & Models",
      desc: "Creator group focused on Sodor branch lines, engines, wagons, and video productions."
    },
    {
      name: "CHXNCE's Hopper Wagon",
      url: "https://chxnce100trainz.wixsite.com/chxnceshopperwagon",
      domain: "chxnce100trainz.wixsite.com",
      icon: "🚛",
      tag: "Rolling Stock & Reskins",
      desc: "High-detail hopper wagons, troublesome trucks, goods stock, and custom reskins."
    },
    {
      name: "Clay Truck Works",
      url: "https://trainkid916.wixsite.com/claytruckworks",
      domain: "trainkid916.wixsite.com",
      icon: "🧱",
      tag: "China Clay & Engines",
      desc: "Standard gauge engines, quarry clay trucks, and scenic assets for Trainz."
    },
    {
      name: "The Big Station (TBS)",
      url: "https://bigstationtbs.wixsite.com/the-big-station",
      domain: "bigstationtbs.wixsite.com",
      icon: "🏛️",
      tag: "Stations & Scenery",
      desc: "Classic TVS/RWS models, terminus stations, locomotives, and landmark scenic assets."
    },
    {
      name: "Westernroutes",
      url: "https://westernroute.wixsite.com/westernroutes",
      domain: "westernroute.wixsite.com",
      icon: "🗺️",
      tag: "Routes & Layouts",
      desc: "Expansive, beautifully crafted Trainz routes and layouts inspired by the Island of Sodor."
    },
    {
      name: "Arlesburgh Bridge Depot",
      url: "https://arlesburghbridgedepo.wixsite.com/arlesburghbridgedepo",
      domain: "arlesburghbridgedepo.wixsite.com",
      icon: "⚓",
      tag: "Harbor & Coastal Assets",
      desc: "Detailed harbor, dock, coastal Sodor assets, bridges, and coastal rolling stock."
    },
    {
      name: "New Weyland Works",
      url: "https://new-weymouth-workshops.jimdofree.com/",
      domain: "new-weymouth-workshops.jimdofree.com",
      icon: "🏭",
      tag: "Workshops",
      desc: "Community Trainz workshop with locomotive releases, reskins, and railway accessories."
    },
    {
      name: "Mainland Studios",
      url: "https://mainlandstudios.wixsite.com/mysite",
      domain: "mainlandstudios.wixsite.com",
      icon: "🎬",
      tag: "Series & 3D Assets",
      desc: "Outstanding Trainz series production team, custom 3D models, and community resources."
    },
    {
      name: "Ravenshire Works",
      url: "https://thetardisexpress.wixsite.com/ravenshireworks",
      domain: "thetardisexpress.wixsite.com",
      icon: "🦅",
      tag: "Custom Models",
      desc: "Creative custom rolling stock, vintage steam locomotives, and distinctive diesels."
    },
    {
      name: "Sudrian Industries",
      url: "https://sudrianindustries.wixsite.com/sudrianindustries",
      domain: "sudrianindustries.wixsite.com",
      icon: "🏗️",
      tag: "Industrial Stock",
      desc: "Industrial shunter locomotives, heavy rolling stock, cranes, and quarry scenery."
    },
    {
      name: "Harwick Enterprises",
      url: "https://harwickenterprises3.wixsite.com/harwick-enterprises",
      domain: "harwickenterprises3.wixsite.com",
      icon: "🌊",
      tag: "Branchlines & Models",
      desc: "High quality rolling stock, scenery props, and authentic Sodor community models."
    },
    {
      name: "Vicarstown Transport",
      url: "https://vicarstowntranspor.wixsite.com/vicarstown-transport",
      domain: "vicarstowntranspor.wixsite.com",
      icon: "🚌",
      tag: "Vehicles & Roads",
      desc: "Vintage road vehicles, classic buses, traction engines, and scenic town transport."
    },
    {
      name: "Surly's Garage",
      url: "https://ihavenotalent62.wixsite.com/surlysgarage",
      domain: "ihavenotalent62.wixsite.com",
      icon: "🔧",
      tag: "Garage & Scenery",
      desc: "Unique custom 3D models, roadside clutter, and creative character additions."
    },
    {
      name: "Sudrian Boilersmiths (Wix Archive)",
      url: "https://sodorboilersmiths.wixsite.com/sudrianboilersmiths",
      domain: "sodorboilersmiths.wixsite.com",
      icon: "📦",
      tag: "Legacy Archive",
      desc: "Classic releases and archive of locomotive content from the Sudrian Boilersmiths creators."
    }
  ];

  // 2. Render Community Sites
  const sitesContainer = document.getElementById("community-sites-container");
  const siteSearchInput = document.getElementById("site-search-input");
  const siteCountIndicator = document.getElementById("site-count-indicator");

  function renderSites(query = "") {
    if (!sitesContainer) return;
    const q = query.toLowerCase().trim();
    const filtered = COMMUNITY_SITES.filter(s => 
      s.name.toLowerCase().includes(q) || 
      s.desc.toLowerCase().includes(q) ||
      s.domain.toLowerCase().includes(q) ||
      s.tag.toLowerCase().includes(q)
    );

    if (siteCountIndicator) {
      siteCountIndicator.textContent = `${filtered.length} of ${COMMUNITY_SITES.length} community sites`;
    }

    if (filtered.length === 0) {
      sitesContainer.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 32px; color: var(--text-muted);">
          <p>No community sites matching "<strong>${escapeHtml(query)}</strong>"</p>
        </div>
      `;
      return;
    }

    sitesContainer.innerHTML = filtered.map(site => `
      <a href="${site.url}" target="_blank" rel="noopener noreferrer" class="site-link-card">
        <div class="site-card-header">
          <div class="site-logo-icon">${site.icon}</div>
          <div>
            <div class="site-card-title">${escapeHtml(site.name)}</div>
            <div class="site-card-domain">${escapeHtml(site.domain)}</div>
          </div>
        </div>
        <div class="site-card-desc">${escapeHtml(site.desc)}</div>
        <div class="site-card-action">
          <span>Visit Workshop</span>
          <span>↗</span>
        </div>
      </a>
    `).join("");
  }

  if (siteSearchInput) {
    siteSearchInput.addEventListener("input", (e) => {
      renderSites(e.target.value);
    });
  }

  // Initial render
  renderSites();

  // 3. YouTube Episodes & Playlist Setup
  // Configurable for when the playlist or video is published
  const YOUTUBE_CONFIG = {
    channelUrl: "https://www.youtube.com/@brawllaunchchannel",
    playlistId: "", // Put playlist ID here once created (e.g. "PLxxxxxxx")
    upcomingEpisodes: [
      {
        number: "Episode 1",
        title: "A New Dawn on the Island",
        status: "In Production",
        synopsis: "The engines of Sodor begin work on a new branchline contract. Filmed in Trainz Railroad Simulator 2022 with custom sound design.",
        badgeColor: "var(--accent-gold)"
      },
      {
        number: "Episode 2",
        title: "The Coastal Run",
        status: "Planned",
        synopsis: "Heavy storms hit the coastal line past Brendam and Arlesburgh. The mainline engines face unexpected delays.",
        badgeColor: "var(--text-dim)"
      }
    ]
  };

  const episodesContainer = document.getElementById("episodes-container");
  if (episodesContainer) {
    episodesContainer.innerHTML = YOUTUBE_CONFIG.upcomingEpisodes.map(ep => `
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <span class="card-tag">${escapeHtml(ep.number)}</span>
          <span style="font-size: 0.75rem; font-weight: 700; color: ${ep.badgeColor}; background: rgba(255,255,255,0.05); padding: 2px 8px; border-radius: 4px;">
            ${escapeHtml(ep.status)}
          </span>
        </div>
        <h3 class="card-title">${escapeHtml(ep.title)}</h3>
        <p class="card-body">${escapeHtml(ep.synopsis)}</p>
        <div class="card-footer">
          <a href="${YOUTUBE_CONFIG.channelUrl}" target="_blank" rel="noopener noreferrer" class="btn-secondary" style="font-size: 0.85rem; padding: 8px 14px;">
            🔔 Channel Updates
          </a>
        </div>
      </div>
    `).join("");
  }

  function escapeHtml(s) {
    if (!s) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
