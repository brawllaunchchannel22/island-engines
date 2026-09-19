/**
 * Thomas Productions — Video Credits & Assets List
 * Fast, lightweight filtering & search across all assets and music tracks.
 */

document.addEventListener("DOMContentLoaded", () => {
  if (typeof CREDITS_DATA === "undefined") {
    console.error("CREDITS_DATA not loaded!");
    return;
  }

  // Combine items
  const musicList = (CREDITS_DATA.music || []).map(m => ({ ...m, type: "music" }));
  const trainzList = (CREDITS_DATA.trainz || []).map(t => ({ ...t, type: "trainz" }));
  const allItems = [...musicList, ...trainzList];

  // State
  let currentCategory = "all";
  let currentSearch = "";
  let currentAuthor = null;
  let currentLimit = 120;
  let currentFilteredItems = [];

  // DOM Elements
  const searchInput = document.getElementById("search-input");
  const clearBtn = document.getElementById("clear-search-btn");
  const resultsCount = document.getElementById("results-count");
  const cardsContainer = document.getElementById("cards-container");
  const emptyState = document.getElementById("empty-state");
  const categoryFilters = document.getElementById("category-filters");
  const activeFilterBar = document.getElementById("active-filter-bar");
  const activeAuthorName = document.getElementById("active-author-name");
  const resetAuthorBtn = document.getElementById("reset-author-filter");
  const resetSearchBtn = document.getElementById("reset-search-btn");
  const authorsContainer = document.getElementById("authors-container");
  const copyKuidsBtn = document.getElementById("copy-kuids-btn");
  const toast = document.getElementById("toast");

  // Stats in header
  const statTotal = document.getElementById("stat-total");
  const statMusic = document.getElementById("stat-music");
  const statTrainz = document.getElementById("stat-trainz");
  if (statTotal) statTotal.textContent = allItems.length.toLocaleString();
  if (statMusic) statMusic.textContent = musicList.length.toLocaleString();
  if (statTrainz) statTrainz.textContent = trainzList.length.toLocaleString();

  // Populate Authors Cloud
  renderAuthorsCloud();

  // Initial render of cards
  renderCards();

  // Event Listeners
  let debounce = null;
  searchInput.addEventListener("input", (e) => {
    const val = e.target.value.trim();
    clearBtn.style.display = val ? "block" : "none";
    clearTimeout(debounce);
    debounce = setTimeout(() => {
      currentLimit = 120;
      currentSearch = val.toLowerCase();
      renderCards();
    }, 120);
  });

  clearBtn.addEventListener("click", () => {
    searchInput.value = "";
    currentSearch = "";
    currentLimit = 120;
    clearBtn.style.display = "none";
    renderCards();
    searchInput.focus();
  });

  categoryFilters.addEventListener("click", (e) => {
    const btn = e.target.closest(".tab-btn");
    if (!btn) return;

    categoryFilters.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    currentLimit = 120;
    currentCategory = btn.dataset.category;
    renderCards();
  });

  resetAuthorBtn.addEventListener("click", () => {
    currentAuthor = null;
    currentLimit = 120;
    activeFilterBar.style.display = "none";
    renderCards();
  });

  resetSearchBtn.addEventListener("click", () => {
    searchInput.value = "";
    currentSearch = "";
    currentLimit = 120;
    clearBtn.style.display = "none";
    currentCategory = "all";
    currentAuthor = null;
    activeFilterBar.style.display = "none";

    categoryFilters.querySelectorAll(".tab-btn").forEach(b => {
      b.classList.toggle("active", b.dataset.category === "all");
    });
    renderCards();
  });

  if (copyKuidsBtn) {
    copyKuidsBtn.addEventListener("click", () => {
      const kuids = [];
      const seen = new Set();
      currentFilteredItems.forEach(item => {
        if (item.kuid && item.kuid.trim()) {
          const k = item.kuid.trim();
          if (!seen.has(k)) {
            seen.add(k);
            kuids.push(k);
          }
        }
      });

      if (kuids.length === 0) {
        showToast("No KUIDs in current view.");
        return;
      }

      const text = kuids.join("\n");
      copyText(text);
      showToast(`Copied ${kuids.length.toLocaleString()} visible KUIDs to clipboard!`);
    });
  }

  /**
   * Filter & Render
   */
  function renderCards() {
    const filtered = allItems.filter(item => {
      // 1. Author filter
      if (currentAuthor) {
        const author = item.author || item.arranger || item.composer || "";
        const curA = currentAuthor.toLowerCase();
        const itA = author.toLowerCase();
        if (curA.includes("milo the otter")) {
          if (!itA.includes("milo the otter") && !(item.source || "").toLowerCase().includes("milo the otter")) {
            return false;
          }
        } else if (itA !== curA) {
          return false;
        }
      }

      // 2. Category filter
      if (currentCategory !== "all") {
        if (currentCategory === "music" && item.type !== "music") return false;
        if (currentCategory !== "music" && item.category !== currentCategory) return false;
      }

      // 3. Search query
      if (currentSearch) {
        const title = (item.title || item.name || "").toLowerCase();
        const author = (item.author || item.composer || item.arranger || "").toLowerCase();
        const kuid = (item.kuid || "").toLowerCase();
        const tag = (item.tag || item.kind || "").toLowerCase();
        const src = (item.source || "").toLowerCase();

        return (
          title.includes(currentSearch) ||
          author.includes(currentSearch) ||
          kuid.includes(currentSearch) ||
          tag.includes(currentSearch) ||
          src.includes(currentSearch)
        );
      }

      return true;
    });

    currentFilteredItems = filtered;
    resultsCount.textContent = `Showing ${filtered.length} of ${allItems.length} items`;

    if (filtered.length === 0) {
      cardsContainer.innerHTML = "";
      emptyState.style.display = "block";
      return;
    }
    emptyState.style.display = "none";

    // Progressive rendering (first 120 items, with load more)
    const limit = currentLimit;
    const toRender = filtered.slice(0, limit);
    let cardsHtml = toRender.map(item => createCard(item)).join("");

    if (filtered.length > limit) {
      cardsHtml += `
        <div class="load-more-container" style="grid-column: 1 / -1; text-align: center; padding: 1.5rem 0;">
          <button id="load-more-btn" class="btn-simple" style="padding: 0.75rem 2rem; font-size: 0.95rem;">
            Load More (+120 items) — Showing ${limit} of ${filtered.length}
          </button>
        </div>
      `;
    }

    cardsContainer.innerHTML = cardsHtml;
    attachListeners();

    const loadMoreBtn = document.getElementById("load-more-btn");
    if (loadMoreBtn) {
      loadMoreBtn.addEventListener("click", () => {
        currentLimit += 150;
        renderCards();
      });
    }
  }

  /**
   * Create Card HTML
   */
  function createCard(item) {
    const isMusic = item.type === "music";
    const title = escapeHtml(item.title || item.name || "Untitled");
    
    // Category tag
    let catClass = "badge-scenery";
    let catLabel = "Scenery";
    if (isMusic) {
      catClass = "badge-music";
      catLabel = "🎵 Audio Track";
    } else {
      catClass = `badge-${item.category || "scenery"}`;
      catLabel = formatCat(item.category);
    }

    // Author line
    let authorHtml = "";
    if (isMusic) {
      const arranger = item.arranger ? `<strong class="milo-badge">${escapeHtml(item.arranger)}</strong>` : "";
      const composer = item.composer ? escapeHtml(item.composer) : "";
      if (arranger && arranger.includes("Milo the Otter")) {
        authorHtml = `Reorchestrated by <button class="author-btn" data-author="${escapeHtml(item.arranger)}">${arranger}</button> (Original: Mike O'Donnell & Junior Campbell)`;
      } else if (arranger) {
        authorHtml = `Arranged by <button class="author-btn" data-author="${escapeHtml(item.arranger)}">${arranger}</button>`;
      } else {
        authorHtml = `By <button class="author-btn" data-author="${escapeHtml(composer)}">${composer}</button>`;
      }
    } else {
      const creator = escapeHtml(item.author || "Community Modeller");
      authorHtml = `By: <button class="author-btn" data-author="${creator}">${creator}</button>`;
    }

    // Footer info: KUID or Source
    let footerLeft = "";
    if (item.kuid) {
      footerLeft = `<span class="kuid-code" data-copy="${escapeHtml(item.kuid)}" title="Click to copy KUID">
        <span>${escapeHtml(item.kuid)}</span>
        <span style="opacity: 0.6;">📋</span>
      </span>`;
    } else {
      footerLeft = `<span class="item-source">${escapeHtml(isMusic ? (item.tag || "Audio Track") : (catLabel || "3D Asset"))}</span>`;
    }

    const cleanSource = isMusic ? "Milo the Otter" : (item.source || "Trainz 2022");
    const footerRight = `<span class="item-source" title="${escapeHtml(cleanSource)}">${escapeHtml(cleanSource)}</span>`;

    return `
      <div class="item-card">
        <div class="item-header">
          <div class="item-title">${title}</div>
          <span class="badge-tag ${catClass}">${catLabel}</span>
        </div>
        <div class="item-author">${authorHtml}</div>
        <div class="item-footer">
          ${footerLeft}
          ${footerRight}
        </div>
      </div>
    `;
  }

  function attachListeners() {
    // KUID click to copy
    cardsContainer.querySelectorAll(".kuid-code").forEach(btn => {
      btn.addEventListener("click", () => {
        const text = btn.dataset.copy;
        if (text) copyText(text);
      });
    });

    // Author button click
    cardsContainer.querySelectorAll(".author-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const a = btn.dataset.author;
        if (a) filterByAuthor(a);
      });
    });
  }

  function filterByAuthor(name) {
    currentAuthor = name;
    currentLimit = 120;

    // Reset category filter to "all" and clear search so all creator items are shown immediately
    currentCategory = "all";
    categoryFilters.querySelectorAll(".tab-btn").forEach(b => {
      b.classList.toggle("active", b.dataset.category === "all");
    });
    searchInput.value = "";
    currentSearch = "";
    clearBtn.style.display = "none";

    activeAuthorName.textContent = name;
    activeFilterBar.style.display = "flex";
    renderCards();
    window.scrollTo({ top: document.querySelector(".controls-area").offsetTop - 20, behavior: "smooth" });
  }

  function renderAuthorsCloud() {
    if (!authorsContainer) return;
    const authors = CREDITS_DATA.authors || [];

    // Prepend Milo the Otter if not already at top
    let list = [...authors];
    const miloTracks = musicList.filter(m => (m.arranger || "").includes("Milo the Otter")).length;
    if (miloTracks > 0 && !list.some(a => a.name === "Milo the Otter")) {
      list.unshift({ name: "Milo the Otter (Reorchestrations)", count: miloTracks });
    }

    authorsContainer.innerHTML = list.map(a => `
      <button class="creator-tag" data-author="${escapeHtml(a.name)}">
        <span>${escapeHtml(a.name)}</span>
        <span class="creator-count">${a.count}</span>
      </button>
    `).join("");

    authorsContainer.querySelectorAll(".creator-tag").forEach(tag => {
      tag.addEventListener("click", () => {
        const a = tag.dataset.author;
        if (a) filterByAuthor(a);
      });
    });
  }

  function formatCat(c) {
    switch(c) {
      case "routes": return "🗺️ Route / Map";
      case "rolling_stock": return "🚂 Rolling Stock";
      case "buildings": return "🏢 Building / Shed";
      case "infrastructure": return "🛤️ Track / Road";
      case "characters": return "👥 Character";
      case "scenery": return "🌲 Scenery";
      default: return "Asset";
    }
  }

  function copyText(txt) {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(txt).then(() => showToast(`Copied ${txt}!`));
    } else {
      const el = document.createElement("textarea");
      el.value = txt;
      document.body.appendChild(el);
      el.select();
      document.execCommand("copy");
      document.body.removeChild(el);
      showToast(`Copied ${txt}!`);
    }
  }

  let toastTimer = null;
  function showToast(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toast.classList.remove("show");
    }, 2000);
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
