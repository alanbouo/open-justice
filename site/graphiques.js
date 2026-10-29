// Aides d'affichage, sans dépendance. Les données viennent de agregats/*.json.
const DOMAINES = {
  etrangers: "Droit des étrangers", sans_domaine: "Sans domaine identifié", fonction_publique: "Fonction publique",
  securite_sociale_aides: "Sécurité sociale et aides", logement: "Logement", urbanisme: "Urbanisme",
  fiscal: "Fiscal", securite_police: "Sécurité et police", responsabilite_indemnisation: "Responsabilité, indemnisation",
  sante: "Santé", collectivites_domaine_public: "Collectivités, domaine public", education: "Éducation",
  travail_emploi: "Travail, emploi", civil: "Civil", regulation_actes_reglementaires: "Actes réglementaires",
  environnement: "Environnement", commande_publique: "Commande publique", electoral: "Électoral",
  commerce_assurance: "Commerce, assurance",
};
const ORDRES = { TA: "Tribunaux administratifs", CAA: "Cours administratives d'appel", CE: "Conseil d'État" };
const SAISISSANTS = { physique: "Particulier", morale: "Personne morale", etat: "État", tous: "Toutes natures", inconnue: "Nature inconnue" };
const PROCEDURES = { fond: "Au fond", refere_liberte: "Référé-liberté", refere_suspension: "Référé-suspension",
  refere_conservatoire: "Référé conservatoire", refere_provision: "Référé-provision", refere_instruction: "Référé-instruction",
  refere_modification: "Référé-modification", refere_autre: "Autre référé", execution: "Exécution" };
const ISSUES = { gagne: "Obtient gain de cause", partiel: "Gain partiel", perd: "Perd", neutre: "Sans examen du fond" };
const SORTS = { confirme: "Jugement confirmé", infirme_partiellement: "Réformé en partie", infirme: "Infirmé ou annulé" };

const nf = new Intl.NumberFormat("fr-FR");
const pct = (x) => x.toFixed(1).replace(".", ",") + " %";

async function charger(nom) {
  const r = await fetch("agregats/" + nom);
  if (!r.ok) throw new Error(nom + " : " + r.status);
  return r.json();
}

function el(tag, attrs = {}, ...enfants) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") e.className = v; else e.setAttribute(k, v);
  }
  e.append(...enfants);
  return e;
}

function legende(cles, libelles) {
  return el("div", { class: "legende" }, ...Object.keys(cles).map((k) =>
    el("span", {}, el("i", { class: k }), libelles[k])));
}

// Une ligne par groupe : étiquette, barre empilée des parts, effectif.
function barres(conteneur, rows, etiquette, cles, libelles) {
  conteneur.replaceChildren(legende(cles, libelles));
  for (const r of rows) {
    const barre = el("div", { class: "barre", role: "img",
      "aria-label": Object.keys(cles).map((k) => `${libelles[k]} ${pct(r[k])}`).join(", ") });
    for (const k of Object.keys(cles)) {
      const s = el("span", { class: k, title: `${libelles[k]} : ${pct(r[k])}` });
      s.style.width = r[k] + "%";
      barre.append(s);
    }
    conteneur.append(el("div", { class: "ligne" }, el("div", {}, etiquette(r)), barre,
      el("div", { class: "n" }, nf.format(r.n) + " déc.")));
  }
}

function filtres(conteneur, options, courant, quand) {
  conteneur.replaceChildren(...Object.entries(options).map(([cle, libelle]) => {
    const b = el("button", { type: "button", "aria-pressed": String(cle === courant) }, libelle);
    b.addEventListener("click", () => {
      conteneur.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", "false"));
      b.setAttribute("aria-pressed", "true");
      quand(cle);
    });
    return b;
  }));
}

function pied(donnees) {
  const p = document.getElementById("calcul");
  if (p) p.textContent = `Calculé le ${new Date(donnees.calcule_le).toLocaleDateString("fr-FR")} sur ${donnees.base.replace(/^\d+/, (n) => nf.format(Number(n)))}. Aucun groupe de moins de ${donnees.seuil} décisions n'est affiché.`;
}

function erreur(e) {
  document.querySelector("main").prepend(el("p", { class: "reserve" },
    "Les données n'ont pas pu être chargées (" + e.message + "). Ouvrir le site via un serveur web, pas en double-cliquant sur le fichier."));
}

