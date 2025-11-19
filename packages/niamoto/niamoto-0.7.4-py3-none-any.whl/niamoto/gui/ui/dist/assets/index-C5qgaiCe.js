import{r as j,j as e,C as t,e as n,f as r,k as o,a9 as f,aa as g,g as a,V as N,T as v,b,c,d as l,H as w,P as y,D as d,a8 as S,ab as C,$ as q}from"./index-DxSNfwTo.js";import{B as I}from"./book-open-CADtyscg.js";import{C as A}from"./code-XwOALPA4.js";import{R as m}from"./rocket-qCtokFz8.js";import{F as D}from"./file-code-JSNlsDoc.js";const L=[{name:"Configuration",path:"/api/config",icon:e.jsx(w,{className:"w-5 h-5"}),description:"Gestion des fichiers de configuration YAML (import.yml, transform.yml, export.yml)",endpoints:6,examples:["Lecture/écriture configs","Validation","Backups et restauration"]},{name:"Plugins",path:"/api/plugins",icon:e.jsx(y,{className:"w-5 h-5"}),description:"Découverte et introspection des 60+ plugins enregistrés",endpoints:6,examples:["Liste par type/catégorie","Schémas de configuration","Vérification compatibilité"]},{name:"Data Explorer",path:"/api/data",icon:e.jsx(d,{className:"w-5 h-5"}),description:"Exploration et requêtage des données de la base SQLite",endpoints:4,examples:["Requêtes SQL personnalisées","Inspection colonnes","Prévisualisation enrichissements"]},{name:"Entities",path:"/api/entities",icon:e.jsx(S,{className:"w-5 h-5"}),description:"Accès aux entités (taxons, parcelles, zones) avec leurs widgets et relations",endpoints:4,examples:["Liste entités par groupe","Détails avec widgets","Relations hiérarchiques"]},{name:"Transform",path:"/api/transform",icon:e.jsx(m,{className:"w-5 h-5"}),description:"Exécution des transformations de données avec gestion de jobs asynchrones",endpoints:6,examples:["Lancement transformations","Suivi progression","Métriques et résultats"]},{name:"Imports",path:"/api/imports",icon:e.jsx(C,{className:"w-5 h-5"}),description:"Import de données depuis CSV, Excel, JSON, GeoJSON, Shapefile",endpoints:9,examples:["Validation fichiers","Détection champs","Import avec mapping"]},{name:"Export",path:"/api/export",icon:e.jsx(q,{className:"w-5 h-5"}),description:"Génération de sites statiques, API JSON, Darwin Core Archives",endpoints:7,examples:["Lancement exports","Métriques de génération","Configuration cibles"]},{name:"Bootstrap",path:"/api",icon:e.jsx(m,{className:"w-5 h-5"}),description:"Analyse de fichiers et génération automatique de configurations",endpoints:5,examples:["Analyse structure fichiers","Génération configs","Diagnostic projet"]},{name:"Database",path:"/api/database",icon:e.jsx(d,{className:"w-5 h-5"}),description:"Introspection du schéma de base de données et statistiques",endpoints:4,examples:["Schéma complet","Aperçu tables","Statistiques"]},{name:"Files",path:"/api/files",icon:e.jsx(D,{className:"w-5 h-5"}),description:"Navigation système de fichiers, analyse et accès aux exports",endpoints:7,examples:["Parcours répertoires","Analyse fichiers CSV/JSON","Lecture exports"]}],p={curl:`# Récupérer un taxon spécifique
curl http://localhost:8080/api/entities/entity/taxon/1

# Lancer une transformation
curl -X POST http://localhost:8080/api/transform/execute \\
  -H "Content-Type: application/json" \\
  -d '{"config_path": "config/transform.yml"}'

# Lister les exports générés
curl http://localhost:8080/api/files/exports/list`,python:`import requests

# Récupérer un taxon avec ses widgets
response = requests.get(
    "http://localhost:8080/api/entities/entity/taxon/1"
)
taxon = response.json()

# Exécuter un export
response = requests.post(
    "http://localhost:8080/api/export/execute",
    json={"config_path": "config/export.yml"}
)
job_id = response.json()["job_id"]

# Suivre la progression
status = requests.get(
    f"http://localhost:8080/api/export/status/{job_id}"
).json()`,javascript:`// Récupérer un taxon avec fetch
const taxon = await fetch(
  'http://localhost:8080/api/entities/entity/taxon/1'
).then(r => r.json())

// Lancer une transformation
const job = await fetch(
  'http://localhost:8080/api/transform/execute',
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      config_path: 'config/transform.yml'
    })
  }
).then(r => r.json())

// Suivre la progression
const status = await fetch(
  \`http://localhost:8080/api/transform/status/\${job.job_id}\`
).then(r => r.json())`};function k(){const[i,x]=j.useState(!0);return e.jsxs("div",{className:"h-full w-full flex flex-col overflow-auto",children:[e.jsxs("div",{className:"p-6 border-b",children:[e.jsx("h1",{className:"text-2xl font-bold",children:"API Documentation"}),e.jsx("p",{className:"text-sm text-muted-foreground mt-1",children:"API REST complète pour automatisation et intégration externe"})]}),e.jsxs("div",{className:"p-6 space-y-6",children:[e.jsxs(t,{children:[e.jsx(n,{className:"cursor-pointer",onClick:()=>x(!i),children:e.jsxs("div",{className:"flex items-center justify-between",children:[e.jsxs("div",{children:[e.jsxs(r,{className:"flex items-center gap-2",children:[e.jsx(I,{className:"w-5 h-5"}),"Vue d'ensemble"]}),e.jsx(o,{children:"57 endpoints répartis en 10 modules pour contrôler Niamoto"})]}),i?e.jsx(f,{className:"w-5 h-5"}):e.jsx(g,{className:"w-5 h-5"})]})}),i&&e.jsx(a,{className:"space-y-4",children:e.jsx("div",{className:"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4",children:L.map(s=>e.jsx(t,{children:e.jsxs(a,{className:"pt-4 space-y-2",children:[e.jsxs("div",{className:"flex items-center justify-between",children:[e.jsxs("div",{className:"flex items-center gap-2",children:[s.icon,e.jsx("h3",{className:"font-semibold text-sm",children:s.name})]}),e.jsxs(N,{variant:"secondary",children:[s.endpoints," endpoints"]})]}),e.jsx("p",{className:"text-xs text-muted-foreground",children:s.description}),e.jsx("div",{className:"pt-2 space-y-1",children:s.examples.map((h,u)=>e.jsxs("div",{className:"text-xs flex items-center gap-2",children:[e.jsx("div",{className:"w-1 h-1 rounded-full bg-primary"}),e.jsx("span",{className:"text-muted-foreground",children:h})]},u))}),e.jsx("code",{className:"text-xs bg-muted px-2 py-1 rounded block mt-2",children:s.path})]})},s.name))})})]}),e.jsxs(t,{children:[e.jsxs(n,{children:[e.jsxs(r,{className:"flex items-center gap-2",children:[e.jsx(A,{className:"w-5 h-5"}),"Exemples d'utilisation"]}),e.jsx(o,{children:"Intégrez Niamoto dans vos applications et scripts"})]}),e.jsx(a,{children:e.jsxs(v,{defaultValue:"curl",className:"w-full",children:[e.jsxs(b,{className:"grid w-full grid-cols-3",children:[e.jsx(c,{value:"curl",children:"cURL"}),e.jsx(c,{value:"python",children:"Python"}),e.jsx(c,{value:"javascript",children:"JavaScript"})]}),e.jsx(l,{value:"curl",className:"mt-4",children:e.jsx("pre",{className:"bg-muted p-4 rounded-lg text-xs overflow-x-auto",children:e.jsx("code",{children:p.curl})})}),e.jsx(l,{value:"python",className:"mt-4",children:e.jsx("pre",{className:"bg-muted p-4 rounded-lg text-xs overflow-x-auto",children:e.jsx("code",{children:p.python})})}),e.jsx(l,{value:"javascript",className:"mt-4",children:e.jsx("pre",{className:"bg-muted p-4 rounded-lg text-xs overflow-x-auto",children:e.jsx("code",{children:p.javascript})})})]})})]}),e.jsxs(t,{children:[e.jsxs(n,{children:[e.jsx(r,{children:"Cas d'usage"}),e.jsx(o,{children:"Exemples d'intégration avec l'API Niamoto"})]}),e.jsx(a,{children:e.jsxs("div",{className:"grid grid-cols-1 md:grid-cols-2 gap-4",children:[e.jsxs("div",{className:"space-y-2",children:[e.jsx("h4",{className:"font-medium text-sm",children:"Automatisation"}),e.jsx("p",{className:"text-xs text-muted-foreground",children:"Scripts d'import/export réguliers, déclenchement de transformations, génération de sites"})]}),e.jsxs("div",{className:"space-y-2",children:[e.jsx("h4",{className:"font-medium text-sm",children:"Applications tierces"}),e.jsx("p",{className:"text-xs text-muted-foreground",children:"Sites web personnalisés, applications mobiles, tableaux de bord utilisant les données Niamoto"})]}),e.jsxs("div",{className:"space-y-2",children:[e.jsx("h4",{className:"font-medium text-sm",children:"Intégration SIG"}),e.jsx("p",{className:"text-xs text-muted-foreground",children:"Connexion avec QGIS, ArcGIS via requêtes API pour récupérer données géographiques"})]}),e.jsxs("div",{className:"space-y-2",children:[e.jsx("h4",{className:"font-medium text-sm",children:"Workflows scientifiques"}),e.jsx("p",{className:"text-xs text-muted-foreground",children:"Intégration dans pipelines R/Python pour analyses statistiques et génération de rapports"})]})]})})]})]}),e.jsxs("div",{className:"flex-1 border-t",children:[e.jsxs("div",{className:"p-4 bg-muted/50",children:[e.jsx("h3",{className:"text-sm font-semibold mb-2",children:"Documentation complète intégrée"}),e.jsx("p",{className:"text-xs text-muted-foreground mb-4",children:"Interface Swagger interactive avec tous les schémas, paramètres et possibilités de test"})]}),e.jsx("iframe",{src:"/api/docs",className:"w-full h-[600px] border-0",title:"API Documentation",sandbox:"allow-scripts allow-same-origin allow-forms allow-popups"})]})]})}export{k as ApiDocs};
