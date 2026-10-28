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
  if (p) p.textContent = `Calculé le ${new Date(donnees.calcule_le).toLocaleDateString("fr-FR")} sur ${donnees.base}. Aucun groupe de moins de ${donnees.seuil} décisions n'est affiché.`;
}

function erreur(e) {
  document.querySelector("main").prepend(el("p", { class: "reserve" },
    "Les données n'ont pas pu être chargées (" + e.message + "). Ouvrir le site via un serveur web, pas en double-cliquant sur le fichier."));
}

// En-tête et pied communs, écrits une seule fois.
// Chaque entrée du menu regroupe les pages qui lui appartiennent ; « sous » ajoute une seconde ligne de navigation.
const MENU = [
  { href: "index.html", titre: "Accueil", pages: ["index.html"] },
  { href: "administratif.html", titre: "Administratif", pages: ["administratif.html", "durees.html", "issues.html", "appel.html"],
    sous: [["administratif.html", "Vue d'ensemble"], ["durees.html", "Durée"], ["issues.html", "Issue des recours"], ["appel.html", "Appel"]] },
  { href: "judiciaire.html", titre: "Judiciaire", pages: ["judiciaire.html"] },
  { href: "penal.html", titre: "Pénal", pages: ["penal.html"] },
  { href: "domaines.html", titre: "Domaines", pages: ["domaines.html"] },
  { href: "juridictions.html", titre: "Juridictions", pages: ["juridictions.html"] },
  { href: "methode.html", titre: "Méthode", pages: ["methode.html"] },
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
      ...actif.sous.map(([h, t]) => {
        const a = el("a", { href: h }, t);
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