// En-tête et pied communs, écrits une seule fois.
// Chaque entrée du menu regroupe les pages qui lui appartiennent ; « sous » ajoute une seconde ligne de navigation.
const MENU = [
  { href: "index.html", titre: "Accueil", pages: ["index.html"] },
  { href: "comprendre.html", titre: "Comprendre",
    pages: ["comprendre.html", "organisation.html", "deux-ordres.html", "deroule-administratif.html", "deroule-civil.html", "acteurs.html", "lexique.html", "delais.html"],
    sous: [["comprendre.html", "Vue d'ensemble"], ["organisation.html", "Organisation"], ["deux-ordres.html", "Deux ordres"],
      ["deroule-administratif.html", "Affaire administrative"], ["deroule-civil.html", "Affaire civile"], ["acteurs.html", "Les acteurs"], ["lexique.html", "Lexique"], ["delais.html", "Les délais"]] },
  { href: "aller-en-justice.html", titre: "Aller en justice", pages: ["aller-en-justice.html"] },
  { href: "chiffres.html", titre: "Les chiffres",
    pages: ["chiffres.html", "durees.html", "issues.html", "appel.html", "judiciaire.html", "penal.html", "juridictions.html"],
    sous: [["chiffres.html", "Vue d'ensemble"], ["durees.html", "Durée"], ["issues.html", "Issue des recours"], ["appel.html", "Appel"],
      ["judiciaire.html", "Judiciaire", "attente"], ["penal.html", "Pénal", "attente"], ["juridictions.html", "Par juridiction", "attente"]] },
  { href: "situations.html", titre: "Par situation", pages: ["situations.html"] },
  { href: "methode.html", titre: "Méthode et sources", pages: ["methode.html"] },
];

function cadre(courante) {
  const actif = MENU.find((m) => m.pages.includes(courante));
  const nav = el("nav", { "aria-label": "Sections" }, ...MENU.map((m) => {
    const a = el("a", { href: m.href }, m.titre);
    if (m === actif) a.setAttribute("aria-current", "page");
    return a;
  }));
  document.body.prepend(el("header", {}, el("a", { class: "nom", href: "index.html" }, "Open Justice"), nav));
  if (actif?.sous) {
    document.querySelector("header").after(el("nav", { class: "sous", "aria-label": actif.titre },
      ...actif.sous.map(([h, t, etat]) => {
        const a = el("a", { href: h }, t);
        if (etat) { a.className = etat; a.title = "À venir"; }
        if (h === courante) a.setAttribute("aria-current", "page");
        return a;
      })));
  }
  document.body.append(el("footer", {},
    el("p", { id: "calcul" }),
    el("p", {}, "Initiative indépendante. Sources : base Données ouvertes du Conseil d'État et des juridictions administratives (Licence Ouverte 2.0) ; Judilibre, Cour de cassation, pour la justice judiciaire. ",
      "Ce site ne republie aucune décision : il publie des statistiques calculées sur les décisions publiées, ",
      "jamais par magistrat ni par greffier (article 33 de la loi de réforme de la justice de 2019). Code : ",
      el("a", { href: "https://github.com/alanbouo/open-justice" }, "dépôt public"), ".")));
}

// Chiffres officiels (source unique : references/conseil-etat-2025.json, avec URL et date de consultation).
async function chargerReferences(fichier = "conseil-etat-2025.json") {
  const r = await fetch("references/" + fichier);
  if (!r.ok) throw new Error("references : " + r.status);
  return r.json();
}

// {mois, jours} -> « 1 an 9 jours », comme les publie le Conseil d'État.
function dureeFr({ mois, jours }) {
  const ans = Math.floor(mois / 12), m = mois % 12;
  return [ans && `${ans} an${ans > 1 ? "s" : ""}`, m && `${m} mois`, jours && `${jours} jour${jours > 1 ? "s" : ""}`]
    .filter(Boolean).join(" ");
}
const enMois = ({ mois, jours }) => mois + jours / 30.44;
const virgule = (x, d = 1) => x.toFixed(d).replace(".", ",");

// Règle d'écriture des chiffres (CLAUDE.md) : dans le texte courant, on arrondit ; tableaux, cartes et graphiques gardent la valeur exacte.
const MOIS = 365.25 / 12;
const jours = (j) => `${nf.format(Math.round(j))} jour${Math.round(j) > 1 ? "s" : ""}`;
// Durée en jours -> durée lisible. sens = 1 : « moins de » (arrondi au-dessus) ; -1 : « plus de » (arrondi en dessous) ; 0 : le plus proche.
// En jours sous 45 jours, en mois jusqu'à deux ans, puis en années par demi-année.
function approx(j, sens = 0) {
  const r = sens > 0 ? Math.ceil : sens < 0 ? Math.floor : Math.round;
  if (j < 45) return jours(r(j));
  const m = j / MOIS;
  if (m < 24) return `${r(m)} mois`;
  const a = r(m / 6) / 2;
  return `${virgule(a, a % 1 ? 1 : 0)} ans`;
}
// Mêmes règles pour une durée donnée en mois ; un pourcentage s'arrondit à l'unité.
const approxMois = (m, sens = 0) => approx(m * MOIS, sens);
const pctRond = (x) => Math.round(x) + " %";

// Bloc final des pages « Comprendre » : sources datées, puis une ligne sur la nature de l'information.
function sources(liste, consulteLe) {
  const date = new Date(consulteLe).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
  document.querySelector("main").append(el("section", { class: "sources" },
    el("h2", {}, "Sources"),
    el("ul", {}, ...liste.map(([titre, url, note]) =>
      el("li", {}, el("a", { href: url }, titre), note ? " " + note : ""))),
    el("p", {}, `Sources consultées le ${date}. Information générale, pas un conseil juridique.`)));
}
