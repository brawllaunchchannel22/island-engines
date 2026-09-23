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
      tag: "Premier Workshop",
      desc: "Iconic classic Sodor locomotives, rolling stock, and scenic models for Trainz."
    },
    {
      name: "Toolshed Trainz (MC Bunn)",
      url: "https://toolshedtrainz.wixsite.com/mcbunncafe/sites-1",
      domain: "toolshedtrainz.wixsite.com",
      icon: "🛖",
      tag: "Routes & Hub",
      desc: "Extensive directory of Sodor routes, classic locomotives, and community links."
    },
    {
      name: "Mid Sodor Model Works 3D",
      url: "https://midsodormodelworks.wixsite.com/midsodormodelworks3d",
      domain: "midsodormodelworks.wixsite.com",
      icon: "🏔️",
      tag: "Narrow & Standard Gauge",
      desc: "Detailed 3D locomotives, vintage narrow gauge engines, and rolling stock."
    },
    {
      name: "The Old Guard's Van 3D",
      url: "https://theoldguardsvan3d.jimdofree.com/",
      domain: "theoldguardsvan3d.jimdofree.com",
      icon: "🏮",
      tag: "Rolling Stock & Figures",
      desc: "Classic brake vans, workmen figures, and authentic heritage rolling stock."
    },
    {
      name: "Crovan's Gate Works",
      url: "https://crovansgateworks.wixsite.com/crovansgateworks",
      domain: "crovansgateworks.wixsite.com",
      icon: "⚙️",
      tag: "Locomotives & Reskins",
      desc: "Dedicated Sodor workshop releasing steam engines and unique Trainz reskins."
    },
    {
      name: "Sudrian Railways (NorthWestern)",
      url: "https://sudrianrailways.wixsite.com/sudrian-railways-1",
      domain: "sudrianrailways.wixsite.com",
      icon: "🚂",
      tag: "RWS & TVS Models",
      desc: "Authentic Railway Series and TV series rolling stock and route creations."
    },
    {
      name: "The Branchline Crew",
      url: "https://bigboyproducions12.wixsite.com/the-branchline-crew",
      domain: "bigboyproducions12.wixsite.com",
      icon: "🌾",
      tag: "Productions & Models",
      desc: "Creator team focused on Sodor branch lines, wagons, and video series."
    },
    {
      name: "CHXNCE's Hopper Wagon",
      url: "https://chxnce100trainz.wixsite.com/chxnceshopperwagon",
      domain: "chxnce100trainz.wixsite.com",
      icon: "🚛",
      tag: "Wagons & Goods Stock",
      desc: "High-detail hopper wagons, troublesome trucks, and custom liveries."
    },
    {
      name: "Clay Truck Works",
      url: "https://trainkid916.wixsite.com/claytruckworks",
      domain: "trainkid916.wixsite.com",
      icon: "🧱",
      tag: "China Clay & Engines",
      desc: "Standard gauge engines, quarry trucks, and atmospheric scenic assets."
    },
    {
      name: "The Big Station (TBS)",
      url: "https://bigstationtbs.wixsite.com/the-big-station",
      domain: "bigstationtbs.wixsite.com",
      icon: "🏛️",
      tag: "Terminus & Scenery",
      desc: "Classic terminus stations, landmarks, locomotives, and scenic packages."
    },
    {
      name: "Westernroutes",
      url: "https://westernroute.wixsite.com/westernroutes",
      domain: "westernroute.wixsite.com",
      icon: "🗺️",
      tag: "Routes & Layouts",
      desc: "Expansive, beautifully crafted Trainz routes inspired by the Island of Sodor."
    },
    {
      name: "Arlesburgh Bridge Depot",
      url: "https://arlesburghbridgedepo.wixsite.com/arlesburghbridgedepo",
      domain: "arlesburghbridgedepo.wixsite.com",
      icon: "⚓",
      tag: "Harbor & Coastal Assets",
      desc: "Detailed harbor, dock, coastal Sodor assets, bridges, and rolling stock."
    },
    {
      name: "New Weyland Works",
      url: "https://new-weymouth-workshops.jimdofree.com/",
      domain: "new-weymouth-workshops.jimdofree.com",
      icon: "🏭",
      tag: "Community Workshop",
      desc: "Locomotive releases, heritage rolling stock, and railway accessories."
    },
    {
      name: "Mainland Studios",
      url: "https://mainlandstudios.wixsite.com/mysite",
      domain: "mainlandstudios.wixsite.com",
      icon: "🎬",
      tag: "Series & 3D Assets",
      desc: "Outstanding Trainz series production team, models, and community resources."
    },
    {
      name: "Ravenshire Works",
      url: "https://thetardisexpress.wixsite.com/ravenshireworks",
      domain: "thetardisexpress.wixsite.com",
      icon: "🦅",
      tag: "Custom Models",
      desc: "Creative custom rolling stock, vintage steam locomotives, and diesels."
    },
    {
      name: "Sudrian Industries",
      url: "https://sudrianindustries.wixsite.com/sudrianindustries",
      domain: "sudrianindustries.wixsite.com",
      icon: "🏗️",
      tag: "Industrial Stock",
      desc: "Industrial shunters, heavy rolling stock, cranes, and quarry scenery."
    },
    {
      name: "Harwick Enterprises",
      url: "https://harwickenterprises3.wixsite.com/harwick-enterprises",
      domain: "harwickenterprises3.wixsite.com",
      icon: "🌊",
      tag: "Branchlines & Models",
      desc: "High quality rolling stock, scenery props, and authentic community models."
    },
    {
      name: "Vicarstown Transport",
      url: "https://vicarstowntranspor.wixsite.com/vicarstown-transport",
      domain: "vicarstowntranspor.wixsite.com",
      icon: "🚌",
      tag: "Vehicles & Roads",
      desc: "Vintage road vehicles, classic buses, traction engines, and scenic transport."
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
      desc: "Archive of classic locomotive and rolling stock releases from the Boilersmiths."
    }
  ];

  // 2. Render Community Workshops
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
      siteCountIndicator.textContent = `${filtered.length} workshops cataloged`;
    }

    if (filtered.length === 0) {
      sitesContainer.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 48px; color: var(--text-muted);">
          <p style="font-size: 1.05rem;">No workshops matching "<strong>${escapeHtml(query)}</strong>"</p>
        </div>
      `;
      return;
    }

    sitesContainer.innerHTML = filtered.map(site => `
      <a href="${site.url}" target="_blank" rel="noopener noreferrer" class="directory-card">
        <div class="dir-top-row">
          <div class="dir-icon-avatar">${site.icon}</div>
          <div>
            <div class="dir-title">${escapeHtml(site.name)}</div>
            <div class="dir-tag">${escapeHtml(site.tag)}</div>
          </div>
        </div>
        <div class="dir-desc">${escapeHtml(site.desc)}</div>
        <div class="dir-footer-action">
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

  // 3. Image Lightbox Modal for Production Stills
  const lightbox = document.getElementById("image-lightbox");
  const lightboxImg = document.getElementById("lightbox-img");
  const lightboxCaption = document.getElementById("lightbox-caption");
  const lightboxCloseBtn = document.getElementById("lightbox-close-btn");

  if (lightbox && lightboxImg && lightboxCaption) {
    document.querySelectorAll(".lightbox-trigger").forEach(trigger => {
      trigger.addEventListener("click", () => {
        const fullSrc = trigger.getAttribute("data-full");
        const caption = trigger.getAttribute("data-caption") || "";
        if (fullSrc) {
          lightboxImg.src = fullSrc;
          lightboxCaption.textContent = caption;
          lightbox.classList.add("open");
          lightbox.setAttribute("aria-hidden", "false");
          document.body.style.overflow = "hidden"; // Prevent page background scroll
        }
      });
    });

    function closeLightbox() {
      lightbox.classList.remove("open");
      lightbox.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
      setTimeout(() => {
        lightboxImg.src = "";
        lightboxCaption.textContent = "";
      }, 200);
    }

    if (lightboxCloseBtn) {
      lightboxCloseBtn.addEventListener("click", closeLightbox);
    }

    lightbox.addEventListener("click", (e) => {
      // Close if clicking outside the image/dialog box
      if (e.target === lightbox || e.target.classList.contains("lightbox-media-box")) {
        closeLightbox();
      }
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && lightbox.classList.contains("open")) {
        closeLightbox();
      }
    });
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

