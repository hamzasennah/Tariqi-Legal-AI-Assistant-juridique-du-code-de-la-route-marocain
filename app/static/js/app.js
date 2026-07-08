const askForm = document.querySelector("#ask-form");
const answerState = document.querySelector("#answer-state");
const answerCard = document.querySelector("#answer-card");
const sourceList = document.querySelector("#source-list");
const calcForm = document.querySelector("#calc-form");
const calcResult = document.querySelector("#calc-result");
const procedureForm = document.querySelector("#procedure-form");
const procedureResult = document.querySelector("#procedure-result");
const sourcesTable = document.querySelector("#sources-table");

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderMarkdown(markdown) {
  const lines = markdown.split("\n");
  let html = "";
  let inList = false;

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      if (inList) {
        html += "</ul>";
        inList = false;
      }
      continue;
    }
    if (line.startsWith("### ")) {
      if (inList) {
        html += "</ul>";
        inList = false;
      }
      html += `<h3>${escapeHtml(line.slice(4))}</h3>`;
    } else if (line.startsWith("- ")) {
      if (!inList) {
        html += "<ul>";
        inList = true;
      }
      html += `<li>${escapeHtml(line.slice(2))}</li>`;
    } else {
      if (inList) {
        html += "</ul>";
        inList = false;
      }
      html += `<p>${escapeHtml(line)}</p>`;
    }
  }

  if (inList) {
    html += "</ul>";
  }
  return html;
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "Erreur serveur");
  }
  return response.json();
}

function setLoading(element, message) {
  element.classList.remove("error");
  element.textContent = message;
}

function renderSources(sources) {
  if (!sources.length) {
    sourceList.innerHTML = '<p class="muted">Aucune source pertinente trouvée.</p>';
    return;
  }

  sourceList.innerHTML = sources
    .map(
      (source) => `
        <div class="source-item">
          <strong>${escapeHtml(source.authority)} - ${escapeHtml(source.title)}</strong>
          <div class="source-meta">
            ${escapeHtml(source.section)}<br />
            ${escapeHtml(source.document)} · ${escapeHtml(source.date)}
          </div>
          <span class="badge">Confiance ${escapeHtml(source.trust_level)} · score ${source.score}</span>
        </div>
      `
    )
    .join("");
}

document.querySelectorAll("[data-example]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelector("#question").value = button.dataset.example;
  });
});

askForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = document.querySelector("#question").value.trim();
  if (!question) return;

  answerCard.classList.add("hidden");
  setLoading(answerState, "Analyse des sources officielles...");

  try {
    const data = await postJson("/api/ask", { question, top_k: 5 });
    answerState.textContent = "";
    answerCard.innerHTML = renderMarkdown(data.answer_markdown);
    answerCard.classList.remove("hidden");
    renderSources(data.sources);
  } catch (error) {
    answerState.textContent = error.message;
    answerState.classList.add("error");
  }
});

calcForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const infraction = document.querySelector("#infraction").value.trim();
  const delay = document.querySelector("#delay").value;
  setLoading(calcResult, "Calcul en cours...");

  try {
    const data = await postJson("/api/calculate", { infraction, delay });
    if (!data.matched) {
      calcResult.innerHTML = `<p>${escapeHtml(data.message)}</p>`;
      return;
    }
    calcResult.innerHTML = `
      <p><strong>${escapeHtml(data.infraction.nom_infraction)}</strong></p>
      <p>${escapeHtml(data.message)}</p>
      <p class="muted">Classe : ${escapeHtml(data.infraction.classe)} · Source : ${escapeHtml(data.infraction.source)}</p>
    `;
  } catch (error) {
    calcResult.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
});

procedureForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = document.querySelector("#procedure-query").value.trim();
  setLoading(procedureResult, "Recherche de la procédure...");

  try {
    const response = await fetch(`/api/procedure?q=${encodeURIComponent(query)}`);
    const data = await response.json();
    if (!data.procedure) {
      procedureResult.innerHTML = "<p>Aucune procédure correspondante trouvée.</p>";
      return;
    }
    procedureResult.innerHTML = `
      <p><strong>${escapeHtml(data.procedure.title)}</strong></p>
      <p>${escapeHtml(data.procedure.summary)}</p>
      <ol>${data.procedure.steps.map((step) => `<li>${escapeHtml(step)}</li>`).join("")}</ol>
      <p class="muted">${escapeHtml(data.procedure.warning)}</p>
    `;
  } catch (error) {
    procedureResult.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
});

document.querySelector("#load-sources").addEventListener("click", async () => {
  sourcesTable.textContent = "Chargement...";
  const response = await fetch("/api/sources");
  const data = await response.json();
  sourcesTable.classList.remove("muted");
  sourcesTable.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Niveau</th>
          <th>Autorité</th>
          <th>Titre</th>
          <th>Thème</th>
          <th>URL</th>
        </tr>
      </thead>
      <tbody>
        ${data.items
          .map(
            (source) => `
              <tr>
                <td>${escapeHtml(source.trust_level)}</td>
                <td>${escapeHtml(source.authority)}</td>
                <td>${escapeHtml(source.title)}</td>
                <td>${escapeHtml(source.theme)}</td>
                <td><a href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">Ouvrir</a></td>
              </tr>
            `
          )
          .join("")}
      </tbody>
    </table>
  `;
});
